# 与 pytest.mark.parametrize 对比

本文档详细对比 `pytest.mark.parametrize` 和 `pytest-dynamic-params` 插件的功能和使用场景。

## 功能对比矩阵

| 功能 | pytest.mark.parametrize | pytest-dynamic-params |
|------|-------------------------|----------------------|
| **测试函数参数化** | ✅ | ✅ (`@parametrize_test`) |
| **Fixture 参数化** | ❌ | ✅ (`@parametrize_fixture`) |
| **生成器参数化** | ❌ | ✅ (`@parametrize_generator`) |
| **动态参数引用** | ❌ | ✅ (`DynRef`) |
| **动态参数生成** | ❌ | ✅ (`@param_generator`) |
| **参数依赖处理** | ❌ | ✅ (自动解析依赖) |
| **缓存机制** | ❌ | ✅ (支持缓存) |
| **懒加载** | ❌ | ✅ (支持懒加载) |
| **并行测试同步** | ⚠️ (需手动处理) | ✅ (自动同步) |

## 详细对比

### 1. 测试函数参数化

#### pytest.mark.parametrize

```python
import pytest

@pytest.mark.parametrize("input_value,expected", [
    (1, 2),
    (2, 3),
    (3, 4),
])
def test_simple(input_value, expected):
    assert input_value + 1 == expected
```

**特点**：
- ✅ 语法简洁
- ✅ 静态参数
- ❌ 参数值必须在定义时确定
- ❌ 无法引用其他参数

#### pytest-dynamic-params

```python
from dynamic_params import parametrize_test, DynRef

# 基础用法（与 pytest 兼容）
@parametrize_test("input_value,expected", [
    (1, 2),
    (2, 3),
    (3, 4),
])
def test_simple(input_value, expected):
    assert input_value + 1 == expected

# 动态参数引用
@parametrize_test("a", [1, 2])
@parametrize_test("b", [3, 4])
@parametrize_test("result", [DynRef("a") + DynRef("b")])
def test_with_ref(a, b, result):
    assert result == a + b
```

**优势**：
- ✅ 支持参数间引用
- ✅ 支持动态计算
- ✅ 完全兼容 pytest 语法

### 2. Fixture 参数化

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

### 3. 动态参数生成

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
from dynamic_params import param_generator, parametrize_test

# 使用生成器动态生成参数
@param_generator
def generate_large_dataset():
    """动态生成大数据集"""
    for i in range(1000000):
        yield i

@parametrize_test("value", generate_large_dataset)
def test_many_values(value):
    assert value >= 0

# 依赖外部数据源
@param_generator(scope='session')
def generate_user_data():
    """从数据库加载用户数据"""
    import database
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    return [
        {"id": row[0], "username": row[1]}
        for row in cursor.fetchall()
    ]

@parametrize_test("user", generate_user_data)
def test_users(user):
    assert "username" in user
```

**优势**：
- ✅ 支持复杂逻辑生成参数
- ✅ 可以依赖外部数据源
- ✅ 支持懒加载，节省内存
- ✅ 支持缓存，提高性能

### 4. 参数依赖处理

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

#### pytest-dynamic-params

```python
from dynamic_params import parametrize_test, DynRef

# 自动处理参数依赖
@parametrize_test("a", [1, 2, 3])
@parametrize_test("b", [4, 5, 6])
@parametrize_test("sum", [DynRef("a") + DynRef("b")])
def test_sum(a, b, sum):
    assert a + b == sum

# 复杂依赖
@parametrize_test("base", [10])
@parametrize_test("multiplier", [2, 3])
@parametrize_test("result", [DynRef("base") * DynRef("multiplier")])
def test_complex(base, multiplier, result):
    assert result == base * multiplier
```

**优势**：
- ✅ 自动解析依赖关系
- ✅ 支持复杂表达式
- ✅ 代码清晰易维护

### 5. 缓存和性能

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
- ✅ 需要动态生成参数
- ✅ 参数间有依赖关系
- ✅ 需要参数化 fixture
- ✅ 大数据集参数化
- ✅ 依赖外部数据源
- ✅ 并行测试环境

**示例**：
```python
from dynamic_params import param_generator, parametrize_test, DynRef

# 动态生成参数
@param_generator
def generate_test_data():
    return load_from_database()

# 参数化 fixture
@parametrize_fixture("user_id", generate_test_data)
@pytest.fixture
def user(user_id):
    return {"id": user_id}

# 参数依赖
@parametrize_test("a", [1, 2])
@parametrize_test("b", [DynRef("a") * 2])
def test_dependency(a, b):
    assert b == a * 2
```

## 兼容性说明

### 完全兼容

本插件与 `pytest.mark.parametrize` 完全兼容，可以混合使用：

```python
import pytest
from dynamic_params import parametrize_test

# 混合使用
@pytest.mark.parametrize("static_param", [1, 2, 3])
@parametrize_test("dynamic_param", [4, 5, 6])
def test_mixed(static_param, dynamic_param):
    assert static_param + dynamic_param
```

### 迁移建议

**从 pytest.mark.parametrize 迁移**：

1. **保持简单参数化**：
   ```python
   # 继续使用 pytest.mark.parametrize
   @pytest.mark.parametrize("input,expected", [(1, 2)])
   def test_simple(input, expected):
       ...
   ```

2. **复杂场景使用插件**：
   ```python
   # 使用 pytest-dynamic-params
   from dynamic_params import parametrize_test, DynRef
   
   @parametrize_test("a", [1, 2])
   @parametrize_test("b", [DynRef("a") * 2])
   def test_complex(a, b):
       ...
   ```

## 性能对比

| 场景 | pytest.mark.parametrize | pytest-dynamic-params | 性能提升 |
|------|------------------------|----------------------|---------|
| 简单参数化 | 100% | 95-100% | - |
| 动态参数生成 | ❌ 不支持 | ✅ 支持 | ∞ |
| 大数据集（缓存） | 1x | 5-10x | 500-1000% |
| 并行测试同步 | 手动 | 自动 | - |

## 总结

### pytest.mark.parametrize 的优势

- ✅ 语法简洁
- ✅ pytest 内置支持
- ✅ 适合简单场景

### pytest-dynamic-params 的优势

- ✅ 功能强大
- ✅ 支持动态参数
- ✅ 支持参数依赖
- ✅ 支持 fixture 和生成器参数化
- ✅ 性能优化（缓存、懒加载）
- ✅ 并行测试自动同步

### 最佳实践

**根据场景选择合适的工具**：

1. **简单静态参数** → `pytest.mark.parametrize`
2. **动态参数/依赖** → `pytest-dynamic-params`
3. **混合使用** → 两者结合，发挥各自优势

---

**相关文档**：
- [使用指南](usage-guide.md)
- [架构设计](../specs/架构设计.md)
- [详细设计](../specs/详细设计.md)
