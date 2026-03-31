# 生成器依赖外部资源的 xdist 同步方案

## 问题场景

当生成器依赖外部资源时，之前的方案都不适用：

```python
# ❌ 问题示例 1：依赖数据库
@xdist_safe_generator
def generate_db_data():
    import database
    conn = database.connect()  # ← 每个 worker 都会连接数据库
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tests")
    for row in cursor:
        yield row[0]

# 问题：
# 1. 每个 worker 都创建数据库连接（资源浪费）
# 2. 连接可能冲突（锁表、事务隔离）
# 3. 数据库连接无法序列化
```

```python
# ❌ 问题示例 2：依赖网络 API
@xdist_safe_generator
def generate_api_data():
    import requests
    response = requests.get('https://api.example.com/data')  # ← 每个 worker 都调用 API
    for item in response.json():
        yield item

# 问题：
# 1. 多次调用 API（可能被限流）
# 2. 网络延迟影响性能
# 3. API 响应可能不一致
```

```python
# ❌ 问题示例 3：依赖全局状态
counter = 0

@xdist_safe_generator
def generate_with_state():
    global counter
    counter += 1  # ← 每个 worker 有自己的 counter 副本
    yield counter

# 问题：
# 1. 状态不共享
# 2. 每个 worker 的 counter 独立计数
# 3. 结果不一致
```

---

## 解决方案：资源感知的同步方案

### 核心设计原则

1. **资源预加载**：在主进程中预先加载外部资源
2. **数据序列化**：只传递数据，不传递资源连接
3. **懒加载回退**：无法序列化时使用懒加载策略
4. **连接池管理**：每个 worker 独立的连接池

---

## 方案一：预加载 + 数据同步（推荐）✅

### 工作流程

```
主进程                          Worker 进程
  |                                 |
  |-- 1. 连接外部资源 --------------|
  |                                 |
  |-- 2. 加载数据到内存 ------------|
  |                                 |
  |-- 3. 序列化数据（不是连接）-----|
  |                                 |
  |                                 |-- 4. 接收数据
  |                                 |
  |                                 |-- 5. 使用数据生成
```

### 实现代码

```python
# src/dynamic_params/engine/generator/external_resource.py

import json
import hashlib
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path
import tempfile
from contextlib import contextmanager

from .base import GeneratorBase
from .registry import registry as global_registry
from ...types import GeneratorFunc


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
        """
        raise NotImplementedError
    
    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """执行生成器"""
        if self.preload and self._preloaded_data is not None:
            # 使用预加载的数据
            return self._preloaded_data
        else:
            # 直接执行（懒加载模式）
            return super().execute(*args, **kwargs)
    
    def set_preloaded_data(self, data: List[Any]) -> None:
        """设置预加载的数据"""
        self._preloaded_data = data
    
    def get_preloaded_data(self) -> Optional[List[Any]]:
        """获取预加载的数据"""
        return self._preloaded_data


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
    
    def initialize_for_worker(self, sync_file: Path) -> None:
        """Worker 进程初始化"""
        self.is_master = False
        self.is_worker = True
        self.sync_file = sync_file
    
    def register_generator(self, name: str, generator: ExternalResourceGenerator) -> None:
        """注册支持外部资源的生成器"""
        self.preloaded_generators[name] = generator
        
        if self.is_master and generator.preload:
            # 主进程预加载数据
            print(f"[Master] Preloading data for generator: {name}")
            try:
                data = generator.preload_data()
                generator.set_preloaded_data(data)
                print(f"[Master] Preloaded {len(data)} items for {name}")
                
                # 写入同步文件
                self._write_sync_file()
            except Exception as e:
                print(f"[Master] Failed to preload {name}: {e}")
                # 回退到懒加载
                generator.preload = False
    
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
        
        # 原子写入
        if data['generators']:  # 只有数据时才写入
            temp_file = self.sync_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            temp_file.replace(self.sync_file)
    
    def load_from_sync_file(self) -> None:
        """从同步文件加载数据"""
        if not self.sync_file or not self.sync_file.exists():
            return
        
        with open(self.sync_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for name, gen_data in data.get('generators', {}).items():
            # Worker 进程不需要重新创建生成器
            # 只需要从全局注册表获取并设置数据
            if name in global_registry.list():
                generator = global_registry.get(name)
                if isinstance(generator, ExternalResourceGenerator):
                    generator.set_preloaded_data(gen_data['data'])
                    print(f"[Worker] Loaded {len(gen_data['data'])} items for {name}")
    
    def sync_to_worker(self, config: Any) -> None:
        """同步到 worker"""
        if self.is_master and self.sync_file:
            config.workerinput['resource_sync_file'] = str(self.sync_file)
    
    def sync_from_master(self, config: Any) -> None:
        """从主进程同步"""
        if self.is_worker:
            sync_file_str = getattr(config, 'workerinput', {}).get('resource_sync_file')
            if sync_file_str:
                self.initialize_for_worker(Path(sync_file_str))
                self.load_from_sync_file()
    
    def cleanup(self) -> None:
        """清理"""
        if self.sync_file and self.is_master:
            self.sync_file.unlink(missing_ok=True)
            self.sync_file.with_suffix('.tmp').unlink(missing_ok=True)


# 全局预加载管理器
resource_preloader = ResourcePreloader()


# 装饰器
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
```

---

### 使用示例

#### 1. 数据库场景

```python
# tests/conftest.py
from dynamic_params.engine.generator.external_resource import (
    external_resource_generator,
    resource_preloader
)

# 定义数据库生成器
@external_resource_generator(
    resource_type='database',
    preload=True,  # 关键：预加载数据
    scope='session',
    cache=True
)
def generate_db_test_data():
    """
    从数据库加载测试数据
    
    主进程会预加载所有数据，然后同步到 worker
    """
    import database
    
    # 预加载时执行
    if resource_preloader.is_master:
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM test_data WHERE active = true")
        
        # 返回数据列表（不是连接对象）
        data = [
            {'id': row[0], 'name': row[1]}
            for row in cursor.fetchall()
        ]
        return data
    
    # Worker 进程不会执行到这里（使用预加载的数据）
    return []

# pytest 钩子
def pytest_configure(config):
    from dynamic_params.engine.generator.external_resource import resource_preloader
    
    if hasattr(config, 'workerinput'):
        # Worker 进程
        resource_preloader.initialize_for_worker(config)
        resource_preloader.sync_from_master(config)
    else:
        # 主进程
        resource_preloader.initialize_for_master()

def pytest_configure_node(node):
    from dynamic_params.engine.generator.external_resource import resource_preloader
    resource_preloader.sync_to_worker(node.workerinput)

def pytest_unconfigure(config):
    from dynamic_params.engine.generator.external_resource import resource_preloader
    resource_preloader.cleanup()
```

```python
# tests/test_database.py
from dynamic_params import parametrize_test

@parametrize_test("test_data", "generator:generate_db_test_data")
def test_database_data(test_data):
    """
    测试数据库数据
    
    所有 worker 都使用相同的预加载数据
    不会创建额外的数据库连接
    """
    assert 'id' in test_data
    assert 'name' in test_data
    print(f"Testing with data: {test_data}")
```

---

#### 2. 网络 API 场景

```python
# tests/conftest.py
from dynamic_params.engine.generator.external_resource import external_resource_generator

@external_resource_generator(
    resource_type='network',
    preload=True,
    scope='session',
    cache=True
)
def generate_api_test_data():
    """
    从 API 加载测试数据
    
    只在主进程调用一次 API
    """
    import requests
    
    # 主进程调用 API
    if resource_preloader.is_master:
        response = requests.get('https://api.example.com/test-data')
        response.raise_for_status()
        
        # 返回数据（不是 response 对象）
        return response.json()
    
    return []
```

```python
# tests/test_api.py
from dynamic_params import parametrize_test

@parametrize_test("api_data", "generator:generate_api_test_data")
def test_api_response(api_data):
    """
    测试 API 数据
    
    所有 worker 使用相同的数据
    不会触发额外的 API 调用
    """
    assert 'id' in api_data
    assert 'value' in api_data
```

---

#### 3. 混合场景（部分预加载）

```python
# tests/conftest.py
from dynamic_params.engine.generator.external_resource import (
    external_resource_generator,
    resource_preloader
)

# 预加载静态数据
@external_resource_generator(
    resource_type='database',
    preload=True,
    scope='session'
)
def generate_static_data():
    """静态数据，适合预加载"""
    if resource_preloader.is_master:
        # 加载配置数据（小数据量）
        return [
            {'config_key': 'timeout', 'config_value': '30'},
            {'config_key': 'retry', 'config_value': '3'},
        ]
    return []

# 动态数据，使用懒加载
@external_resource_generator(
    resource_type='database',
    preload=False,  # 不预加载
    scope='function'
)
def generate_dynamic_data():
    """
    动态数据，每个 worker 独立加载
    
    适用于：
    1. 数据量太大
    2. 数据实时变化
    3. 每个 worker 需要独立视图
    """
    import database
    
    # 每个 worker 都会执行这里
    conn = database.connect()
    cursor = conn.cursor()
    
    # 获取实时数据
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
    count = cursor.fetchone()[0]
    
    yield {'pending_orders': count}
```

---

### 优化策略

#### 1. 大数据集的分块加载

```python
@external_resource_generator(
    resource_type='database',
    preload=True,
    scope='session'
)
def generate_large_dataset():
    """
    大数据集分块加载
    
    避免一次性加载过多数据
    """
    if resource_preloader.is_master:
        import database
        
        conn = database.connect()
        cursor = conn.cursor()
        
        # 分批加载（每批 1000 条）
        batch_size = 1000
        offset = 0
        all_data = []
        
        while True:
            cursor.execute(
                "SELECT id FROM large_table LIMIT %s OFFSET %s",
                (batch_size, offset)
            )
            batch = cursor.fetchall()
            
            if not batch:
                break
            
            all_data.extend([{'id': row[0]} for row in batch])
            offset += batch_size
            
            print(f"Loaded {len(all_data)} rows...")
        
        return all_data
    
    return []
```

#### 2. 敏感数据的安全处理

```python
@external_resource_generator(
    resource_type='database',
    preload=True,
    scope='session'
)
def generate_secure_data():
    """
    敏感数据处理
    
    不序列化敏感字段
    """
    if resource_preloader.is_master:
        import database
        
        conn = database.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password_hash, email FROM users")
        
        # 过滤敏感字段
        safe_data = [
            {
                'id': row[0],
                # 不包含 password_hash
                'email': row[2].split('@')[0] + '@***'  # 脱敏
            }
            for row in cursor.fetchall()
        ]
        
        return safe_data
    
    return []
```

#### 3. 错误处理和回退

```python
@external_resource_generator(
    resource_type='network',
    preload=True,
    scope='session'
)
def generate_with_fallback():
    """
    预加载失败时使用回退策略
    """
    if resource_preloader.is_master:
        import requests
        
        try:
            # 尝试从 API 加载
            response = requests.get('https://api.example.com/data', timeout=5)
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            print(f"API failed: {e}, using fallback data")
            # 回退到本地数据
            return [
                {'id': 1, 'value': 'fallback_1'},
                {'id': 2, 'value': 'fallback_2'},
            ]
    
    return []
```

---

## 方案二：Worker 独立连接池

### 适用场景

- 数据量太大，无法预加载
- 数据实时变化，需要最新状态
- 每个 worker 需要独立的数据库视图

### 实现

```python
# src/dynamic_params/engine/generator/worker_pool.py

from typing import Dict, Any, Optional
from contextlib import contextmanager
import threading

class WorkerConnectionPool:
    """Worker 进程独立的连接池"""
    
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
                conn.close()
            except:
                pass
        self._pools.clear()


# 数据库连接池
class DatabasePool(WorkerConnectionPool):
    def _create_connection(self, resource_name: str):
        import database
        return database.connect()


# 全局连接池实例
db_pool = DatabasePool()
```

```python
# tests/conftest.py
from dynamic_params.engine.generator.worker_pool import db_pool

@xdist_safe_generator(scope='function')
def generate_with_worker_pool():
    """
    使用 worker 独立的连接池
    
    每个 worker 有自己的数据库连接
    """
    with db_pool.get_connection('test_db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM test_data")
        
        for row in cursor.fetchall():
            yield {'id': row[0]}
```

---

## 方案三：混合策略（最佳实践）

### 核心思想

结合预加载和连接池：
- **静态数据** → 预加载 + 同步
- **动态数据** → Worker 独立连接池
- **配置数据** → 预加载
- **实时数据** → 懒加载

### 完整示例

```python
# tests/conftest.py
from dynamic_params.engine.generator.external_resource import (
    external_resource_generator,
    resource_preloader
)
from dynamic_params.engine.generator.worker_pool import db_pool
from dynamic_params import parametrize_test, parametrize_generator

# ============================================================================
# 1. 静态数据 - 预加载
# ============================================================================

@external_resource_generator(
    resource_type='database',
    preload=True,
    scope='session',
    cache=True
)
def generate_static_config():
    """静态配置数据 - 预加载"""
    if resource_preloader.is_master:
        with db_pool.get_connection('config_db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM app_config")
            return [
                {'key': row[0], 'value': row[1]}
                for row in cursor.fetchall()
            ]
    return []

# ============================================================================
# 2. 动态数据 - Worker 独立连接池
# ============================================================================

@xdist_safe_generator(scope='function')
def generate_realtime_orders():
    """实时订单数据 - 每个 worker 独立加载"""
    with db_pool.get_connection('orders_db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, status FROM orders WHERE created_at > NOW() - INTERVAL '1 hour'"
        )
        
        for row in cursor.fetchall():
            yield {'id': row[0], 'status': row[1]}

# ============================================================================
# 3. 网络 API - 带缓存
# ============================================================================

@external_resource_generator(
    resource_type='network',
    preload=True,
    scope='session',
    cache=True
)
def generate_external_rates():
    """外部汇率数据 - 预加载 + 缓存"""
    if resource_preloader.is_master:
        import requests
        
        try:
            response = requests.get(
                'https://api.exchangerate.com/latest',
                timeout=5
            )
            response.raise_for_status()
            return response.json()['rates']
        
        except Exception as e:
            print(f"Exchange rate API failed: {e}")
            # 回退数据
            return {'USD': 1.0, 'EUR': 0.85, 'GBP': 0.73}
    
    return []

# ============================================================================
# 4. 组合使用
# ============================================================================

@parametrize_generator("config", "generator:generate_static_config")
@parametrize_test("order", "generator:generate_realtime_orders")
def test_order_with_config(config, order):
    """
    测试订单处理
    
    - config: 预加载的静态配置
    - order: 实时订单数据
    """
    assert 'key' in config
    assert 'id' in order

# ============================================================================
# Pytest 钩子
# ============================================================================

def pytest_configure(config):
    if hasattr(config, 'workerinput'):
        resource_preloader.initialize_for_worker(config)
        resource_preloader.sync_from_master(config)
    else:
        resource_preloader.initialize_for_master()

def pytest_configure_node(node):
    resource_preloader.sync_to_worker(node.workerinput)

def pytest_unconfigure(config):
    resource_preloader.cleanup()
    db_pool.close_all()
```

---

## 性能对比

| 场景 | 预加载方案 | Worker 连接池 | 混合方案 |
|------|-----------|------------|---------|
| **数据库连接数** | 1 个（主进程） | N 个（每个 worker） | 1 + N |
| **API 调用次数** | 1 次 | N 次 | 1 次 |
| **内存占用** | 高（主进程） | 低 | 中等 |
| **数据一致性** | ✅ 完全一致 | ❌ 可能不一致 | ⚠️ 部分一致 |
| **实时性** | ❌ 启动时快照 | ✅ 实时 | ⚠️ 混合 |
| **适用数据量** | < 100 MB | 不限 | 灵活 |

---

## 选择指南

### 使用预加载（方案一）

```python
@external_resource_generator(preload=True)
```

**适用场景**：
- ✅ 数据量适中（< 100 MB）
- ✅ 数据不频繁变化
- ✅ 需要数据一致性
- ✅ 外部资源有限（数据库连接数限制）

**不适用**：
- ❌ 数据量巨大（GB 级别）
- ❌ 数据实时变化
- ❌ 每个 worker 需要独立视图

---

### 使用 Worker 连接池（方案二）

```python
@xdist_safe_generator + WorkerConnectionPool
```

**适用场景**：
- ✅ 数据量巨大
- ✅ 需要实时数据
- ✅ 每个 worker 独立操作
- ✅ 数据库支持并发连接

**不适用**：
- ❌ 数据库连接数有限
- ❌ API 有调用频率限制
- ❌ 需要数据强一致性

---

### 使用混合方案（方案三）

```python
# 静态数据预加载
@external_resource_generator(preload=True)

# 动态数据连接池
@xdist_safe_generator + WorkerConnectionPool
```

**推荐用于**：
- ✅ 生产环境
- ✅ 复杂业务场景
- ✅ 性能和一致性都需要

---

## 故障排查

### 问题 1：预加载失败

```python
# 错误：TypeError: Object of type Connection is not JSON serializable

# 原因：尝试序列化数据库连接
@external_resource_generator(preload=True)
def generate_data():
    conn = database.connect()
    return conn  # ❌ 错误：返回连接对象

# 解决：返回数据，不是连接
@external_resource_generator(preload=True)
def generate_data():
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    return cursor.fetchall()  # ✅ 正确：返回数据列表
```

### 问题 2：Worker 无法获取数据

```python
# 错误：GeneratorNotFoundError

# 原因：忘记在钩子中初始化
def pytest_configure(config):
    # ❌ 忘记调用
    # resource_preloader.initialize_for_worker(config)
    # resource_preloader.sync_from_master(config)
    pass

# 解决：正确初始化
def pytest_configure(config):
    if hasattr(config, 'workerinput'):
        resource_preloader.initialize_for_worker(config)
        resource_preloader.sync_from_master(config)
```

---

## 总结

### 推荐方案

**生产环境** → 混合方案（方案三）

**关键要点**：
1. ✅ 静态数据预加载（配置、字典）
2. ✅ 动态数据 Worker 独立连接（订单、日志）
3. ✅ 外部 API 带缓存和回退
4. ✅ 正确的资源清理

### 实施步骤

1. **识别资源类型**
   - 数据库、网络、文件
   - 静态、动态、配置

2. **选择加载策略**
   - 预加载 or 懒加载
   - 共享 or 独立

3. **实现生成器**
   - 使用正确的装饰器
   - 处理异常情况

4. **测试验证**
   - 单 worker 测试
   - 多 worker 验证
   - 性能测试

---

**版本**: 1.0.0  
**更新日期**: 2026-03-31  
**维护者**: Dynamic Params Team
