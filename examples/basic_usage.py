"""
基础用法示例

此文件包含pytest-dynamic-params插件的基础使用示例，
展示了插件的核心功能和常见使用场景，
并提供了实用的最佳实践。
"""

import datetime

import pytest

from dynamic_params import generator, use_generators


# 示例1：基础参数生成 - 数值计算
@generator
def calculate_result(input_value):
    """基础参数生成器，计算输入值的两倍

    这是最基本的参数生成器示例，展示了如何定义一个简单的参数生成函数。
    """
    return input_value * 2


@use_generators(result=calculate_result)
@pytest.mark.parametrize("input_value", [1, 2, 3, 5, 10])
def test_basic_parameter_generation(input_value, result):
    """测试基础参数生成功能

    测试用例数量：5个
    验证生成的参数值是否正确计算
    """
    assert result == input_value * 2


# 示例2：与fixture混合使用 - 用户权限管理
@pytest.fixture
def database():
    """模拟数据库连接fixture

    提供用户权限数据，模拟真实的数据库连接
    """
    return {
        "users": {
            "admin": {
                "type": "admin",
                "permissions": ["read", "write", "delete", "admin"],
            },
            "user": {"type": "user", "permissions": ["read", "write"]},
            "guest": {"type": "guest", "permissions": ["read"]},
        },
        "roles": {"admin": "Administrator", "user": "Regular User", "guest": "Guest"},
    }


@generator
def get_user_data(database, user_type):
    """依赖于fixture的参数生成器

    根据用户类型从数据库获取用户数据和权限

    Args:
        database: 数据库连接fixture
        user_type: 用户类型

    Returns:
        用户数据字典，包含类型和权限
    """
    user_info = database["users"].get(user_type, {"type": "unknown", "permissions": []})
    role_name = database["roles"].get(user_type, "Unknown Role")
    return {
        **user_info,
        "role_name": role_name,
        "last_updated": datetime.datetime.now().isoformat(),
    }


@use_generators(user_data=get_user_data)
@pytest.mark.parametrize("user_type", ["admin", "user", "guest"])
def test_fixture_integration(database, user_type, user_data):
    """测试与fixture混合使用

    验证参数生成器能否正确使用fixture提供的数据
    """
    assert user_data["type"] == user_type
    assert user_data["permissions"] == database["users"][user_type]["permissions"]
    assert user_data["role_name"] == database["roles"][user_type]
    assert "last_updated" in user_data


# 示例3：参数化fixture支持 - 多环境配置
@pytest.fixture(params=["dev", "test", "staging", "prod"])
def environment(request):
    """参数化fixture，提供不同的环境配置

    为不同环境提供详细的配置信息
    """
    env_config = {
        "dev": {
            "env": "dev",
            "timeout": 10,
            "debug": True,
            "api_url": "http://dev-api.example.com",
            "db_url": "postgresql://dev:dev@localhost:5432/dev_db",
        },
        "test": {
            "env": "test",
            "timeout": 30,
            "debug": False,
            "api_url": "http://test-api.example.com",
            "db_url": "postgresql://test:test@localhost:5432/test_db",
        },
        "staging": {
            "env": "staging",
            "timeout": 45,
            "debug": False,
            "api_url": "http://staging-api.example.com",
            "db_url": "postgresql://staging:staging@staging-db:5432/staging_db",
        },
        "prod": {
            "env": "prod",
            "timeout": 60,
            "debug": False,
            "api_url": "https://api.example.com",
            "db_url": "postgresql://prod:prod@prod-db:5432/prod_db",
        },
    }
    return env_config[request.param]


@generator
def generate_config(environment, feature_flag):
    """依赖于参数化fixture的参数生成器

    根据环境配置和特性标志生成完整的应用配置

    Args:
        environment: 环境配置fixture
        feature_flag: 特性标志

    Returns:
        完整的配置字典
    """
    return {
        "env": environment["env"],
        "feature": feature_flag,
        "timeout": environment["timeout"] + 10,
        "debug": environment["debug"],
        "api_url": environment["api_url"],
        "db_url": environment["db_url"],
        "feature_enabled": feature_flag != "control",
        "config_version": "1.0",
    }


@use_generators(config=generate_config)
@pytest.mark.parametrize("feature_flag", ["A/B", "control", "beta"])
def test_parametrized_fixture_usage(environment, feature_flag, config):
    """测试参数化fixture与参数生成器的结合使用

    验证参数生成器能否正确处理来自参数化fixture的数据
    """
    assert config["env"] == environment["env"]
    assert config["feature"] == feature_flag
    assert config["timeout"] == environment["timeout"] + 10
    assert config["debug"] == environment["debug"]
    assert config["api_url"] == environment["api_url"]
    assert config["feature_enabled"] == (feature_flag != "control")


# 示例4：多个fixture嵌套 - 应用配置链
@pytest.fixture
def base_config():
    """基础配置fixture

    提供应用的基础配置信息
    """
    return {
        "app": "test-application",
        "version": "1.0.0",
        "secret": "dev-secret-key",
        "author": "Test Team",
        "created_at": "2024-01-01",
    }


@pytest.fixture
def database_config(base_config):
    """数据库配置fixture（依赖base_config）

    基于基础配置扩展数据库相关配置
    """
    return {
        **base_config,
        "db": "postgresql",
        "host": "localhost",
        "port": 5432,
        "db_name": "test_db",
        "db_user": "test_user",
        "db_password": "test_pass",
    }


@pytest.fixture
def app_config(database_config):
    """应用配置fixture（依赖database_config）

    基于数据库配置扩展应用相关配置
    """
    return {
        **database_config,
        "app_port": 8080,
        "app_url": "http://localhost:8080",
        "api_prefix": "/api/v1",
        "allowed_origins": ["*"],
        "cors_enabled": True,
    }


@generator
def generate_test_data(app_config, test_type, test_id):
    """依赖于嵌套fixture的参数生成器

    根据应用配置和测试类型生成测试数据

    Args:
        app_config: 应用配置fixture
        test_type: 测试类型
        test_id: 测试ID

    Returns:
        测试数据字典
    """
    return {
        "config": app_config,
        "test_type": test_type,
        "test_id": test_id,
        "test_data": {
            "users": [
                {"id": 1, "name": "Test User 1"},
                {"id": 2, "name": "Test User 2"},
            ],
            "products": [
                {"id": 1, "name": "Product 1", "price": 10.99},
                {"id": 2, "name": "Product 2", "price": 19.99},
            ],
        },
        "timestamp": datetime.datetime.now().isoformat(),
        "environment": app_config.get("env", "local"),
    }


@use_generators(test_data=generate_test_data)
@pytest.mark.parametrize("test_type", ["unit", "integration", "e2e"])
@pytest.mark.parametrize("test_id", [1, 2])
def test_fixture_nesting(app_config, test_type, test_id, test_data):
    """测试fixture嵌套依赖

    验证参数生成器能否正确处理多层嵌套的fixture依赖
    """
    assert test_data["config"]["app_port"] == 8080
    assert test_data["config"]["db"] == "postgresql"
    assert test_data["test_type"] == test_type
    assert test_data["test_id"] == test_id
    assert len(test_data["test_data"]["users"]) == 2
    assert len(test_data["test_data"]["products"]) == 2
    assert "timestamp" in test_data


# 示例5：数据转换 - 格式转换
@generator
def format_data(input_data, format_type):
    """数据转换参数生成器

    根据指定格式转换输入数据

    Args:
        input_data: 输入数据
        format_type: 目标格式类型

    Returns:
        转换后的数据
    """
    if format_type == "uppercase":
        return input_data.upper()
    elif format_type == "lowercase":
        return input_data.lower()
    elif format_type == "title":
        return input_data.title()
    elif format_type == "length":
        return len(input_data)
    elif format_type == "reverse":
        return input_data[::-1]
    elif format_type == "strip":
        return input_data.strip()
    else:
        return input_data


@use_generators(formatted_data=format_data)
@pytest.mark.parametrize(
    "input_data", ["hello world", "TEST DATA", "Python Testing", "  trimmed  ", "12345"]
)
@pytest.mark.parametrize(
    "format_type", ["uppercase", "lowercase", "title", "length", "reverse", "strip"]
)
def test_data_transformation(input_data, format_type, formatted_data):
    """测试数据转换功能

    验证参数生成器能否根据不同格式类型转换数据
    """
    if format_type == "uppercase":
        assert formatted_data == input_data.upper()
    elif format_type == "lowercase":
        assert formatted_data == input_data.lower()
    elif format_type == "title":
        assert formatted_data == input_data.title()
    elif format_type == "length":
        assert formatted_data == len(input_data)
    elif format_type == "reverse":
        assert formatted_data == input_data[::-1]
    elif format_type == "strip":
        assert formatted_data == input_data.strip()


# 示例6：条件参数生成 - 基于输入条件的动态参数
@generator
def generate_conditional_params(input_value):
    """条件参数生成器

    根据输入值的条件生成不同的参数

    Args:
        input_value: 输入值

    Returns:
        基于条件生成的参数字典
    """
    if input_value < 0:
        return {
            "type": "negative",
            "value": input_value,
            "abs_value": abs(input_value),
            "description": "Negative number",
        }
    elif input_value == 0:
        return {"type": "zero", "value": input_value, "description": "Zero"}
    elif input_value > 0 and input_value < 10:
        return {
            "type": "small_positive",
            "value": input_value,
            "squared": input_value**2,
            "description": "Small positive number",
        }
    else:
        return {
            "type": "large_positive",
            "value": input_value,
            "sqrt": input_value**0.5,
            "description": "Large positive number",
        }


@use_generators(conditional_params=generate_conditional_params)
@pytest.mark.parametrize("input_value", [-5, 0, 5, 25])
def test_conditional_parameter_generation(input_value, conditional_params):
    """测试条件参数生成

    验证参数生成器能否根据输入条件生成不同的参数
    """
    assert conditional_params["value"] == input_value

    if input_value < 0:
        assert conditional_params["type"] == "negative"
        assert conditional_params["abs_value"] == abs(input_value)
    elif input_value == 0:
        assert conditional_params["type"] == "zero"
    elif input_value > 0 and input_value < 10:
        assert conditional_params["type"] == "small_positive"
        assert conditional_params["squared"] == input_value**2
    else:
        assert conditional_params["type"] == "large_positive"
        assert conditional_params["sqrt"] == input_value**0.5

    assert "description" in conditional_params
