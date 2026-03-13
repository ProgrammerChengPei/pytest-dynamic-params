# pytest-dynamic-params 使用指南

## 概述

`pytest-dynamic-params` 是一个用于pytest的动态参数化插件，允许测试开发者声明式地定义参数生成器，系统自动处理参数收集、依赖解析、动态参数生成和测试用例参数化。

## 安装

```bash
pip install -e .
```

## 核心概念

### 1. 参数生成器 (`@param_generator`)
使用 `@param_generator` 装饰器定义的函数，用于动态生成参数值。支持配置作用域、缓存和懒加载。

### 2. 动态参数装饰器 (`@dynamic_params`)
使用 `@dynamic_params` 装饰器将参数生成器与测试函数关联起来，支持多个动态参数。

### 3. 作用域管理
支持四种作用域：`function`（默认）、`class`、`module`、`session`，控制参数生成的生命周期。

### 4. 依赖解析
系统自动分析生成器函数的参数签名，确定依赖关系并按正确顺序执行，支持复杂的依赖链。

### 5. 懒加载
通过 `lazy` 参数控制是否启用懒加载，避免不必要的参数生成，提高性能。

### 6. 缓存机制
通过 `cache` 参数控制是否启用缓存，对于计算密集型的参数生成可以显著提高性能。

## 基础用法

### 简单参数生成

```python
from dynamic_params import param_generator, dynamic_params

@param_generator
def calculate_result(input_value):
    return input_value * 2

@dynamic_params(result=calculate_result)
@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_basic(input_value, result):
    assert result == input_value * 2
```

### 与fixture混合使用

```python
@pytest.fixture
def database():
    # 数据库连接逻辑
    return {"users": {"admin": {"type": "admin"}, "user": {"type": "user"}}}

@param_generator
def get_user_data(database, user_type):
    return database["users"].get(user_type, {"type": "unknown"})

@dynamic_params(user_data=get_user_data)
@pytest.mark.parametrize("user_type", ["admin", "user"])
def test_with_fixture(database, user_type, user_data):
    assert user_data["type"] == user_type
```

## fixture参数化

### 概述

`pytest-dynamic-params` 支持通过参数生成器动态生成fixture值，实现fixture的参数化。这是该插件的一个核心特性，允许fixture值根据其他fixture或参数动态生成。

### 基本用法

```python
from dynamic_params import param_generator, dynamic_params
import pytest

@pytest.fixture
def base_config():
    return {"base": "config"}

@param_generator
def generate_env_config(base_config, environment):
    # 动态生成依赖其他fixture的fixture值
    return {**base_config, "env": environment}

# 可以将动态参数用作其他测试的fixture
@pytest.fixture
def env_config(generate_env_config):
    return generate_env_config

@dynamic_params(env_config=generate_env_config)
@pytest.mark.parametrize("environment", ["dev", "test", "prod"])
def test_fixture_parameterization(environment, env_config):
    assert env_config["env"] == environment
    assert env_config["base"] == "config"

# 在其他测试中使用env_config fixture
def test_using_parametrized_fixture(env_config):
    assert "env" in env_config
    assert "base" in env_config
```

### 高级用法

#### 1. 多层fixture依赖

```python
@pytest.fixture
def db_connection():
    # 模拟数据库连接
    return {"host": "localhost", "port": 5432}

@param_generator
def generate_user_data(db_connection, user_id):
    # 从数据库获取用户数据
    return {
        "id": user_id,
        "name": f"User_{user_id}",
        "db": db_connection
    }

@param_generator
def generate_user_profile(user_data, role):
    # 基于用户数据生成用户配置文件
    return {
        **user_data,
        "role": role,
        "permissions": get_permissions(role)
    }

@dynamic_params(
    user_data=generate_user_data,
    user_profile=generate_user_profile
)
@pytest.mark.parametrize("user_id", [1, 2, 3])
@pytest.mark.parametrize("role", ["admin", "user"])
def test_multilevel_fixture_dependencies(
    db_connection, user_id, role, user_data, user_profile
):
    assert user_data["id"] == user_id
    assert user_profile["role"] == role
    assert user_profile["permissions"] == get_permissions(role)
```

#### 2. 作用域控制

```python
@param_generator(scope="module")
def module_scoped_config():
    # 模块级别的配置，只生成一次
    return {"module": "config"}

@pytest.fixture(scope="module")
def shared_config(module_scoped_config):
    return module_scoped_config

@dynamic_params(shared_config=module_scoped_config)
def test_shared_config(shared_config):
    assert "module" in shared_config

# 这个测试将使用相同的shared_config值
def test_another_shared_config(shared_config):
    assert "module" in shared_config
```

#### 3. 与传统fixture混合使用

```python
@pytest.fixture
def static_fixture():
    return "static_value"

@param_generator
def dynamic_fixture(static_fixture, dynamic_input):
    return f"{static_fixture}_{dynamic_input}"

@pytest.fixture
def combined_fixture(dynamic_fixture):
    return f"combined_{dynamic_fixture}"

@dynamic_params(dynamic_fixture=dynamic_fixture)
@pytest.mark.parametrize("dynamic_input", ["a", "b", "c"])
def test_combined_fixtures(static_fixture, dynamic_input, dynamic_fixture, combined_fixture):
    assert dynamic_fixture == f"{static_fixture}_{dynamic_input}"
    assert combined_fixture == f"combined_{dynamic_fixture}"
```

### 核心优势

1. **动态fixture生成**：fixture值可以根据其他fixture或参数动态生成，而不仅仅是静态值
2. **fixture复用**：参数化的fixture可以在多个测试中复用，提高代码可维护性
3. **依赖管理**：自动处理fixture之间的依赖关系，无需手动管理依赖顺序
4. **作用域控制**：支持与pytest fixture相同的作用域管理，灵活控制fixture的生命周期
5. **性能优化**：支持缓存和懒加载，提高测试执行效率

### 常见用例

- **环境配置**：根据测试环境动态生成配置
- **数据准备**：根据测试参数动态准备测试数据
- **依赖服务**：根据测试需求动态配置依赖服务
- **复杂对象**：动态构建复杂的测试对象
- **配置组合**：根据不同参数组合生成不同的配置

## 高级用法

### 多个动态参数

```python
@param_generator
def get_raw_data(data_source, size):
    return [{"id": i, "source": data_source} for i in range(size)]

@param_generator
def process_data(raw_data, algorithm):
    return [apply_algorithm(item, algorithm) for item in raw_data]

@dynamic_params(
    raw_data=get_raw_data,
    processed_data=process_data
)
@pytest.mark.parametrize("data_source", ["api", "database"])
@pytest.mark.parametrize("size", [5, 10])
@pytest.mark.parametrize("algorithm", ["algo1", "algo2"])
def test_multiple_dynamic_params(
    data_source, size, algorithm,
    raw_data, processed_data
):
    assert len(raw_data) == size
    assert len(processed_data) == size
```

### 作用域控制

```python
@param_generator(scope="function")  # 每个测试函数重新生成
def function_scoped_data():
    return random.randint(1, 100)

@param_generator(scope="class")     # 每个测试类共享
def class_scoped_data():
    return "shared among class"

@param_generator(scope="module")    # 每个模块共享
def module_scoped_data():
    return "shared among module"

@param_generator(scope="session")   # 整个测试会话共享
def session_scoped_data():
    return "shared across session"
```

### 缓存控制

```python
@param_generator(cache=True)  # 启用缓存（默认）
def cached_data(input_value):
    # 计算密集型操作
    return expensive_computation(input_value)

@param_generator(cache=False)  # 禁用缓存
def uncached_data():
    return time.time()  # 每次调用返回不同值
```

### 懒加载控制

```python
@param_generator(lazy=True)  # 启用懒加载（默认）
def lazy_data(input_value):
    # 只有在实际使用时才会执行
    return compute_expensive_value(input_value)

@param_generator(lazy=False)  # 禁用懒加载
def eager_data(input_value):
    # 会立即执行，不管是否使用
    return compute_expensive_value(input_value)
```

## 错误处理

### 循环依赖检测

```python
# 这将触发循环依赖错误
@param_generator
def generate_a(b_value):  # 依赖于b
    return f"A_based_on_{b_value}"

@param_generator 
def generate_b(a_value):  # 依赖于a - 循环依赖！
    return f"B_based_on_{a_value}"

@dynamic_params(a=generate_a, b=generate_b)
def test_will_fail(a, b):  # 这个测试将失败，因为存在循环依赖
    pass
```

### 缺失参数错误

如果参数生成器需要的参数在测试环境中不可用，插件会抛出 `MissingParameterError` 并提供详细的错误信息。

### 执行错误

如果参数生成器执行过程中发生异常，插件会抛出 `ExecutionError` 并包含原始异常信息和调用上下文。

## 配置

### 配置文件配置

可以在 `pytest.ini` 中配置插件行为：

```ini
[pytest]
# 动态参数化系统配置
dynamic_param_cache_enabled = true
dynamic_param_validation = strict
dynamic_param_log_level = INFO

# 缓存大小配置
dynamic_param_cache_size_function = 1000
dynamic_param_cache_size_class = 500
dynamic_param_cache_size_module = 200
dynamic_param_cache_size_session = 100

# 性能配置
dynamic_param_lazy_loading = true
dynamic_param_incremental_generation = true

# 测试标记
markers =
    dynamic_param: 使用动态参数的测试
    param_generator: 参数生成器函数
```

### 环境变量配置

也可以通过环境变量配置插件行为：

- `PYTEST_DYNAMIC_PARAM_CACHE`: 控制缓存是否启用
- `PYTEST_DYNAMIC_PARAM_VALIDATION`: 验证级别
- `PYTEST_DYNAMIC_PARAM_LOG_LEVEL`: 日志级别
- `PYTEST_DYNAMIC_PARAM_LAZY_LOADING`: 懒加载设置
- `PYTEST_DYNAMIC_PARAM_INCREMENTAL`: 增量生成设置
- `PYTEST_DYNAMIC_PARAM_DEBUG`: 调试模式
- `PYTEST_DYNAMIC_PARAM_PROFILE`: 性能分析
- `PYTEST_DYNAMIC_PARAM_CACHE_DIR`: 缓存目录

## 最佳实践

1. **保持生成器函数纯净**：生成器函数应该只负责生成参数值，不要有副作用。
2. **合理使用作用域**：根据测试需求选择合适的作用域，避免不必要的重复计算。
3. **明确依赖关系**：确保生成器函数的参数签名清晰地表达依赖关系。
4. **启用缓存**：对于计算密集型的参数生成，启用缓存可以显著提高性能。
5. **使用懒加载**：对于可能不被使用的参数，启用懒加载可以避免不必要的计算。
6. **使用有意义的参数名**：使用描述性的参数名有助于理解测试逻辑。
7. **控制依赖复杂度**：避免过于复杂的依赖链，保持依赖关系清晰。

## 常见问题

### 为什么我的参数生成器没有被执行？

确保：
1. 使用了 `@param_generator` 装饰器
2. 在测试函数上使用了 `@dynamic_params` 装饰器
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