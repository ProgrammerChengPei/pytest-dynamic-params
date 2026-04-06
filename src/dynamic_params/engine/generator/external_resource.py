"""
支持外部资源的生成器同步方案

本模块提供了在 xdist 环境中安全使用外部资源（数据库、网络、文件）的生成器。

核心特性：
1. 预加载数据（不序列化连接）
2. Worker 独立连接池
3. 混合策略支持
4. 错误处理和回退
"""

import json
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ...types import GeneratorFunc
from .base import GeneratorBase
from .registry import registry as global_registry

# ============================================================================
# 外部资源生成器基类
# ============================================================================

class ExternalResourceGenerator(GeneratorBase):
    """支持外部资源的生成器基类"""
    
    def __init__(self, func: GeneratorFunc, scope: str = "function",
                 cache: bool = False, lazy: bool = False,
                 preload: bool = True, resource_type: str = None):
        """
        Args:
            func: 生成器函数
            scope: 作用域
            cache: 是否缓存
            lazy: 是否懒加载
            preload: 是否预加载（关键参数）
            resource_type: 资源类型（'database', 'network', 'file'）
        """
        super().__init__(func, scope, cache, lazy)
        self.preload = preload
        self.resource_type = resource_type
        self._preloaded_data = None
        self._resource_connection = None
    
    def preload_data(self, context: Dict[str, Any] = None) -> List[Any]:
        """
        预加载外部资源数据
        
        子类需要实现这个方法
        
        Returns:
            加载的数据列表
        """
        raise NotImplementedError
    
    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """执行生成器"""
        if self.preload and self._preloaded_data is not None:
            # 使用预加载的数据
            return self._preloaded_data
        else:
            # 直接执行（懒加载模式）
            result = list(super().execute(*args, **kwargs))
            if self.cache:
                self._preloaded_data = result
            return result
    
    def set_preloaded_data(self, data: List[Any]) -> None:
        """设置预加载的数据"""
        self._preloaded_data = data
    
    def get_preloaded_data(self) -> Optional[List[Any]]:
        """获取预加载的数据"""
        return self._preloaded_data
    
    def __getstate__(self):
        """序列化时排除连接对象"""
        state = self.__dict__.copy()
        # 移除不可序列化的属性
        state['_resource_connection'] = None
        return state


# ============================================================================
# 资源预加载管理器
# ============================================================================

class ResourcePreloader:
    """资源预加载管理器"""
    
    def __init__(self):
        self.preloaded_generators: Dict[str, ExternalResourceGenerator] = {}
        self.sync_file: Optional[Path] = None
        self.is_master = False
        self.is_worker = False
    
    def initialize_for_master(self) -> None:
        """主进程初始化"""
        self.is_master = True
        self.is_worker = False
        self.sync_file = Path(tempfile.mktemp(suffix='_resource_sync.json'))
        self.sync_file.unlink(missing_ok=True)
        print(f"[ResourcePreloader] Initialized for master, sync file: {self.sync_file}")
    
    def initialize_for_worker(self, sync_file: Path) -> None:
        """Worker 进程初始化"""
        self.is_master = False
        self.is_worker = True
        self.sync_file = sync_file
        print(f"[ResourcePreloader] Initialized for worker, sync file: {self.sync_file}")
    
    def register_generator(self, name: str, generator: ExternalResourceGenerator) -> None:
        """注册支持外部资源的生成器"""
        self.preloaded_generators[name] = generator
        
        if self.is_master and generator.preload:
            # 主进程预加载数据
            print(f"[ResourcePreloader] Preloading data for generator: {name}")
            try:
                data = generator.preload_data()
                generator.set_preloaded_data(data)
                print(f"[ResourcePreloader] Preloaded {len(data)} items for {name}")
                
                # 写入同步文件
                self._write_sync_file()
            except Exception as e:
                print(f"[ResourcePreloader] Failed to preload {name}: {e}")
                # 回退到懒加载
                generator.preload = False
                import traceback
                traceback.print_exc()
    
    def _write_sync_file(self) -> None:
        """写入同步文件"""
        if not self.sync_file:
            return
        
        # 只同步预加载的数据
        data = {
            'generators': {}
        }
        
        for name, gen in self.preloaded_generators.items():
            if gen.preload and gen.get_preloaded_data() is not None:
                data['generators'][name] = {
                    'name': name,
                    'data': gen.get_preloaded_data(),
                    'resource_type': gen.resource_type,
                    'preload': True
                }
        
        # 原子写入（只有数据时才写入）
        if data['generators']:
            try:
                temp_file = self.sync_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                temp_file.replace(self.sync_file)
                print(f"[ResourcePreloader] Sync file written: {self.sync_file}")
            except Exception as e:
                print(f"[ResourcePreloader] Failed to write sync file: {e}")
                import traceback
                traceback.print_exc()
    
    def load_from_sync_file(self) -> None:
        """从同步文件加载数据"""
        if not self.sync_file or not self.sync_file.exists():
            print(f"[ResourcePreloader] Sync file not found: {self.sync_file}")
            return
        
        try:
            with open(self.sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for name, gen_data in data.get('generators', {}).items():
                # Worker 进程从全局注册表获取生成器并设置数据
                if name in global_registry.list():
                    generator = global_registry.get(name)
                    if isinstance(generator, ExternalResourceGenerator):
                        generator.set_preloaded_data(gen_data['data'])
                        print(f"[ResourcePreloader] Loaded {len(gen_data['data'])} items for {name}")
                    else:
                        print(f"[ResourcePreloader] Generator {name} is not ExternalResourceGenerator")
                else:
                    print(f"[ResourcePreloader] Generator {name} not found in registry")
        except Exception as e:
            print(f"[ResourcePreloader] Failed to load from sync file: {e}")
            import traceback
            traceback.print_exc()
    
    def sync_to_worker(self, config: Any) -> None:
        """同步到 worker"""
        if self.is_master and self.sync_file:
            if hasattr(config, 'workerinput'):
                config.workerinput['resource_sync_file'] = str(self.sync_file)
                print(f"[ResourcePreloader] Passing sync file to worker: {self.sync_file}")
    
    def sync_from_master(self, config: Any) -> None:
        """从主进程同步"""
        if self.is_worker:
            workerinput = getattr(config, 'workerinput', {})
            sync_file_str = workerinput.get('resource_sync_file')
            if sync_file_str:
                self.initialize_for_worker(Path(sync_file_str))
                self.load_from_sync_file()
    
    def cleanup(self) -> None:
        """清理临时文件"""
        if self.sync_file and self.is_master:
            try:
                self.sync_file.unlink(missing_ok=True)
                self.sync_file.with_suffix('.tmp').unlink(missing_ok=True)
                print(f"[ResourcePreloader] Cleaned up sync file: {self.sync_file}")
            except Exception as e:
                print(f"[ResourcePreloader] Failed to cleanup: {e}")


# 全局预加载管理器实例
resource_preloader = ResourcePreloader()


# ============================================================================
# 装饰器
# ============================================================================

def external_resource_generator(resource_type: str = None,
                               preload: bool = True,
                               scope: str = "function",
                               cache: bool = False):
    """
    外部资源生成器装饰器
    
    Args:
        resource_type: 资源类型 ('database', 'network', 'file')
        preload: 是否预加载
        scope: 作用域
        cache: 是否缓存
    
    Returns:
        生成器实例
    
    Example:
        @external_resource_generator(resource_type='database', preload=True)
        def generate_db_data():
            import database
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_data")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
    """
    from functools import wraps
    
    def decorator(func: GeneratorFunc) -> ExternalResourceGenerator:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 创建支持外部资源的生成器
        generator = ExternalResourceGenerator(
            func=wrapper,
            scope=scope,
            cache=cache,
            preload=preload,
            resource_type=resource_type
        )
        
        # 注册到预加载管理器
        generator_name = func.__name__
        resource_preloader.register_generator(generator_name, generator)
        
        # 也注册到全局注册表
        global_registry.register(generator_name, generator)
        
        return generator
    
    return decorator


# ============================================================================
# Worker 连接池（用于懒加载场景）
# ============================================================================

class WorkerConnectionPool:
    """Worker 进程独立的连接池基类"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._pools: Dict[str, Any] = {}
        self._worker_id = self._get_worker_id()
    
    def _get_worker_id(self) -> str:
        """获取 worker ID"""
        import os
        return os.environ.get('PYTEST_XDIST_WORKER', 'master')
    
    @contextmanager
    def get_connection(self, resource_name: str):
        """获取连接"""
        conn = self._pools.get(resource_name)
        
        if conn is None:
            # 创建新连接
            conn = self._create_connection(resource_name)
            self._pools[resource_name] = conn
        
        try:
            yield conn
        except Exception as e:
            # 连接失败，尝试重连
            print(f"[{self._worker_id}] Connection failed: {e}, reconnecting...")
            conn = self._create_connection(resource_name)
            self._pools[resource_name] = conn
            yield conn
    
    def _create_connection(self, resource_name: str):
        """创建连接（子类实现）"""
        raise NotImplementedError
    
    def close_all(self):
        """关闭所有连接"""
        for name, conn in self._pools.items():
            try:
                if hasattr(conn, 'close'):
                    conn.close()
            except Exception as e:
                print(f"[{self._worker_id}] Failed to close connection {name}: {e}")
        self._pools.clear()


# 数据库连接池实现
class DatabasePool(WorkerConnectionPool):
    """数据库连接池"""
    
    def __init__(self, connection_func: Callable = None):
        self._connection_func = connection_func
        super().__init__()
    
    def _create_connection(self, resource_name: str):
        """创建数据库连接"""
        if self._connection_func:
            return self._connection_func()
        else:
            # 默认实现
            try:
                import database
                return database.connect()
            except ImportError:
                raise ImportError(
                    "Please provide a connection function or install 'database' module"
                )


# 全局数据库连接池实例
db_pool = DatabasePool()


# ============================================================================
# pytest 钩子函数
# ============================================================================

# 这些钩子函数已经在 pytest_plugin.py 中定义，此处注释掉以避免重复
# def pytest_configure(config: Any) -> None:
#     """pytest 配置钩子"""
#     if hasattr(config, 'workerinput'):
#         # Worker 进程
#         print("[pytest_configure] Initializing for worker")
#         resource_preloader.initialize_for_worker(config)
#         resource_preloader.sync_from_master(config)
#     else:
#         # 主进程
#         print("[pytest_configure] Initializing for master")
#         resource_preloader.initialize_for_master()
# 
# 
# def pytest_configure_node(node: Any) -> None:
#     """配置 worker 节点钩子"""
#     print("[pytest_configure_node] Syncing to worker")
#     resource_preloader.sync_to_worker(node.workerinput)
# 
# 
# def pytest_unconfigure(config: Any) -> None:
#     """pytest 卸载钩子"""
#     print("[pytest_unconfigure] Cleaning up")
#     resource_preloader.cleanup()
#     if 'db_pool' in globals():
#         db_pool.close_all()
