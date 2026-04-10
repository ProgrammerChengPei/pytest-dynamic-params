# pytest-dynamic-params 使用指南

## 概述

`pytest-dynamic-params` 是一个用于pytest的动态参数化插件，支持声明式地定义参数生成器，系统自动处理参数收集、依赖解析、动态参数生成和测试用例参数化。

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

### 1. 参数化fixture装饰器 (`@parametrize_fixture`)

使用 `@parametrize_fixture` 装饰器对fixture进行参数化，支持定义参数化fixture。参数名称有特殊处理规则，支持灵活的参数定义。

### 2. 链式参数生成器 (`@param_generator`)

使用 `@param_generator` 装饰器定义链式参数生成器，支持 A→B→C 的真实依赖传递关系。基于参数名严格匹配实现自动依赖解析。

### 3. 链式依赖解析机制

系统自动分析生成器函数的参数签名，根据参数名精确匹配来确定依赖关系，支持复杂的链式依赖。

### 4. Scope自动推断

根据依赖生成器的最小scope自动确定生成器的scope，无需手动配置。

### 5. 与原生pytest无缝集成

完全兼容pytest原生功能，支持与 `@pytest.mark.parametrize`、`@pytest.fixture` 等装饰器混合使用。

## 基本用法

### 单级参数生成器使用

```python
from dynamic_params import param_generator
import pytest

@param_generator
def calculate_result(input_value):
    """基于输入值计算结果"""
    return input_value * 2

@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_basic_dependency(input_value, calculate_result):
    """基础依赖测试：calculate_result自动依赖于input_value"""
    assert calculate_result == input_value * 2
```

### 链式依赖示例

```python
from dynamic_params import param_generator
import pytest

@param_generator  
def get_user_data(user_id):
    """获取用户数据"""
    return {"id": user_id, "name": f"user_{user_id}"}

@param_generator
def calculate_user_stats(user_data, stat_type):
    """计算用户统计信息，依赖于用户数据"""
    if stat_type == "age":
        return user_data["id"] * 10
    elif stat_type == "score":
        return user_data["id"] * 100

@pytest.mark.parametrize("user_id", [1, 2, 3])
@pytest.mark.parametrize("stat_type", ["age", "score"])
def test_chain_dependencies(user_id, stat_type, get_user_data, calculate_user_stats):
    """链式依赖测试：calculate_user_stats依赖于get_user_data"""
    assert get_user_data["id"] == user_id
    assert calculate_user_stats > 0
```

### 与fixture结合使用

```python
from dynamic_params import param_generator
import pytest

@pytest.fixture
def base_config():
    """基础配置fixture"""
    return {"base": "config"}

@pytest.fixture 
def api_url():
    """API URL fixture"""
    return "http://api.example.com"

@param_generator
def generate_env_config(base_config, environment):
    """基于基础配置和环境生成环境配置"""
    return {**base_config, "env": environment}

@param_generator
def generate_api_endpoint(api_url, resource, method):
    """生成完整API端点信息"""
    return {
        "endpoint": f"{api_url}/{resource}",
        "method": method,
        "url": api_url
    }

@pytest.mark.parametrize("environment", ["dev", "test", "prod"])
@pytest.mark.parametrize("resource", ["users", "products"])
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_fixture_and_generator_integration(
    base_config, api_url, environment, resource, method,
    generate_env_config, generate_api_endpoint
):
    """fixture与参数生成器集成测试"""
    assert generate_env_config["base"] == "config"
    assert generate_env_config["env"] == environment
    assert generate_api_endpoint["method"] == method
    assert resource in generate_api_endpoint["endpoint"]
```

## 高级链式依赖示例

### 多级依赖关系

```python
from dynamic_params import param_generator
import pytest

@param_generator
def get_product_info(product_id):
    """获取产品基本信息"""
    return {"id": product_id, "name": f"Product_{product_id}"}

@param_generator
def calculate_product_price(product_info, discount_rate):
    """计算产品价格，依赖于产品信息"""
    base_price = product_info["id"] * 100
    return base_price * (1 - discount_rate)

@param_generator
def check_product_availability(product_info, price, warehouse_id):
    """检查产品可用性，依赖于产品信息和价格"""
    return {
        "product": product_info["name"],
        "price": price,
        "available": price > 0 and warehouse_id > 0
    }

@pytest.mark.parametrize("product_id", [1, 2, 3])
@pytest.mark.parametrize("discount_rate", [0.0, 0.1, 0.2])
@pytest.mark.parametrize("warehouse_id", [1, 2])
def test_multi_level_chain(
    product_id, discount_rate, warehouse_id,
    get_product_info, calculate_product_price, check_product_availability
):
    """三级链式依赖测试：product_id → product_info → price → availability"""
    assert get_product_info["id"] == product_id
    assert calculate_product_price > 0
    assert "available" in check_product_availability
    assert isinstance(check_product_availability["available"], bool)
```

### 复杂业务场景示例

```python
from dynamic_params import param_generator
import pytest

@pytest.fixture
def user_session():
    """模拟用户会话"""
    return {"user_id": 123, "logged_in": True}

@param_generator
def get_user_permissions(user_session, permission_level):
    """获取用户权限，依赖于用户会话"""
    return {
        "user_id": user_session["user_id"],
        "can_read": permission_level in ["read", "write"],
        "can_write": permission_level == "write"
    }

@param_generator
def access_secured_resource(user_permissions, resource_id):
    """访问受保护资源，依赖于用户权限"""
    return {
        "resource_id": resource_id,
        "accessible": user_permissions["can_read"],
        "writable": user_permissions["can_write"]
    }

@pytest.mark.parametrize("permission_level", ["read", "write", "none"])
@pytest.mark.parametrize("resource_id", ["doc1", "doc2", "config"])
def test_security_workflow(
    user_session, permission_level, resource_id,
    get_user_permissions, access_secured_resource
):
    """安全流程测试：用户会话→权限检查→资源访问"""
    assert user_session["logged_in"] is True
    assert get_user_permissions["user_id"] == user_session["user_id"]
    
    if permission_level == "none":
        assert not access_secured_resource["accessible"]
    else:
        assert access_secured_resource["accessible"]
        if permission_level == "write":
            assert access_secured_resource["writable"]
        else:
            assert not access_secured_resource["writable"]
```

### 参数化fixture使用示例

```python
from dynamic_params import parametrize_fixture, param_generator
import pytest

@parametrize_fixture
@pytest.mark.parametrize("env_type", ["dev", "test", "prod"])
def environment_config(env_type):
    """参数化环境配置fixture"""
    configs = {
        "dev": {"debug": True, "timeout": 30},
        "test": {"debug": True, "timeout": 60}, 
        "prod": {"debug": False, "timeout": 120}
    }
    return configs[env_type]

@param_generator
def generate_service_config(environment_config, service_name):
    """生成服务配置，依赖环境配置"""
    return {
        "service": service_name,
        "debug": environment_config["debug"],
        "timeout": environment_config["timeout"]
    }

@pytest.mark.parametrize("service_name", ["api", "db", "cache"])
def test_parametrized_fixture_with_generator(
    env_type, service_name, environment_config, generate_service_config
):
    """参数化fixture与链式生成器结合使用"""
    assert isinstance(environment_config, dict)
    assert "debug" in environment_config
    assert generate_service_config["service"] == service_name
    assert generate_service_config["debug"] == environment_config["debug"]
```

## 参数生成器行为配置

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
    param_generator: 参数生成器函数
    parametrize_fixture: 参数化fixture
```

## 最佳实践

1. **保持生成器函数纯净**：生成器函数应该只负责生成参数值，不要有副作用。
2. **合理使用作用域**：系统会根据依赖链自动推断scope，但可通过配置进行优化。
3. **明确依赖关系**：确保生成器函数的参数签名清晰地表达依赖关系，名称匹配是关键。
4. **启用缓存**：对于计算密集型的参数生成，启用缓存可以显著提高性能。
5. **使用懒加载**：对于可能不被使用的参数，启用懒加载可以避免不必要的计算。
6. **使用有意义的参数名**：使用描述性的参数名有助于理解测试逻辑和依赖关系。
7. **控制依赖复杂度**：避免过于复杂的依赖链，保持依赖关系清晰可维护。
8. **利用自动依赖检测**：`@param_generator` 自动推断依赖关系，无需手动配置。
9. **集成pytest原生功能**：与 `@pytest.mark.parametrize`、`@pytest.fixture` 等装饰器无缝结合。
10. **参数名精确匹配**：确保依赖关系通过精确的参数名匹配来实现。

## 常见问题

### 为什么我的参数生成器没有被执行？

确保：

1. 使用了 `@param_generator` 装饰器
2. 测试函数中引用了生成器函数
3. 生成器的参数名与被依赖的参数完全匹配
4. 依赖的参数在测试参数化或fixture中可用
5. 没有循环依赖问题

### 如何调试参数生成问题？

启用详细日志记录：

```bash
python -m pytest -v -s --log-cli-level=DEBUG
```

查看依赖解析过程：

```bash
python -m pytest tests/ -v --dynamic-params-debug
```

### 如何处理循环依赖？

重构参数生成器，消除循环依赖关系。可以：

1. 合并相关的生成器函数
2. 提取共享逻辑到单独的函数
3. 重新设计参数依赖结构
4. 使用参数化fixture替代部分依赖链

### 如何优化性能？

1. **启用缓存**：对计算密集的生成器启用缓存
2. **使用合理的scope**：根据数据特性选择合适的scope等级
3. **避免重复计算**：利用pytest的fixture缓存机制
4. **懒加载**：对可选依赖启用懒加载
5. **批量处理**：相关参数尽量在一个生成器中处理

## 性能建议

1. **缓存策略**：根据测试频率调整缓存大小和时效
2. **懒加载配置**：对大型数据或远程资源启用懒加载
3. **作用域优化**：了解scope自动推断逻辑，必要时手动调整
4. **依赖解析效率**：保持依赖链简洁，避免深度嵌套
5. **批量生成优势**：相关参数同生成器处理减少解析开销
6. **监控资源使用**：定期检查内存和计算资源消耗

## 测试执行命令

运行完整的测试套件：

```bash
python -m pytest tests/ --alluredir=reports/allure-results -clean --cov=src.dynamic_params --cov-report=html:reports/coverage-html --cov-report=xml:reports/coverage.xml --cov-report=term
```

查看Allure报告：

```bash
allure serve reports/allure-results
```