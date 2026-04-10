# 同步方案：文件同步 + pytest 钩子传递

## 📋 目录

1. [方案概述](#方案概述)
2. [核心设计](#核心设计)
3. [实现细节](#实现细节)
4. [使用指南](#使用指南)
5. [完整示例](#完整示例)
6. [性能优化](#性能优化)
7. [故障排查](#故障排查)
8. [最佳实践](#最佳实践)

---

## 方案概述

### 为什么需要同步方案？

单一方案存在局限性：

**方案一（文件同步）的局限**：
- ⚠️ 无法传递运行时配置
- ⚠️ 临时文件管理复杂
- ⚠️ 并发访问可能冲突

**方案二（pytest 钩子）的局限**：
- ⚠️ 只能传递可序列化数据
- ⚠️ 数据大小有限制
- ⚠️ 无法传递大型数据集

### 同步方案的优势

结合两种方案的优势：

```
┌─────────────────────────────────────────────────────┐
│              同步方案架构                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  主进程                          Worker 进程         │
│    │                                 │              │
│    ├── 文件同步 ───────────────────> │              │
│    │   - 生成器元数据                │              │
│    │   - 预加载数据（大数据）        │              │
│    │   - 外部资源数据                │              │
│    │                                 │              │
│    ├── pytest 钩子 ────────────────> │              │
│    │   - Worker 配置                 │              │
│    │   - 运行时参数                  │              │
│    │   - 同步状态                    │              │
│    │                                 │              │
└─────────────────────────────────────────────────────┘
```

**核心优势**：
- ✅ **大数据走文件** - 避免序列化限制
- ✅ **小配置走钩子** - 快速高效
- ✅ **两层验证** - 确保同步可靠性
- ✅ **灵活回退** - 一种方式失败时用另一种

---

## 核心设计

### 三层架构

```python
┌─────────────────────────────────────────┐
│  应用层                                  │
│  - @sync_generator 装饰器               │
│  - 普通生成器                           │
│  - 外部资源生成器                        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  同步层                                  │
│  - SyncManager                          │
│  - 文件同步                             │
│  - pytest 钩子传递                       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  存储层                                  │
│  - 临时文件（大数据）                   │
│  - pytest workerinput（小配置）         │
└─────────────────────────────────────────┘
```

### 数据流

```python
# 主进程
1. 注册生成器 → SyncManager
2. 预加载数据 → 写入同步文件
3. 准备配置 → pytest_configure_node
4. 传递配置 → workerinput

# Worker 进程
1. 接收配置 → pytest_configure
2. 初始化管理器 → apply_from_hook
3. 读取同步文件 → load_from_sync_file
4. 设置生成器数据 → set_preloaded_data
```

---

## 实现细节

### 核心组件

#### 1. SyncManager

```python
class SyncManager:
    """同步管理器"""
    
    def __init__(self):
        # 配置
        self.config = WorkerConfig()
        
        # 文件同步
        self.sync_file: Optional[Path] = None
        self.resource_sync_file: Optional[Path] = None
        
        # 生成器注册
        self.generators: Dict[str, GeneratorBase] = {}
        self.external_generators: Dict[str, Any] = {}
        
        # 线程安全
        self._lock = threading.Lock()
    
    def initialize_for_master(self) -> None:
        """主进程初始化"""
        # 创建同步文件
        self.sync_file = Path(tempfile.mktemp(suffix='_sync.json'))
        
        # 设置配置
        self.config.is_master = True
        self.config.is_worker = False
    
    def initialize_for_worker(self, config_data: Dict[str, Any]) -> None:
        """Worker 进程初始化"""
        # 从钩子配置加载
        self.config = WorkerConfig.from_dict(config_data)
        
        # 从文件加载数据
        self.load_from_sync_file()
    
    def register_generator(self, name: str, generator: GeneratorBase, 
                          preload_data: Optional[List[Any]] = None) -> None:
        """注册生成器"""
        self.generators[name] = generator
        
        # 主进程预加载数据
        if self.config.is_master and preload_data:
            self._write_sync_file()
```

#### 2. WorkerConfig

```python
class WorkerConfig:
    """Worker 配置（通过 pytest 钩子传递）"""
    
    def __init__(self):
        self.worker_id: str = "master"
        self.is_master: bool = True
        self.is_worker: bool = False
        self.sync_file_path: Optional[str] = None
        self.custom_config: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化（用于 pytest 钩子传递）"""
        return {
            'worker_id': self.worker_id,
            'sync_file_path': self.sync_file_path,
            'custom_config': self.custom_config
        }
```

#### 3. 装饰器

```python
def sync_generator(resource_type: str = None,
                    preload: bool = True,
                    scope: str = "function",
                    cache: bool = False,
                    use_file_sync: bool = True):
    """
    同步生成器装饰器
    
    Args:
        resource_type: 资源类型（None=普通，'database'/'network'=外部资源）
        preload: 是否预加载
        scope: 作用域
        cache: 是否缓存
        use_file_sync: 是否使用文件同步
    """
    def decorator(func: GeneratorFunc):
        # 创建生成器
        if resource_type:
            generator = ExternalResourceGenerator(...)
        else:
            generator = GeneratorBase(...)
        
        # 注册到同步管理器
        sync_manager.register_generator(func.__name__, generator)
        
        return generator
    
    return decorator
```

---

## 使用指南

### 快速开始

#### Step 1: 定义生成器

```python
from dynamic_params.engine.generator.sync_manager import sync_generator

# 普通生成器
@sync_generator(scope='session', cache=True)
def generate_simple():
    yield from [1, 2, 3]

# 外部资源生成器（预加载）
@sync_generator(resource_type='database', preload=True)
def generate_db_data():
    if is_master():
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data")
        return cursor.fetchall()
    return []
```

#### Step 2: 在 conftest.py 中初始化

```python
# tests/conftest.py
def pytest_configure(config):
    from dynamic_params.engine.generator.sync_manager import sync_manager
    
    if hasattr(config, 'workerinput'):
        # Worker 进程
        hook_config = config.workerinput.get('sync_config', {})
        sync_manager.apply_from_hook(hook_config)
        sync_manager.initialize_for_worker(hook_config)
        sync_manager.load_from_sync_file()
    else:
        # 主进程
        sync_manager.initialize_for_master()

def pytest_configure_node(node):
    from dynamic_params.engine.generator.sync_manager import sync_manager
    
    # 准备配置（小数据）
    config_data = sync_manager.prepare_for_hook()
    config_data['worker_id'] = node.workerinput.get('workerid')
    
    # 通过钩子传递
    node.workerinput['sync_config'] = config_data

def pytest_unconfigure(config):
    from dynamic_params.engine.generator.sync_manager import sync_manager
    sync_manager.cleanup()
```

#### Step 3: 在测试中使用

```python
import pytest
from dynamic_params import parametrize_fixture

@parametrize_fixture("data", "generator:generate_db_data")
@pytest.fixture
def data_fixture(data):
    return data

def test_with_data(data_fixture):
    assert data_fixture is not None
```

#### Step 4: 运行测试

```bash
# 单个 worker
pytest tests/ -v

# 多个 worker（验证同步）
pytest tests/ -n 2 -v

# 详细输出
pytest tests/ -n 2 -v --capture=no
```

---

## 完整示例

### 示例 1：普通生成器

```python
from dynamic_params.engine.generator.sync_manager import sync_generator

@sync_generator(scope='session', cache=True)
def generate_session_data():
    """Session 级别数据 - 通过文件同步元数据"""
    print(f"Worker: {get_worker_id()}")
    yield from [1, 2, 3, 4, 5]

import pytest
from dynamic_params import parametrize_fixture

@parametrize_fixture("data", "generator:generate_session_data")
@pytest.fixture
def session_data_fixture(data):
    return data

def test_session(session_data_fixture):
    assert session_data_fixture in [1, 2, 3, 4, 5]
```

### 示例 2：数据库预加载

```python
@sync_generator(resource_type='database', preload=True, scope='session')
def generate_users():
    """从数据库加载用户 - 主进程预加载，文件同步"""
    if is_master():
        import database
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users")
        users = [
            {'id': row[0], 'username': row[1]}
            for row in cursor.fetchall()
        ]
        print(f"Loaded {len(users)} users")
        return users
    return []

@parametrize_fixture("user", "generator:generate_users")
@pytest.fixture
def user_fixture(user):
    return user

def test_user_data(user_fixture):
    assert 'username' in user_fixture
```

### 示例 3：网络 API 调用

```python
@sync_generator(resource_type='network', preload=True, scope='session')
def generate_exchange_rates():
    """从 API 加载汇率 - 只调用一次"""
    if is_master():
        import requests
        response = requests.get('https://api.exchangerate.com/latest')
        return response.json()['rates']
    return []

@parametrize_test("rate", "generator:generate_exchange_rates")
def test_currency(rate):
    assert isinstance(rate, (int, float))
```

### 示例 4：混合场景

```python
# 静态数据 - 预加载
@sync_generator(preload=True, scope='session')
def generate_config():
    if is_master():
        return {'timeout': 30, 'retry': 3}
    return []

# 实时数据 - Worker 独立
@xdist_safe_generator(scope='function')
def generate_realtime_logs():
    with db_pool.get_connection('logs_db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM logs ORDER BY created_at DESC LIMIT 10")
        for row in cursor.fetchall():
            yield {'id': row[0]}

# 组合使用
@parametrize_generator("config", "generator:generate_config")
@parametrize_test("log", "generator:generate_realtime_logs")
def test_mixed(config, log):
    assert 'timeout' in config
    assert 'id' in log
```

---

## 性能优化

### 1. 数据分层策略

```python
# 大数据走文件
@sync_generator(preload=True)
def generate_large_data():
    if is_master():
        # 加载 100MB 数据
        return large_dataset  # 文件同步

# 小数据走钩子
def pytest_configure_node(node):
    # 传递小配置
    node.workerinput['small_config'] = {'key': 'value'}  # 钩子传递
```

### 2. 分批加载

```python
@sync_generator(preload=True)
def generate_batched_data():
    if is_master():
        all_data = []
        batch_size = 1000
        
        for i in range(0, total, batch_size):
            batch = load_batch(i, batch_size)
            all_data.extend(batch)
            print(f"Loaded batch {i//batch_size}")
        
        return all_data
    return []
```

### 3. 懒加载回退

```python
@sync_generator(preload=False)  # 不预加载
def generate_lazy_data():
    """数据量太大时，使用懒加载"""
    # 每个 worker 独立加载
    import database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM large_table")
    
    for row in cursor.fetchall():
        yield row
```

---

## 故障排查

### 问题 1: Worker 无法获取数据

```python
# 错误：GeneratorNotFoundError

# 原因：忘记在 conftest.py 中初始化

# ❌ 错误
def pytest_configure(config):
    pass  # 忘记调用 sync_manager

# ✅ 正确
def pytest_configure(config):
    if hasattr(config, 'workerinput'):
        sync_manager.initialize_for_worker(...)
        sync_manager.load_from_sync_file()
    else:
        sync_manager.initialize_for_master()
```

### 问题 2: 同步文件不存在

```python
# 错误：FileNotFoundError

# 原因：主进程未创建同步文件

# 检查：
def test_check_sync():
    from dynamic_params.engine.generator.sync_manager import sync_manager
    
    status = sync_manager.get_sync_status()
    print(f"Sync file exists: {status['sync_file_exists']}")
    
    if not status['sync_file_exists']:
        print("ERROR: Sync file not created by master")
```

### 问题 3: 数据不一致

```python
# 错误：不同 worker 获取到不同数据

# 原因：预加载数据未正确同步

# 解决：验证同步状态
def test_verify_sync():
    status = get_sync_status()
    
    assert status['initialized'], "Not initialized"
    assert status['synced'], "Not synced"
    assert status['sync_file_exists'], "Sync file missing"
```

---

## 最佳实践

### ✅ 推荐

```python
# 1. 静态数据使用预加载
@sync_generator(preload=True, scope='session')

# 2. 动态数据使用 Worker 独立
@xdist_safe_generator(scope='function')

# 3. 敏感数据脱敏
return {'id': user.id}  # 不包含 password

# 4. 错误处理
try:
    return api_call()
except Exception as e:
    print(f"API failed: {e}")
    return fallback_data()

# 5. 正确初始化
def pytest_configure(config):
    if hasattr(config, 'workerinput'):
        sync_manager.initialize_for_worker(...)
    else:
        sync_manager.initialize_for_master()
```

### ❌ 避免

```python
# 1. 返回连接对象
@sync_generator(preload=True)
def generate_data():
    conn = database.connect()
    return conn  # ❌ TypeError

# 2. 忘记清理
def pytest_unconfigure(config):
    pass  # ❌ 忘记调用 sync_manager.cleanup()

# 3. 大数据一次性加载
return list(range(10_000_000))  # ❌ 内存爆炸

# 4. 不验证同步状态
def test_something():
    # 直接使用，不检查是否同步
    data = generator.execute()  # ❌ 可能为空
```

---

## 性能对比

| 指标 | 纯文件同步 | 纯钩子传递 | **同步方案** |
|------|-----------|-----------|-------------|
| **大数据支持** | ✅ 优秀 | ❌ 差 | ✅ **优秀** |
| **小配置传递** | ⚠️ 一般 | ✅ 优秀 | ✅ **优秀** |
| **可靠性** | ⚠️ 中等 | ⚠️ 中等 | ✅ **高** |
| **灵活性** | ⚠️ 一般 | ⚠️ 一般 | ✅ **高** |
| **实现复杂度** | ✅ 简单 | ✅ 简单 | ⚠️ 中等 |

---

## 总结

### 核心优势

1. **大数据走文件** - 避免序列化限制
2. **小配置走钩子** - 快速高效
3. **两层验证** - 确保同步可靠性
4. **灵活回退** - 一种方式失败时用另一种

### 适用场景

- ✅ 生产环境（需要高可靠性）
- ✅ 混合数据（静态 + 动态）
- ✅ 外部资源（数据库、API）
- ✅ 大型测试套件

### 实施步骤

1. **识别数据类型**
   - 大数据 → 文件同步
   - 小配置 → pytest 钩子

2. **选择装饰器**
   - 普通生成器 → `@sync_generator`
   - 外部资源 → `@sync_generator(resource_type=...)`

3. **初始化**
   - 在 conftest.py 中设置钩子

4. **验证**
   - 单 worker 测试
   - 多 worker 验证

---

**版本**: 1.0.0  
**更新日期**: 2026-03-31  
**维护者**: Dynamic Params Team
