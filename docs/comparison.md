# 与 pytest.mark.parametrize 对比

本文档详细对比 `pytest.mark.parametrize` 和 `pytest-dynamic-params` 插件的功能和使用场景。

## 功能对比矩阵

| 功能 | pytest.mark.parametrize | pytest-dynamic-params |
|------|-------------------------|----------------------|
| **测试函数参数化** | ✅ | ❌ (不提供) |
| **Fixture 参数化** | ❌ | ✅ (`@parametrize_fixture`) |
| **链式参数生成** | ❌ | ✅ (`@param_generator`) |
| **参数依赖处理** | ❌ | ✅ (链式依赖自动解析) |
| **缓存机制** | ❌ | ✅ (支持缓存) |
| **懒加载** | ❌ | ✅ (支持懒加载) |
| **并行测试同步** | ⚠️ (需手动处理) | ✅ (自动同步) |
| **Scope 自动推断** | ❌ | ✅ (基于依赖关系的智能 scope 推断) |

## 详细对比

### 1. Fixture 参数化

#### pytest.mark.parametrize（间接方式）

```python
import pytest

@pytest.fixture(params=[1, 2, 3])
def user_id(request):
    return request.param

@pytest.fixture
def user(user_id):
    return {"id": user_id, "name": f"User {user_id}"}

def test_user(user):
    assert user["id"] in [1, 2, 3]
```

**局限**：
- ❌ 需要 `params` 参数
- ❌ 无法动态生成参数
- ❌ 依赖关系复杂时难以维护

#### pytest-dynamic-params

```python
from dynamic_params import parametrize_fixture

# 直接参数化 fixture
@parametrize_fixture("user_id", [1, 2, 3])
@pytest.fixture
def user(user_id):
    return {"id": user_id, "name": f"User {user_id}"}

def test_user(user):
    assert user["id"] in [1, 2, 3]

# 多层依赖
@parametrize_fixture("base_url", ["http://localhost", "http://testserver"])
@pytest.fixture
def url_context(base_url):
    return {"base": base_url}

@parametrize_fixture("endpoint", ["/users", "/posts"])
@pytest.fixture
def full_url(url_context, endpoint):
    return f"{url_context['base']}{endpoint}"

def test_api(full_url):
    assert full_url.startswith("http://")
```

**优势**：
- ✅ 语法简洁
- ✅ 支持多层依赖
- ✅ 可以使用生成器

### 2. 链式参数生成

#### pytest.mark.parametrize

```python
import pytest

# 无法动态生成参数
# 必须在定义时确定所有参数值
@pytest.mark.parametrize("value", list(range(100)))
def test_many_values(value):
    assert value >= 0
```

**局限**：
- ❌ 无法使用函数生成参数
- ❌ 无法依赖运行时上下文
- ❌ 大数据集占用内存

#### pytest-dynamic-params

```python
from dynamic_params import param_generator, parametrize_fixture

# 使用链式生成器动态生成参数
@param_generator
def generate_large_dataset():
    """动态生成大数据集"""
    for i in range(1000000):
        yield i

@parametrize_fixture("value", generate_large_dataset)
@pytest.fixture
def test_value(value):
    return value

def test_many_values(test_value):
    assert test_value >= 0

# 链式依赖生成器
@param_generator
def database_connection():
    """提供数据库连接"""
    import database
    return database.connect()

@param_generator
def user_data(db_conn):
    """链式依赖数据库连接获取用户数据"""
    cursor = db_conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    return [
        {"id": row[0], "username": row[1]}
        for row in cursor.fetchall()
    ]

@parametrize_fixture("user", user_data)
@pytest.fixture
def user_fixture(user):
    return user

# Scope 自动推断：user_data 继承 db_conn 的最小 scope
```

**优势**：
- ✅ 支持复杂逻辑生成参数
- ✅ 可以依赖外部数据源
- ✅ 支持懒加载，节省内存
- ✅ 支持缓存，提高性能
- ✅ 支持链式依赖自动解析
- ✅ 自动推断 scope

### 3. 参数依赖处理

#### pytest.mark.parametrize

```python
import pytest

# 无法直接处理参数依赖
# 需要手动组合参数
@pytest.mark.parametrize("a,b,sum", [
    (1, 2, 3),
    (2, 3, 5),
    (3, 4, 7),
])
def test_sum(a, b, sum):
    assert a + b == sum
```

**局限**：
- ❌ 需要手动计算依赖值
- ❌ 参数多时组合复杂
- ❌ 容易出错

#### pytest-dynamic-params（链式生成器方案）

```python
import pytest
from dynamic_params import param_generator, parametrize_fixture

# 链式依赖生成器
@param_generator
def generate_base_values():
    """生成基础值"""
    yield from [1, 2, 3]

@param_generator
def generate_multipliers(value):
    """依赖基础值生成乘数"""
    yield from [2 * value, 3 * value, 4 * value]

@param_generator
def calculate_result(base, multiplier):
    """链式依赖计算最终结果"""
    return base + multiplier

# 使用 fixture 组合链式生成器
@parametrize_fixture("base", generate_base_values)
@pytest.fixture
def base_fixture(base):
    return base

@parametrize_fixture("multiplier", generate_multipliers)
@pytest.fixture  
def multiplier_fixture(multiplier):
    return multiplier

@parametrize_fixture("result", calculate_result)
@pytest.fixture
def result_fixture(result):
    return result
```

**优势**：
- ✅ 自动解析依赖关系
- ✅ 支持复杂依赖链
- ✅ 代码清晰易维护
- ✅ 自动 scope 推断

### 4. 缓存和性能

#### pytest.mark.parametrize

```python
import pytest

# 无缓存机制
# 每次测试都会重新计算
@pytest.mark.parametrize("data", [
    expensive_computation()  # 每次都执行
    for _ in range(100)
])
def test_data(data):
    assert data is not None
```

**局限**：
- ❌ 无缓存机制
- ❌ 重复计算开销大
- ❌ 无法控制执行时机

#### pytest-dynamic-params

```python
from dynamic_params import param_generator

# 支持缓存
@param_generator(scope="session", cache=True)
def generate_expensive_data():
    """只执行一次，结果缓存"""
    return expensive_computation()

# 支持懒加载
@param_generator(lazy=True)
def generate_lazy_data():
    """只在需要时执行"""
    return large_dataset()

# 并行测试自动预加载
@param_generator(scope='session')
def generate_static_config():
    """主进程预加载，同步到所有 Worker"""
    return load_config()
```

**优势**：
- ✅ 支持缓存，避免重复计算
- ✅ 支持懒加载，按需生成
- ✅ 并行测试自动同步

## 使用场景建议

### 使用 pytest.mark.parametrize

**适用场景**：
- ✅ 简单的静态参数化
- ✅ 参数值在定义时确定
- ✅ 无参数依赖关系
- ✅ 小型测试套件

**示例**：
```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 3),
])
def test_simple(input, expected):
    assert input + 1 == expected
```

### 使用 pytest-dynamic-params

**适用场景**：
- ✅ 需要参数化 fixture
- ✅ 动态生成参数
- ✅ 参数间有依赖关系
- ✅ 大数据集参数化
- ✅ 依赖外部数据源
- ✅ 并行测试环境
- ✅ 需要自动 scope 推断

**示例**：
```python
from dynamic_params import param_generator, parametrize_fixture

# 链式依赖生成器
@param_generator
def database_config():
    return load_database_config()

@param_generator
def database_connection(db_config):
    return connect_to_database(db_config)

@param_generator
def user_data(db_conn):
    return fetch_user_data(db_conn)

# 参数化 fixture
@parametrize_fixture("user", user_data)
@pytest.fixture
def user_fixture(user):
    return process_user_data(user)

def test_user_fixture(user_fixture):
    assert "id" in user_fixture
```

## 兼容性说明

### 混合使用

本插件与 `pytest.mark.parametrize` 完全兼容，可以混合使用：

```python
import pytest
from dynamic_params import parametrize_fixture

# 混合使用
@parametrize_fixture("dynamic_value", [4, 5, 6])
@pytest.fixture
def dynamic_fixture(dynamic_value):
    return dynamic_value

@pytest.mark.parametrize("static_value", [1, 2, 3])
def test_mixed(dynamic_fixture, static_value):
    result = dynamic_fixture + static_value
    assert result > 0
```

### 架构建议

**推荐使用模式**：

1. **简单参数化** → 继续使用 `pytest.mark.parametrize`
2. **复杂依赖/动态参数** → 使用 `pytest-dynamic-params` 的链式生成器
3. **Fixture 参数化** → 使用 `@parametrize_fixture`
4. **需要缓存/懒加载** → 使用 `@param_generator` 的相应选项

## 性能对比

| 场景 | pytest.mark.parametrize | pytest-dynamic-params | 性能提升 |
|------|------------------------|----------------------|---------|
| 简单参数化 | 100% | ❌ 废弃 | - |
| Fixture 参数化 | ❌ 不支持 | ✅ 支持 | ∞ |
| 动态参数生成 | ❌ 不支持 | ✅ 支持 | ∞ |
| 大数据集（缓存） | ❌ 不支持 | 5-10x | 500-1000% |
| 复杂依赖链 | ❌ 不支持 | 自动解析 | ∞ |

## 总结

### pytest.mark.parametrize 的优势

- ✅ 语法简洁
- ✅ pytest 内置支持
- ✅ 适合简单静态参数化场景

### pytest-dynamic-params 的优势

- ✅ 强大的 fixture 参数化
- ✅ 先进的链式参数生成器
- ✅ 自动依赖解析和 scope 推断
- ✅ 性能优化（缓存、懒加载）
- ✅ 并行测试自动同步

### 最佳实践

**根据场景选择合适的工具**：

1. **简单静态参数** → `pytest.mark.parametrize`
2. **Fixture 参数化/动态参数/依赖链** → `pytest-dynamic-params`
3. **混合使用** → 两者结合，发挥各自优势

---

**相关文档**：
- [使用指南](usage-guide.md)
- [项目结构](STRUCTURE.md)
- [架构设计](../specs/架构设计.md)
- [详细设计](../specs/详细设计.md)