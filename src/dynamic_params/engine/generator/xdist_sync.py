"""
生成器在 xdist worker 进程间同步的实现方案

本模块提供了在 pytest-xdist 环境中同步生成器的机制，确保所有 worker 进程
都能访问到相同的生成器定义和状态。

实现方案：
1. 使用 JSON 序列化生成器元数据
2. 通过 pytest 的 workerinput/workeroutput 钩子在 master 和 worker 之间传递
3. 在每个 worker 进程中重新注册生成器
4. 使用进程安全的缓存机制
"""

import json
import pickle
import hashlib
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import tempfile
import os

from .base import GeneratorBase
from .registry import GeneratorRegistry, registry as global_registry
from ...types import GeneratorFunc


class GeneratorMetadata:
    """生成器元数据，用于序列化"""
    
    def __init__(self, name: str, func_name: str, scope: str = "function",
                 cache: bool = False, lazy: bool = False, 
                 source_code: str = None, module_name: str = None):
        self.name = name
        self.func_name = func_name
        self.scope = scope
        self.cache = cache
        self.lazy = lazy
        self.source_code = source_code
        self.module_name = module_name
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'func_name': self.func_name,
            'scope': self.scope,
            'cache': self.cache,
            'lazy': self.lazy,
            'source_code': self.source_code,
            'module_name': self.module_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneratorMetadata':
        """从字典创建"""
        return cls(**data)
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GeneratorMetadata':
        """从 JSON 字符串创建"""
        return cls.from_dict(json.loads(json_str))


class XdistGeneratorSync:
    """xdist 生成器同步管理器"""
    
    def __init__(self):
        self.registered_generators: Dict[str, GeneratorMetadata] = {}
        self.sync_file: Optional[Path] = None
        self.is_master = False
        self.is_worker = False
    
    def initialize_for_master(self) -> None:
        """在主进程中初始化"""
        self.is_master = True
        self.is_worker = False
        # 创建临时文件用于 worker 间同步
        self.sync_file = Path(tempfile.mktemp(suffix='_gen_sync.json'))
        self.sync_file.unlink(missing_ok=True)
    
    def initialize_for_worker(self, sync_file: Path) -> None:
        """在 worker 进程中初始化"""
        self.is_master = False
        self.is_worker = True
        self.sync_file = sync_file
    
    def register_generator(self, name: str, generator: GeneratorBase) -> None:
        """注册生成器并记录元数据"""
        # 获取生成器函数信息
        func = generator.func
        metadata = GeneratorMetadata(
            name=name,
            func_name=func.__name__,
            scope=generator.scope,
            cache=generator.cache,
            lazy=generator.lazy,
            source_code=self._get_source_code(func),
            module_name=func.__module__
        )
        self.registered_generators[name] = metadata
        
        # 如果是主进程，更新同步文件
        if self.is_master:
            self._write_sync_file()
    
    def _get_source_code(self, func: Callable) -> str:
        """获取函数的源代码"""
        try:
            import inspect
            return inspect.getsource(func)
        except (OSError, TypeError):
            # 无法获取源代码时返回 None
            return None
    
    def _write_sync_file(self) -> None:
        """写入同步文件"""
        if not self.sync_file:
            return
        
        data = {
            'generators': {
                name: meta.to_dict() 
                for name, meta in self.registered_generators.items()
            }
        }
        
        # 使用原子写入避免并发问题
        temp_file = self.sync_file.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        temp_file.replace(self.sync_file)
    
    def load_from_sync_file(self) -> None:
        """从同步文件加载生成器元数据"""
        if not self.sync_file or not self.sync_file.exists():
            return
        
        with open(self.sync_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for name, meta_dict in data.get('generators', {}).items():
            self.registered_generators[name] = GeneratorMetadata.from_dict(meta_dict)
    
    def recreate_generator(self, metadata: GeneratorMetadata, 
                          global_namespace: Dict[str, Any] = None) -> Optional[GeneratorBase]:
        """从元数据重新创建生成器"""
        if metadata.source_code:
            # 尝试从源代码重新创建
            return self._recreate_from_source(metadata, global_namespace)
        else:
            # 尝试从模块导入
            return self._recreate_from_module(metadata, global_namespace)
    
    def _recreate_from_source(self, metadata: GeneratorMetadata,
                             global_namespace: Dict[str, Any] = None) -> Optional[GeneratorBase]:
        """从源代码重新创建生成器"""
        try:
            # 创建命名空间
            namespace = global_namespace or {}
            
            # 执行源代码
            exec(metadata.source_code, namespace)
            
            # 获取函数
            func = namespace.get(metadata.func_name)
            if func is None:
                return None
            
            # 创建生成器实例
            generator_class = type('DynamicGenerator', (GeneratorBase,), {})
            generator = generator_class(
                func=func,
                scope=metadata.scope,
                cache=metadata.cache,
                lazy=metadata.lazy
            )
            
            return generator
        except Exception as e:
            print(f"Failed to recreate generator from source: {e}")
            return None
    
    def _recreate_from_module(self, metadata: GeneratorMetadata,
                             global_namespace: Dict[str, Any] = None) -> Optional[GeneratorBase]:
        """从模块导入重新创建生成器"""
        try:
            # 导入模块
            if metadata.module_name:
                import importlib
                module = importlib.import_module(metadata.module_name)
                func = getattr(module, metadata.func_name, None)
                
                if func:
                    generator_class = type('DynamicGenerator', (GeneratorBase,), {})
                    generator = generator_class(
                        func=func,
                        scope=metadata.scope,
                        cache=metadata.cache,
                        lazy=metadata.lazy
                    )
                    return generator
        except Exception as e:
            print(f"Failed to recreate generator from module: {e}")
            return None
        
        return None
    
    def sync_to_worker(self, config: Any) -> None:
        """将生成器同步到 worker 进程"""
        if not self.is_master:
            return
        
        # 将同步文件路径传递给 worker
        config.workerinput['generator_sync_file'] = str(self.sync_file)
    
    def sync_from_master(self, config: Any) -> None:
        """从主进程同步生成器"""
        if not self.is_worker:
            return
        
        # 从配置中获取同步文件路径
        sync_file_str = getattr(config, 'workerinput', {}).get('generator_sync_file')
        if sync_file_str:
            sync_file = Path(sync_file_str)
            self.initialize_for_worker(sync_file)
            self.load_from_sync_file()
            
            # 重新创建并注册生成器
            self._recreate_and_register_generators()
    
    def _recreate_and_register_generators(self) -> None:
        """重新创建并注册所有生成器"""
        for name, metadata in self.registered_generators.items():
            generator = self.recreate_generator(metadata)
            if generator:
                global_registry.register(name, generator)
    
    def cleanup(self) -> None:
        """清理临时文件"""
        if self.sync_file and self.is_master:
            self.sync_file.unlink(missing_ok=True)
            self.sync_file.with_suffix('.tmp').unlink(missing_ok=True)


# 全局同步管理器实例
xdist_sync = XdistGeneratorSync()


# pytest 钩子函数
def pytest_configure(config: Any) -> None:
    """pytest 配置钩子"""
    # 判断是否是主进程
    if hasattr(config, 'workerinput'):
        # worker 进程
        xdist_sync.initialize_for_worker(config)
        xdist_sync.sync_from_master(config)
    else:
        # 主进程
        xdist_sync.initialize_for_master()


def pytest_configure_node(node: Any) -> None:
    """配置 worker 节点钩子"""
    # 将同步信息传递给 worker
    xdist_sync.sync_to_worker(node.workerinput)


def pytest_unconfigure(config: Any) -> None:
    """pytest 卸载钩子"""
    xdist_sync.cleanup()


# 装饰器包装器，用于自动注册生成器元数据
def xdist_safe_generator(func: GeneratorFunc = None, *,
                         scope: str = "function",
                         cache: bool = False,
                         lazy: bool = False) -> Callable:
    """
    xdist 安全的生成器装饰器
    
    这个装饰器会自动记录生成器的元数据，以便在 xdist worker 进程间同步
    
    Args:
        func: 生成器函数
        scope: 作用域
        cache: 是否缓存
        lazy: 是否懒加载
    
    Returns:
        生成器实例
    """
    from functools import wraps
    
    def decorator(fn: GeneratorFunc) -> GeneratorBase:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        
        # 创建生成器
        generator = GeneratorBase(
            func=wrapper,
            scope=scope,
            cache=cache,
            lazy=lazy
        )
        
        # 注册到同步管理器
        generator_name = fn.__name__
        xdist_sync.register_generator(generator_name, generator)
        
        # 也注册到全局注册表
        global_registry.register(generator_name, generator)
        
        return generator
    
    if func is not None:
        return decorator(func)
    
    return decorator
