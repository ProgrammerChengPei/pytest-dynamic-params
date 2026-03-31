# pytest-dynamic-params 使用指南

## 概述

`pytest-dynamic-params` 是一个用于pytest的动态参数化插件，允许测试开发者声明式地定义参数生成器，系统自动处理参数收集、依赖解析、动态参数生成和测试用例参数化。

## 安装

### 从 PyPI 安装

```bash
pip install pytest-dynamic-params
```

### 从源码安装（开发模式）

```bash
pip install -e .
```

## 核心概念

### 1. 参数生成器 (`@generator`)

使用 `@generator` 装饰器定义的函数，用于动态生成参数值。支持配置作用域、缓存和懒加载。

### 2. 动态参数装饰器 (`@use_generators`)

使用 `@use_generators` 装饰器将参数生成器与测试函数关联起来，支持多个动态参数。

### 3. 动态参数化装饰器 (`@dynamic_parametrize`)

使用 `@dynamic_parametrize` 装饰器参数化测试函数，类似于 pytest 的 `@pytest.mark.parametrize`，但支持动态解析参数值和引用 fixture。

### 4. 引用对象 (`DynRef`)

使用 `DynRef` 类创建对参数或 fixture 的引用，用于在 `@dynamic_parametrize` 中动态解析值。

### 5. 作用域管理

支持四种作用域：`function`（默认）、`class`、`module`、`session`，控制参数生成的生命周期。

### 6. 依赖解析

系统自动分析生成器函数的参数签名，确定依赖关系并按正确顺序执行，支持复杂的依赖链。

### 7. 懒加载

通过 `lazy` 参数控制是否启用懒加载，避免不必要的参数生成，提高性能。

### 8. 缓存机制

通过 `cache` 参数控制是否启用缓存，对于计算密集型的参数生成可以显著提高性能。

## 装饰器1：`@generator` 装饰器

### 基本功能

`@generator` 装饰器用于定义参数生成器函数，这些函数可以动态生成测试参数值。生成器函数可以接受参数，这些参数可以是普通值、fixture 或其他生成器的返回值。

### 基本用法

```python
from dynamic_params import generator

@generator
def calculate_result(input_value):
    """计算结果生成器

    Args:
        input_value: 输入值

    Returns:
        计算结果
    """
    return input_value * 2
```

### 高级配置

#### 作用域控制

```python
import random

@generator(scope="function")  # 每个测试函数重新生成
def function_scoped_data():
    """函数作用域数据生成器

    每个测试函数执行时都会重新生成
    """
    return random.randint(1, 100)

@generator(scope="class")     # 每个测试类共享
def class_scoped_data():
    """类作用域数据生成器

    每个测试类只生成一次，类内所有测试共享
    """
    return "shared among class"

@generator(scope="module")    # 每个模块共享
def module_scoped_data():
    """模块作用域数据生成器

    每个模块只生成一次，模块内所有测试共享
    """
    return "shared among module"

@generator(scope="session")   # 整个测试会话共享
def session_scoped_data():
    """会话作用域数据生成器

    整个测试会话只生成一次，所有测试共享
    """
    return "shared across session"
```

#### 缓存控制

```python
@generator(cache=True)  # 启用缓存（默认）
def cached_data(input_value):
    """启用缓存的数据生成器

    对于相同的输入值，会缓存结果，提高性能
    """
    # 计算密集型操作
    return expensive_computation(input_value)

@generator(cache=False)  # 禁用缓存
def uncached_data():
    """禁用缓存的数据生成器

    每次调用都会重新生成，适合返回时间相关的值
    """
    return time.time()  # 每次调用返回不同值
```

#### 懒加载控制

```python
def compute_expensive_value(input_value):
    """模拟计算密集型操作"""
    print(f"Computing value for {input_value}")
    return input_value * 10

@generator(lazy=True)  # 启用懒加载（默认）
def lazy_data(input_value):
    """启用懒加载的数据生成器

    只有在实际使用时才会执行，避免不必要的计算
    """
    return compute_expensive_value(input_value)

@generator(lazy=False)  # 禁用懒加载
def eager_data(input_value):
    """禁用懒加载的数据生成器

    会立即执行，不管是否使用，适合需要提前计算的场景
    """
    return compute_expensive_value(input_value)
```

### 错误处理

#### 循环依赖检测

```python
# 这将触发循环依赖错误
@generator
def generate_a(b_value):  # 依赖于b
    return f"A_based_on_{b_value}"

@generator 
def generate_b(a_value):  # 依赖于a - 循环依赖！
    return f"B_based_on_{a_value}"

@use_generators(a=generate_a, b=generate_b)
def test_will_fail(a, b):  # 这个测试将失败，因为存在循环依赖
    pass
```

#### 缺失参数错误

如果参数生成器需要的参数在测试环境中不可用，插件会抛出 `MissingParameterError` 并提供详细的错误信息。

#### 执行错误

如果参数生成器执行过程中发生异常，插件会抛出 `ExecutionError` 并包含原始异常信息和调用上下文。

## 装饰器2：`@use_generators` 装饰器

### 基本功能

`@use_generators` 装饰器用于将参数生成器与测试函数关联起来，支持多个动态参数。它会自动解析生成器之间的依赖关系，并按正确的顺序执行生成器。

### 基本用法

```python
from dynamic_params import generator, use_generators

@generator
def calculate_result(input_value):
    return input_value * 2

@use_generators(result=calculate_result)
def test_basic(input_value, result):
    assert result == input_value * 2
```

### 高级用法

#### 多个动态参数

```python
def apply_algorithm(item, algorithm):
    """应用算法处理数据"""
    if algorithm == "algo1":
        return {**item, "processed": item["id"] * 2}
    else:
        return {**item, "processed": item["id"] * 3}

@generator
def get_raw_data(data_source, size):
    """获取原始数据"""
    return [{"id": i, "source": data_source} for i in range(size)]

@generator
def process_data(raw_data, algorithm):
    """处理原始数据"""
    return [apply_algorithm(item, algorithm) for item in raw_data]

@use_generators(
    raw_data=get_raw_data,
    processed_data=process_data
)
@pytest.mark.parametrize("data_source", ["api", "database"])
@pytest.mark.parametrize("size", [5, 10])
@pytest.mark.parametrize("algorithm", ["algo1", "algo2"])
def test_multiple_use_generators(
    data_source, size, algorithm,
    raw_data, processed_data
):
    assert len(raw_data) == size
    assert len(processed_data) == size
```

#### 与fixture混合使用

##### 1. Generator中使用Fixture

```python
@pytest.fixture
def database():
    # 数据库连接逻辑
    return {"users": {"admin": {"type": "admin"}, "user": {"type": "user"}}}

@generator
def get_user_data(database, user_type):
    """获取用户数据"""
    return database["users"].get(user_type, {"type": "unknown"})

@use_generators(user_data=get_user_data)
@pytest.mark.parametrize("user_type", ["admin", "user"])
def test_with_fixture(database, user_type, user_data):
    assert user_data["type"] == user_type
```

##### 2. Fixture中使用Generator

```python
from dynamic_params import generator, use_generators
import pytest

@pytest.fixture
def base_config():
    return {"base": "config"}

@generator
def generate_env_config(base_config, environment):
    # 动态生成依赖其他fixture的fixture值
    return {**base_config, "env": environment}

# 可以将动态参数用作其他测试的fixture
@pytest.fixture
def env_config(generate_env_config):
    return generate_env_config

@use_generators(env_config=generate_env_config)
@pytest.mark.parametrize("environment", ["dev", "test", "prod"])
def test_fixture_parameterization(environment, env_config):
    assert env_config["env"] == environment
    assert env_config["base"] == "config"

# 在其他测试中使用env_config fixture
def test_using_parametrized_fixture(env_config):
    assert "env" in env_config
    assert "base" in env_config
```

#### 与 `@dynamic_parametrize` 结合使用

##### 1. 基本结合使用

```python
from dynamic_params import generator, use_generators, dynamic_parametrize, DynRef

@pytest.fixture
def base_config():
    return {"base": "config"}

@generator
def generate_env_config(base_config, environment):
    """生成环境配置"""
    return {**base_config, "env": environment}

@use_generators(env_config=generate_env_config)
@dynamic_parametrize(
    "environment, expected_env",
    [
        ("dev", "dev"),
        ("test", "test"),
        ("prod", "prod")
    ]
)
def test_combined_decorators(environment, expected_env, env_config):
    assert env_config["env"] == expected_env
    assert env_config["base"] == "config"
```

##### 2. 与 DynRef 结合的高级示例

```python
from dynamic_params import generator, use_generators, dynamic_parametrize, DynRef

@pytest.fixture
def api_url():
    return "http://api.example.com"

@pytest.fixture
def default_method():
    return "GET"

@generator
def generate_endpoint(api_url, resource, method):
    """生成API端点"""
    return f"{api_url}/{resource}", method

@use_generators(endpoint_and_method=generate_endpoint)
@dynamic_parametrize(
    "resource, method",
    [
        ("users", DynRef("default_method")),
        ("products", "POST"),
        ("orders", "PUT")
    ]
)
def test_api_endpoints(resource, method, endpoint_and_method, api_url):
    endpoint, used_method = endpoint_and_method
    assert endpoint == f"{api_url}/{resource}"
    assert used_method == method
    assert method in ["GET", "POST", "PUT"]
```

## 装饰器3：`@dynamic_parametrize` 装饰器

### 基本功能

`@dynamic_parametrize` 装饰器用于参数化测试函数，类似于 pytest 的 `@pytest.mark.parametrize`，但支持动态解析参数值和引用 fixture。

### 基本用法

```python
from dynamic_params import dynamic_parametrize

@dynamic_parametrize(
    "input_value, expected_result",
    [
        (1, 1),
        (2, 2),
        (3, 3)
    ]
)
def test_basic_dynamic_parametrize(input_value, expected_result):
    assert input_value == expected_result
```

### 高级用法

#### 与 `DynRef` 结合使用

```python
from dynamic_params import dynamic_parametrize, DynRef

@pytest.fixture
def base_value():
    return 10

@dynamic_parametrize(
    "param1, param2",
    [
        (1, 2),
        (DynRef("base_value"), DynRef("base_value"))
    ]
)
def test_with_dynref(param1, param2):
    assert isinstance(param1, (int, float))
    assert isinstance(param2, (int, float))
```

#### 与其他装饰器结合

```python
@dynamic_parametrize(
    "input_value",
    [1, 2, 3]
)
@pytest.mark.parametrize("multiplier", [2, 3])
def test_combined_parametrize(input_value, multiplier):
    assert input_value * multiplier > 0
```

## 配置

### 配置文件配置

可以在 `pytest.ini` 中配置插件行为：

```ini
[pytest.dynamic_params]
# 系统配置
cache_enabled = true
validation = strict
log_level = INFO

# 缓存大小配置
cache_size_function = 1000
cache_size_class = 500
cache_size_module = 200
cache_size_session = 100

# 性能配置
lazy_loading = true
incremental_generation = true

# 测试标记
markers =
    use_generators: 使用动态参数的测试
    generator: 参数生成器函数
```

## 最佳实践

1. **保持生成器函数纯净**：生成器函数应该只负责生成参数值，不要有副作用。
2. **合理使用作用域**：根据测试需求选择合适的作用域，避免不必要的重复计算。
3. **明确依赖关系**：确保生成器函数的参数签名清晰地表达依赖关系。
4. **启用缓存**：对于计算密集型的参数生成，启用缓存可以显著提高性能。
5. **使用懒加载**：对于可能不被使用的参数，启用懒加载可以避免不必要的计算。
6. **使用有意义的参数名**：使用描述性的参数名有助于理解测试逻辑。
7. **控制依赖复杂度**：避免过于复杂的依赖链，保持依赖关系清晰。
8. **合理使用 `DynRef`**：只在需要引用其他参数或 fixture 时使用 `DynRef`。
9. **与其他装饰器结合**：可以与 `@pytest.mark.parametrize` 等装饰器结合使用。

## 常见问题

### 为什么我的参数生成器没有被执行？

确保：

1. 使用了 `@generator` 装饰器
2. 在测试函数上使用了 `@use_generators` 装饰器
3. 参数名在两个装饰器之间保持一致
4. 依赖的参数在测试环境中可用

### 如何调试参数生成问题？

启用详细日志记录：

```bash
python -m pytest -v -s --log-cli-level=DEBUG
```

### 如何处理循环依赖？

重构参数生成器，消除循环依赖关系。可以：

1. 合并相关的生成器函数
2. 提取共享逻辑到单独的函数
3. 重新设计参数依赖结构

## 性能建议

1. **懒加载**：启用懒加载功能可以避免不必要的参数生成
2. **缓存**：对计算密集型的生成器启用缓存
3. **作用域**：根据测试需求合理选择作用域，避免过度重复计算
4. **依赖解析**：简化参数生成器之间的依赖关系，避免过于复杂的依赖链
5. **批量生成**：对于相关参数，考虑在一个生成器中批量生成，减少依赖解析开销
6. **合理配置**：根据测试环境和需求调整缓存大小和其他配置参数

## 测试执行命令

运行完整的测试套件：

```bash
python -m pytest tests/ --alluredir=reports/allure-results -clean --cov=src.dynamic_params --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml --cov-report=term
```

查看Allure报告：

```bash
allure serve reports/allure-results
```