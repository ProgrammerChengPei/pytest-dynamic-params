# pytest-dynamic-params

一个用于动态参数生成和参数化的 pytest 插件，旨在解决 `pytest.mark.parametrize` 的局限性，让测试参数化更灵活、更强大。

## 特性

- **动态参数生成**：使用生成器函数动态生成测试参数，支持复杂逻辑
- **扩展参数化**：支持对测试函数、fixture 和生成器进行参数化
- **链式参数依赖**：支持基于参数名自动匹配的链式依赖关系
- **无缝集成**：与 pytest 原生功能完全兼容
- **缓存策略**：生成器支持缓存，提高性能
- **懒加载**：生成器支持懒加载，按需生成数据
- **并行测试自动预加载**：Session/module 级别的生成器自动在主进程预加载并同步到所有 Worker
- **Worker 独立连接**：每个 Worker 拥有独立的数据库/连接池，用于实时数据查询

## 安装

### 从 PyPI 安装

```bash
pip install pytest-dynamic-params
```

### 从源码安装

```bash
pip install -e .
```

## 使用方法

### 基础用法

#### 定义参数生成器

```python
from dynamic_params import param_generator

@param_generator(scope="session", cache=True)
def generate_user_ids():
    """生成用户 ID"""
    for i in range(10):
        yield i
```

#### 参数化测试函数

使用 `@pytest.mark.parametrize` 进行标准参数化：

```python
import pytest

@pytest.mark.parametrize("user_id, expected", [[1, 2], [3, 4]])
def test_user(user_id, expected):
    assert user_id + 1 == expected
```

#### 在参数化中使用生成器

```python
import pytest

@pytest.mark.parametrize("user_id", generate_user_ids)
def test_user(user_id):
    assert isinstance(user_id, int)
    assert user_id >= 0
```

### 高级用法

#### 参数化 fixture

使用 `@parametrize_fixture` 装饰器对 fixture 进行参数化：

```python
from dynamic_params import parametrize_fixture

@parametrize_fixture("user_id", [1, 2, 3])
def user(user_id):
    """根据 user_id 提供 user 的 fixture"""
    return {"id": user_id, "name": f"User {user_id}"}

def test_user_fixture(user):
    assert "id" in user
    assert "name" in user
```

**多层依赖示例**：

```python
from dynamic_params import parametrize_fixture

@parametrize_fixture("base_url", ["http://localhost", "http://testserver"])
def url_context(base_url):
    return {"base": base_url}

@parametrize_fixture("endpoint", ["/users", "/posts", "/comments"])
def full_url(url_context, endpoint):
    return f"{url_context['base']}{endpoint}"

def test_api_url(full_url):
    assert full_url.startswith("http://")
```

#### 链式参数生成器

动态参数生成器支持多级链式依赖，支持显式和隐式两种配置模式：

**显式依赖模式 - 使用 pytest.mark.parametrize**

```python
import pytest
from dynamic_params import param_generator

@param_generator
def generate_base_values():
    """基础值生成器"""
    return [1, 2, 3]

@param_generator
@pytest.mark.parametrize("base_value", generate_base_values)  # 显式依赖
def generate_scaled_values(base_value):
    """依赖基础值生成器"""
    return [base_value * 2, base_value * 3]
```

**隐式依赖模式 - 参数名自动匹配**

```python
import pytest
from dynamic_params import param_generator

@param_generator
def base_values():
    """基础值生成器"""
    return [1, 2, 3]

@param_generator
def scale_factor():
    """比例因子生成器"""
    return [2, 3]

@param_generator
def scaled_values(base_values, scale_factor):  # 参数名与生成器名精确匹配
    """依赖多个生成器的链式生成器"""
    return [value * factor for value in base_values for factor in scale_factor]
```

#### 高级链式依赖示例

**多级链式依赖（A → B → C 模式）**

```python
import pytest
from dynamic_params import param_generator

@param_generator
def database_names():
    """第一级：数据库名称"""
    return ["primary", "secondary"]

@param_generator
@pytest.mark.parametrize("db_name", database_names)
def table_names(db_name):
    """第二级：数据库表名（依赖数据库名）"""
    return [f"{db_name}_users", f"{db_name}_posts"]

@param_generator
@pytest.mark.parametrize("table_name", table_names)
def query_templates(table_name):
    """第三级：查询模板（依赖表名）"""
    return [f"SELECT * FROM {table_name}", f"SELECT count(*) FROM {table_name}"]
```

**与原生 pytest 功能混合使用**

```python
import pytest
from dynamic_params import param_generator

@pytest.fixture
def default_multiplier():
    return 2

@param_generator
def values_to_scale():
    return [1, 2, 3]

@param_generator
def scale_factors():
    return [2, 3, 4]

@param_generator
def scaled_results(values_to_scale, scale_factors, default_multiplier):
    # 依赖生成器 + fixture
    results = []
    for value in values_to_scale:
        for factor in scale_factors:
            results.append(value * factor * default_multiplier)
    return results
```

## 配置

可以通过 `pytest.ini` 或 `conftest.py` 配置插件：

### pytest.ini

```ini
[pytest]
dynamic_params_default_cache = false
dynamic_params_default_lazy = false
dynamic_params_default_scope = function
```

### conftest.py

```python
def pytest_configure(config):
    config.addinivalue_line("dynamic_params_default_cache", "false")
    config.addinivalue_line("dynamic_params_default_lazy", "false")
    config.addinivalue_line("dynamic_params_default_scope", "function")
```

## 性能优化

### 缓存

生成器可以缓存以避免重复计算：

```python
@param_generator(scope="session", cache=True)
def generate_expensive_data():
    # 高开销的计算
    return [1, 2, 3]
```

### 懒加载

生成器可以懒加载，只在需要时生成数据：

```python
@param_generator(lazy=True)
def generate_large_dataset():
    # 按需生成
    for i in range(1000000):
        yield i
```

### 并行测试支持

对于 pytest-xdist 并行测试，插件提供自动同步机制：

**静态数据 - 自动预加载**：

```python
@param_generator(scope='session', cache=True)
def generate_static_config():
    """自动在主进程预加载并同步到所有 Worker"""
    return {'timeout': 30, 'retry': 3}
```

**实时数据 - Worker 独立**：

```python
from dynamic_params.engine.generator.worker_pool import WorkerPool

@param_generator(scope='function')
def generate_realtime_orders():
    """每个 Worker 独立的数据库连接"""
    with WorkerPool.get_connection('orders_db', create_conn_func) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM orders WHERE status = 'pending'")
        for row in cursor.fetchall():
            yield {'id': row[0]}
```

**核心优势**：

- ✅ **装饰器零改动**：无需在装饰器中添加额外参数
- ✅ **自动预加载**：Session/module 级别的生成器自动预加载
- ✅ **Worker 隔离**：每个 Worker 对实时数据有独立连接
- ✅ **数据一致性**：所有 Worker 接收相同的预加载数据

## 与 pytest.mark.parametrize 的关系

### 功能对比

| 功能                    | pytest.mark.parametrize | 本插件                               |
| -------------------- | ----------------------- | --------------------------------- |
| Fixture 参数化           | ❌                       | ✅（@parametrize\_fixture）          |
| 动态参数生成（链式依赖）     | ❌                       | ✅（@param\_generator）              |
| 生成器 scope 自动推断   | ❌                       | ✅（基于依赖的自动 scope 管理）        |
| 隐式依赖识别（参数名匹配） | ❌                       | ✅（通过生成器名自动匹配）            |

### 使用建议

- **简单参数化**：使用官方 `@pytest.mark.parametrize`
- **需要对 fixture 参数化**：使用插件的 `@parametrize_fixture`
- **需要动态生成链式依赖参数**：使用插件的 `@param_generator`
- **生成器依赖管理**：结合 `@param_generator` 和 `@pytest.mark.parametrize` 实现显式依赖

### 兼容性

本插件与 `pytest.mark.parametrize` 完全兼容，可以混合使用。

## 兼容性

- **Python**: 3.7+
- **pytest**: 7.0+
- **pytest-xdist**: 支持并行测试

## 测试

运行测试：

```bash
pytest
```

运行覆盖率测试：

```bash
pytest --cov=dynamic_params
```

## 许可证

MIT License

## 贡献

欢迎贡献！请参见 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与贡献。

## 问题反馈

如果遇到任何问题，请在 [GitHub 仓库](https://github.com/yourusername/pytest-dynamic-params/issues) 提交 Issue。

## 常见问题

### Q: 生成器函数可以返回任意类型的数据吗？

A: 是的，生成器可以返回任何可迭代的数据类型，包括列表、元组、生成器表达式等。

### Q: 可以在一个测试函数上使用多个参数化装饰器吗？

A: 是的，支持在同一个测试函数上使用多个参数化装饰器，它们会组合生成所有可能的参数组合。

### Q: 插件支持 pytest 的所有版本吗？

A: 插件支持 pytest 7.0+ 版本，建议使用最新版本以获得最佳体验。
