# pytest-dynamic-params 使用指南

## 概述

`pytest-dynamic-params` 是一个用于pytest的动态参数化插件，允许测试开发者声明式地定义参数生成器，系统自动处理参数收集、依赖解析、动态参数生成和测试用例参数化。

## 安装

```bash
pip install -e .
```

## 核心概念

### 1. 参数生成器 (`@param_generator`)
使用 `@param_generator` 装饰器定义的函数，用于动态生成参数值。

### 2. 动态参数装饰器 (`@with_dynamic_params`)
使用 `@with_dynamic_params` 装饰器将参数生成器与测试函数关联起来。

### 3. 作用域管理
支持四种作用域：`function`（默认）、`class`、`module`、`session`。

### 4. 依赖解析
系统自动分析生成器函数的参数签名，确定依赖关系并按正确顺序执行。

## 基础用法

### 简单参数生成

```python
from dynamic_params import param_generator, with_dynamic_params

@param_generator
def calculate_result(input_value):
    return input_value * 2

@with_dynamic_params(result=calculate_result)
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

@with_dynamic_params(user_data=get_user_data)
@pytest.mark.parametrize("user_type", ["admin", "user"])
def test_with_fixture(database, user_type, user_data):
    assert user_data["type"] == user_type
```

### 参数化fixture支持

```python
@pytest.fixture(params=["dev", "test", "prod"])
def environment(request):
    return {"env": request.param, "timeout": 30}

@param_generator
def generate_config(environment, feature_flag):
    return {
        "env": environment["env"],
        "feature": feature_flag,
        "timeout": environment["timeout"] + 10
    }

@with_dynamic_params(config=generate_config)
@pytest.mark.parametrize("feature_flag", ["A/B", "control"])
def test_parametrized_fixture(environment, feature_flag, config):
    assert config["env"] == environment["env"]
    assert config["feature"] == feature_flag
    assert config["timeout"] == environment["timeout"] + 10
```

## 高级用法

### 多个动态参数

```python
@param_generator
def get_raw_data(data_source, size):
    return [{"id": i, "source": data_source} for i in range(size)]

@param_generator
def process_data(raw_data, algorithm):
    return [apply_algorithm(item, algorithm) for item in raw_data]

@with_dynamic_params(
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

@with_dynamic_params(a=generate_a, b=generate_b)
def test_will_fail(a, b):  # 这个测试将失败，因为存在循环依赖
    pass
```

### 缺失参数错误

如果参数生成器需要的参数在测试环境中不可用，插件会抛出 `MissingParameterError` 并提供详细的错误信息。

## 配置

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

## 最佳实践

1. **保持生成器函数纯净**：生成器函数应该只负责生成参数值，不要有副作用。
2. **合理使用作用域**：根据测试需求选择合适的作用域，避免不必要的重复计算。
3. **明确依赖关系**：确保生成器函数的参数签名清晰地表达依赖关系。
4. **启用缓存**：对于计算密集型的参数生成，启用缓存可以显著提高性能。
5. **使用有意义的参数名**：使用描述性的参数名有助于理解测试逻辑。

## 常见问题

### 为什么我的参数生成器没有被执行？

确保：
1. 使用了 `@param_generator` 装饰器
2. 在测试函数上使用了 `@with_dynamic_params` 装饰器
3. 参数名在两个装饰器之间保持一致

### 如何调试参数生成问题？

启用详细日志记录：
```bash
python -m pytest -v -s --log-cli-level=DEBUG
```

## 性能建议

1. **懒加载**：启用懒加载功能可以避免不必要的参数生成
2. **缓存**：对计算密集型的生成器启用缓存
3. **作用域**：根据测试需求合理选择作用域，避免过度重复计算
4. **依赖解析**：简化参数生成器之间的依赖关系，避免过于复杂的依赖链