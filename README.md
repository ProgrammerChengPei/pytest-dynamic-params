# pytest-dynamic-params

![CI](https://github.com/ProgrammerChengPei/pytest-dynamic-params/workflows/Code%20Quality/badge.svg)

![Coverage](https://codecov.io/gh/ProgrammerChengPei/pytest-dynamic-params/branch/main/graph/badge.svg)

![Version](https://img.shields.io/pypi/v/pytest-dynamic-params.svg)

![Downloads](https://img.shields.io/pypi/dm/pytest-dynamic-params.svg)

![Python](https://img.shields.io/pypi/pyversions/pytest-dynamic-params.svg)

![License](https://img.shields.io/pypi/l/pytest-dynamic-params.svg)

一个革命性的 pytest 动态参数化插件，彻底突破传统 pytest 参数化的局限性，为复杂测试场景提供更强大、更灵活、更高效的参数管理解决方案。

## 目录

- [特性](#特性)
- [安装](#安装)
- [快速上手](#快速上手)
- [核心概念](#核心概念)
- [使用示例](#使用示例)
- [高级用法](#高级用法)
- [配置](#配置)
- [项目结构](#项目结构)
- [运行测试](#运行测试)
- [贡献](#贡献)
- [许可证](#许可证)

## 特性

- **声明式参数生成**：使用装饰器定义参数生成器，专注于"生成什么"而非"如何生成"，简化参数生成逻辑
- **动态参数化**：使用`@dynamic_parametrize`装饰器替代`@pytest.mark.parametrize`，解决传统静态参数无法支持所有嵌套关系的问题
- **动态引用**：使用`DynRef`类在参数化中直接引用其他参数和fixture，简化复杂参数依赖
- **自动依赖管理**：系统自动分析生成器函数的参数签名，智能识别依赖关系并按正确顺序执行，无需手动排序
- **高级 fixture 参数化**：支持通过参数生成器动态生成 fixture 值，实现更灵活的 fixture 参数化和依赖管理
- **全面支持嵌套关系**：支持静态参数、动态参数、静态fixture、动态fixture之间的各种嵌套调用关系
- **灵活的作用域管理**：支持function、class、module、session四种作用域，更灵活地控制参数生成时机和生命周期
- **性能优化**：内置懒加载和缓存机制，避免重复计算，大幅提升测试执行效率
- **智能错误检测**：自动检测并报告参数生成器之间的循环依赖，提前发现并解决问题
- **可配置性**：支持多种配置选项，包括缓存设置、懒加载、日志级别等，适应不同场景需求
- **无缝集成**：完全兼容现有的pytest机制，包括`@pytest.mark.parametrize`装饰器和fixture系统，无需修改现有测试代码

## 安装

### 从 PyPI 安装

```bash
pip install pytest-dynamic-params
```

### 从源码安装（开发模式）

如果您需要从源码安装并进行开发，可以使用以下命令：

```bash
pip install -e .
```

## 快速上手

```python
from dynamic_params import generator, use_generators
import pytest

@generator
def calculate_result(input_value):
    return input_value * 2

@use_generators(result=calculate_result)
@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_basic(input_value, result):
    assert result == input_value * 2
```

## 核心概念

### 1. 参数生成器 (`@generator`)
使用 `@generator` 装饰器定义的函数，用于动态生成参数值。支持配置作用域、缓存和懒加载。

### 2. 生成器使用装饰器 (`@use_generators`)
`@use_generators` 用于将参数生成器与测试函数关联起来，支持多个动态参数。

### 3. 动态参数化装饰器 (`@dynamic_parametrize`)
`@dynamic_parametrize` 是对 `@pytest.mark.parametrize` 的增强，支持在参数值中引用其他参数和fixture。

### 4. 动态引用 (`DynRef`)
`DynRef` 类用于在 `@dynamic_parametrize` 中引用其他参数或fixture的值。

### 5. 作用域管理
支持四种作用域：`function`（默认）、`class`、`module`、`session`，控制参数生成的生命周期。

### 6. 依赖解析
系统自动分析生成器函数的参数签名，确定依赖关系并按正确顺序执行，支持复杂的依赖链。

### 7. 懒加载
通过 `lazy` 参数控制是否启用懒加载，避免不必要的参数生成，提高性能。

### 8. 缓存机制
通过 `cache` 参数控制是否启用缓存，对于计算密集型的参数生成可以显著提高性能。

## 使用示例

### 1. 动态数据生成

参数生成器在测试运行阶段执行，完全支持使用 fixture 值，实现真正的动态数据生成。

```python
from dynamic_params import generator, use_generators
import pytest

@pytest.fixture
def environment():
    return "production"

@generator
def generate_config(environment):
    # 这里可以使用 fixture 的值，因为 generate_config 在测试运行阶段执行
    return {"env": environment, "timeout": 30}

@use_generators(config=generate_config)
def test_with_fixture_dependency(environment, config):
    assert config["env"] == environment
    assert config["timeout"] == 30
```

### 2. 复杂参数引用

使用 `@dynamic_parametrize` 和 `DynRef` 实现参数间的动态引用，支持在参数值中引用其他参数或 fixture，提供更灵活的参数化能力。

```python
from dynamic_params import dynamic_parametrize, DynRef
import pytest

@pytest.fixture
def base_value():
    return 10

@dynamic_parametrize(
    "value, expected",
    [
        (1, 11),
        (2, DynRef("base_value"))  # 引用 fixture
    ]
)
def test_dynamic_parametrize_with_ref(value, expected, base_value):
    assert value + base_value == expected

# 引用其他参数
@dynamic_parametrize(
    "a, b, result",
    [
        (1, 2, 3),
        (4, 5, DynRef("a"))  # 引用参数 a
    ]
)
def test_dynamic_parametrize_with_param_ref(a, b, result):
    assert a + b == result
```

### 3. 复杂参数组合

声明式装饰器自动处理参数组合，特别是动态参数与fixture的复杂依赖关系，简化参数管理，减少代码复杂度。

```python
from dynamic_params import generator, use_generators
import pytest

@generator
def generate_base_config():
    return {"base": "config"}

@generator
def generate_env_config(base_config, environment):
    return {**base_config, "env": environment}

@generator
def generate_full_config(env_config, feature_flag):
    return {**env_config, "feature": feature_flag}

# Fixture 中使用动态参数
@pytest.fixture
def app_config(generate_full_config):
    # 直接使用动态参数作为 fixture
    return generate_full_config

@use_generators(
    base_config=generate_base_config,
    env_config=generate_env_config,
    full_config=generate_full_config
)
@pytest.mark.parametrize("environment", ["dev", "test", "prod"])
@pytest.mark.parametrize("feature_flag", [True, False])
def test_complex_parameter_combinations(
    environment, feature_flag, base_config, env_config, full_config, app_config
):
    assert base_config["base"] == "config"
    assert env_config["env"] == environment
    assert full_config["feature"] == feature_flag
    # 验证 fixture 中使用动态参数
    assert app_config == full_config
```

### 4. 使用 dynamic_parametrize 引用参数生成器

```python
from dynamic_params import generator, use_generators, dynamic_parametrize, DynRef
import pytest

@generator
def calculate_result(input_value):
    return input_value * 2

@dynamic_parametrize(
    "input_value, expected",
    [
        (1, 2),
        (2, DynRef("result"))  # 引用参数生成器的结果
    ]
)
@use_generators(result=calculate_result)
def test_dynamic_parametrize_with_generator(input_value, expected, result):
    assert result == input_value * 2
    assert expected == result
```

## 高级用法

### 1. 多层fixture依赖

```python
from dynamic_params import generator, use_generators
import pytest

@pytest.fixture
def db_connection():
    # 模拟数据库连接
    return {"host": "localhost", "port": 5432}

@generator
def generate_user_data(db_connection, user_id):
    # 从数据库获取用户数据
    return {
        "id": user_id,
        "name": f"User_{user_id}",
        "db": db_connection
    }

@generator
def generate_user_profile(user_data, role):
    # 基于用户数据生成用户配置文件
    def get_permissions(role):
        if role == "admin":
            return ["read", "write", "delete"]
        return ["read"]
    
    return {
        **user_data,
        "role": role,
        "permissions": get_permissions(role)
    }

@use_generators(
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
    if role == "admin":
        assert user_profile["permissions"] == ["read", "write", "delete"]
    else:
        assert user_profile["permissions"] == ["read"]
```

### 2. 作用域管理

支持 function、class、module、session 四种作用域，更灵活地控制参数生成时机和生命周期，提高测试执行效率。

```python
from dynamic_params import generator, use_generators
import pytest

# 会话级作用域，整个测试会话只执行一次
@generator(scope="session")
def generate_session_data():
    print("Generating session data...")
    return {"session": "data"}

# 模块级作用域，每个模块执行一次
@generator(scope="module")
def generate_module_data():
    print("Generating module data...")
    return {"module": "data"}

# 类级作用域，每个测试类执行一次
@generator(scope="class")
def generate_class_data():
    print("Generating class data...")
    return {"class": "data"}

# 函数级作用域，每个测试函数执行一次
@generator(scope="function")
def generate_function_data():
    print("Generating function data...")
    return {"function": "data"}

class TestScope:
    @use_generators(
        session_data=generate_session_data,
        module_data=generate_module_data,
        class_data=generate_class_data,
        function_data=generate_function_data
    )
    def test_scope_1(self, session_data, module_data, class_data, function_data):
        assert session_data == {"session": "data"}
        assert module_data == {"module": "data"}
        assert class_data == {"class": "data"}
        assert function_data == {"function": "data"}

    @use_generators(
        session_data=generate_session_data,
        module_data=generate_module_data,
        class_data=generate_class_data,
        function_data=generate_function_data
    )
    def test_scope_2(self, session_data, module_data, class_data, function_data):
        assert session_data == {"session": "data"}
        assert module_data == {"module": "data"}
        assert class_data == {"class": "data"}
        assert function_data == {"function": "data"}
```

### 3. 性能优化（缓存与懒加载）

内置懒加载和缓存机制，避免重复计算，大幅提升测试执行效率，特别是对于复杂的参数生成逻辑。

```python
from dynamic_params import generator, use_generators
import time

# 启用缓存，避免重复计算
@generator(cache=True)
def generate_expensive_data(input_value):
    print(f"Generating expensive data for {input_value}...")
    time.sleep(0.1)  # 模拟耗时操作
    return input_value * 10

# 启用懒加载，推迟计算到实际需要时
@generator(lazy=True)
def generate_lazy_data(input_value):
    print(f"Generating lazy data for {input_value}...")
    time.sleep(0.1)  # 模拟耗时操作
    return input_value * 20

@use_generators(
    expensive_data=generate_expensive_data,
    lazy_data=generate_lazy_data
)
@pytest.mark.parametrize("input_value", [1, 1, 2, 2])
def test_performance_optimization(input_value, expensive_data, lazy_data):
    # 对于相同的 input_value，expensive_data 只会计算一次（缓存）
    # lazy_data 只有在实际使用时才会计算（懒加载）
    assert expensive_data == input_value * 10
    assert lazy_data == input_value * 20
```

## 配置

使用 `pytest.ini` 配置文件来配置插件行为：

```ini
[pytest.dynamic_params]
# 动态参数化系统配置
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

配置文件提供了集中管理、版本控制、可读性好、持久化等优点，适合长期项目和团队协作。

## 项目结构

项目的主要组成部分：

- `src/` - 源代码
  - `dynamic_params/` - 核心实现
    - `engine/` - 内部引擎
      - `config.py` - 配置管理
      - `dependency.py` - 依赖解析
      - `registry.py` - 生成器注册表
    - `plugin/` - 插件实现
      - `pytest_plugin.py` - 核心插件逻辑
      - `processors/` - 装饰器处理器
      - `utils.py` - 插件工具函数
    - `public/` - 公共 API
      - `decorators/` - 装饰器
      - `generators/` - 生成器核心类
    - `utils/` - 通用工具
      - `helpers.py` - 辅助函数
    - `__init__.py` - 公共 API 导出
    - `errors.py` - 错误处理
    - `types.py` - 类型定义
- `tests/` - 测试代码
- `examples/` - 使用示例
- `docs/` - 文档
- `specs/` - 项目规格说明
- `reports/` - 测试报告

有关详细的源码架构说明，请参见 [docs/STRUCTURE.md](./docs/STRUCTURE.md)。

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

## 贡献

欢迎贡献！请按照以下步骤：

1. Fork 仓库
2. 创建新分支用于您的功能或 bug 修复
3. 为您的更改编写测试
4. 实现您的更改
5. 运行测试套件确保所有测试通过
6. 提交拉取请求

请确保您的代码遵循项目的代码风格指南并通过所有测试。

## 许可证

MIT 许可证

更多信息请参见 [LICENSE](./LICENSE)。