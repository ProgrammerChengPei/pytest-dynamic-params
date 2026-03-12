# pytest-dynamic-params

![CI](https://github.com/ProgrammerChengPei/pytest-dynamic-params/workflows/CI/badge.svg)
![Coverage](https://codecov.io/gh/ProgrammerChengPei/pytest-dynamic-params/branch/main/graph/badge.svg)
![Version](https://img.shields.io/pypi/v/pytest-dynamic-params.svg)
![Downloads](https://img.shields.io/pypi/dm/pytest-dynamic-params.svg)
![Python](https://img.shields.io/pypi/pyversions/pytest-dynamic-params.svg)
![License](https://img.shields.io/pypi/l/pytest-dynamic-params.svg)

pytest-dynamic-params 是一个为 pytest 设计的动态参数化插件，解决了传统 pytest 参数化中的核心问题：

- **参数化时机冲突**：传统 `@pytest.mark.parametrize` 在模块导入阶段执行，而 fixture 在测试运行阶段才实例化
- **动态数据生成困难**：无法在装饰器参数中调用依赖 fixture 的函数
- **复杂的参数组合**：需要手动编写钩子函数处理参数收集、组合和动态生成
- **依赖管理缺失**：无法自动处理参数间的依赖关系，需要手动排序

通过声明式参数生成器自动处理依赖解析和参数化，支持懒加载、缓存机制和多作用域管理，与现有 pytest 机制无缝集成，简化复杂测试场景的参数管理，提高测试效率和可维护性。

## 特性

- **声明式参数生成**：使用装饰器定义参数生成器，专注于"生成什么"而非"如何生成"
- **自动依赖管理**：系统自动分析生成器函数的参数签名，确定依赖关系并按正确顺序执行
- **与现有机制兼容**：完全兼容现有的pytest机制，包括`@pytest.mark.parametrize`装饰器和fixture系统
- **性能优化**：支持懒加载和缓存机制，提高测试执行效率
- **灵活的作用域管理**：支持function、class、module、session四种作用域
- **智能错误检测**：自动检测并报告参数生成器之间的循环依赖
- **可配置性**：支持多种配置选项，满足不同场景需求

## 安装

```bash
pip install -e .
```

## 快速开始

安装后，您可以立即在测试中使用动态参数装饰器：

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

## 核心概念

- **参数生成器**：使用`@param_generator`装饰器定义的函数，用于生成参数值
- **动态参数**：在运行时生成的参数，可以依赖其他参数或fixture
- **参数依赖**：参数之间的依赖关系，系统自动按依赖顺序生成参数
- **懒加载**：推迟参数生成到实际需要时执行，避免不必要的计算
- **缓存机制**：缓存参数生成结果，避免重复计算，提高性能
- **作用域管理**：控制参数生成器实例的生命周期，影响缓存和执行时机

## 如何解决核心问题

### 1. 解决参数化时机冲突

传统 pytest 中，`@pytest.mark.parametrize` 在模块导入阶段执行，而 fixture 在测试运行阶段才实例化，导致无法在参数化中使用 fixture 的值。

**解决方案**：
```python
from dynamic_params import param_generator, dynamic_params
import pytest

@pytest.fixture
def environment():
    return "production"

@param_generator
def generate_config(environment):
    # 这里可以使用 fixture 的值，因为 generate_config 在测试运行阶段执行
    return {"env": environment, "timeout": 30}

@dynamic_params(config=generate_config)
def test_with_fixture_dependency(environment, config):
    assert config["env"] == environment
    assert config["timeout"] == 30
```

### 2. 解决动态数据生成困难

传统 pytest 中，无法在装饰器参数中调用依赖 fixture 的函数，限制了动态数据生成的能力。

**解决方案**：
```python
from dynamic_params import param_generator, dynamic_params
import pytest

@pytest.fixture
def database():
    return {"users": [1, 2, 3], "prefix": "User_"}

@param_generator
def get_user_data(database, user_id):
    # 这里可以动态生成依赖 fixture 的数据
    return {"id": user_id, "name": f"{database['prefix']}{user_id}"}

@dynamic_params(user_data=get_user_data)
@pytest.mark.parametrize("user_id", [1, 2, 3])
def test_dynamic_data_generation(database, user_id, user_data):
    assert user_data["id"] == user_id
    assert user_data["name"] == f"{database['prefix']}{user_id}"
    assert user_id in database["users"]
```

### 3. 解决复杂的参数组合

传统 pytest 中，需要手动编写钩子函数处理参数收集、组合和动态生成，代码复杂度高。

**解决方案**：
```python
from dynamic_params import param_generator, dynamic_params
import pytest

@param_generator
def generate_base_config():
    return {"base": "config"}

@param_generator
def generate_env_config(base_config, environment):
    return {**base_config, "env": environment}

@param_generator
def generate_full_config(env_config, feature_flag):
    return {**env_config, "feature": feature_flag}

@dynamic_params(
    base_config=generate_base_config,
    env_config=generate_env_config,
    full_config=generate_full_config
)
@pytest.mark.parametrize("environment", ["dev", "test", "prod"])
@pytest.mark.parametrize("feature_flag", [True, False])
def test_complex_parameter_combinations(
    environment, feature_flag, base_config, env_config, full_config
):
    assert base_config["base"] == "config"
    assert env_config["env"] == environment
    assert full_config["feature"] == feature_flag
```

### 4. 解决依赖管理缺失

传统 pytest 中，无法自动处理参数间的依赖关系，需要手动排序，容易出错。

**解决方案**：
```python
from dynamic_params import param_generator, dynamic_params

@param_generator
def generate_a():
    return "value_a"

@param_generator
def generate_b(a):  # 依赖 generate_a 的结果
    return f"b_from_{a}"

@param_generator
def generate_c(b):  # 依赖 generate_b 的结果
    return f"c_from_{b}"

@dynamic_params(a=generate_a, b=generate_b, c=generate_c)
def test_automatic_dependency_management(a, b, c):
    assert a == "value_a"
    assert b == "b_from_value_a"
    assert c == "c_from_b_from_value_a"
```

系统会自动分析参数生成器的依赖关系，并按正确的顺序执行它们，无需手动排序。

## 使用示例

完整的使用示例请参见：
- `examples/basic_usage.py` - 基础用法示例（可直接复制使用）
- `examples/advanced_usage.py` - 高级用法示例（包含作用域、缓存和懒加载）
- `docs/usage-guide.md` - 详细使用指南

## 配置

可以在`pytest.ini`中配置插件行为：

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

也可以通过环境变量配置：
- `PYTEST_DYNAMIC_PARAM_CACHE`: 控制缓存是否启用
- `PYTEST_DYNAMIC_PARAM_VALIDATION`: 验证级别
- `PYTEST_DYNAMIC_PARAM_LOG_LEVEL`: 日志级别
- `PYTEST_DYNAMIC_PARAM_LAZY_LOADING`: 懒加载设置
- `PYTEST_DYNAMIC_PARAM_INCREMENTAL`: 增量生成设置
- `PYTEST_DYNAMIC_PARAM_DEBUG`: 调试模式
- `PYTEST_DYNAMIC_PARAM_PROFILE`: 性能分析
- `PYTEST_DYNAMIC_PARAM_CACHE_DIR`: 缓存目录

## 项目结构

项目的主要组成部分：

- `src/` - 源代码
- `tests/` - 测试代码
- `examples/` - 使用示例
- `docs/` - 文档
- `specs/` - 项目规格说明
- `reports/` - 测试报告

有关详细的源码架构说明，请参见 [docs/structure.md](./docs/structure.md)。

## 运行测试

```bash
# 运行单元测试
python -m pytest tests/unit/

# 运行功能测试
python -m pytest tests/functional/

# 运行集成测试
python -m pytest tests/integration/

# 运行性能测试
python -m pytest tests/performance/

# 运行所有测试
python -m pytest tests/

# 查看覆盖率
python -m pytest --cov=src.dynamic_params tests/unit/ --cov-report=html

# 生成完整报告（Allure + 覆盖率）
python -m pytest tests/ --alluredir=reports/allure-results -clean --cov=src.dynamic_params --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml --cov-report=term

# 查看Allure报告
allure serve reports/allure-results
```

## 测试报告

有关测试报告的详细说明，请参见：
- [docs/reports-readme.md](./docs/reports-readme.md) - 报告使用说明
- [docs/reports-summary.md](./docs/reports-summary.md) - 测试结果和覆盖率摘要

生成的报告位于 `reports/` 目录：
- Allure报告：`reports/allure-results`（可通过 `allure serve` 查看）
- 覆盖率HTML报告：`reports/coverage-html/index.html`
- 覆盖率XML报告：`reports/coverage.xml`

## 许可证

MIT