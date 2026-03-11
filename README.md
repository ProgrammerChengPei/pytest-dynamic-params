# pytest-dynamic-params

一个用于pytest的动态参数化插件，允许测试开发者声明式地定义参数生成器，系统自动处理参数收集、依赖解析、动态参数生成和测试用例参数化。

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
from dynamic_params import param_generator, with_dynamic_params

@param_generator
def calculate_result(input_value):
    return input_value * 2

@with_dynamic_params(result=calculate_result)
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