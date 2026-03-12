"""
基础用法示例

此文件包含pytest-dynamic-params插件的基础使用示例
"""

import pytest

from dynamic_params import dynamic_params, param_generator


# 示例1：基础参数生成
@param_generator
def calculate_result(input_value):
    """基础参数生成器"""
    return input_value * 2


@dynamic_params(result=calculate_result)
@pytest.mark.parametrize("input_value", [1, 2, 3])
def test_basic(input_value, result):
    """测试用例数量：3个"""
    assert result == input_value * 2


# 示例2：与fixture混合使用
@pytest.fixture
def database():
    """模拟数据库连接"""
    return {"users": {"admin": {"type": "admin"}, "user": {"type": "user"}}}


@param_generator
def get_user_data(database, user_type):
    """依赖于fixture的参数生成器"""
    return database["users"].get(user_type, {"type": "unknown"})


@dynamic_params(user_data=get_user_data)
@pytest.mark.parametrize("user_type", ["admin", "user"])
def test_fixture_integration(database, user_type, user_data):
    """与fixture混合使用测试示例"""
    assert user_data["type"] == user_type
    assert database["users"][user_type] is not None


# 示例3：参数化fixture支持
@pytest.fixture(params=["dev", "test", "prod"])
def environment(request):
    """参数化fixture"""
    return {"env": request.param, "timeout": 30}


@param_generator
def generate_config(environment, feature_flag):
    """依赖于参数化fixture的参数生成器"""
    return {
        "env": environment["env"],
        "feature": feature_flag,
        "timeout": environment["timeout"] + 10,
    }


@dynamic_params(config=generate_config)
@pytest.mark.parametrize("feature_flag", ["A/B", "control"])
def test_parametrized_fixture_usage(environment, feature_flag, config):
    """参数化fixture测试示例"""
    assert config["env"] == environment["env"]
    assert config["feature"] == feature_flag
    assert config["timeout"] == environment["timeout"] + 10


# 示例4：多个fixture嵌套
@pytest.fixture
def base_config():
    """基础配置fixture"""
    return {"app": "test", "version": "1.0"}


@pytest.fixture
def database_config(base_config):
    """数据库配置fixture（依赖base_config）"""
    return {**base_config, "db": "postgresql"}


@pytest.fixture
def app_config(database_config):
    """应用配置fixture（依赖database_config）"""
    return {**database_config, "port": 8080}


@param_generator
def generate_test_data(app_config, test_type):
    """依赖于嵌套fixture的参数生成器"""
    return {"config": app_config, "type": test_type, "data": [1, 2, 3]}


@dynamic_params(test_data=generate_test_data)
@pytest.mark.parametrize("test_type", ["unit", "integration"])
def test_fixture_nesting(app_config, test_type, test_data):
    """fixture嵌套依赖测试示例"""
    assert test_data["config"]["port"] == 8080
    assert test_data["type"] == test_type
    assert len(test_data["data"]) == 3
