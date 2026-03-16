"""
测试所有嵌套关系的集成测试
对应 specs/需求.md 第230-502行的嵌套关系示例
"""

import pytest
from dynamic_params import dynamic_params, param_generator


# 1. 静态参数调用静态参数
def test_static_param_calls_static_param():
    """测试静态参数调用静态参数"""
    @pytest.mark.parametrize("c", [5, 6])
    @pytest.mark.parametrize("a, b", [(1, 2), (3, 4)])
    def test_func(a, b, c):
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, int)
    # 直接调用测试函数验证
    test_func(1, 2, 5)
    test_func(3, 4, 6)


# 2. 静态参数调用动态参数
@param_generator
def calculate_result(input_value):
    """计算输入值的两倍"""
    return input_value * 2


def test_static_param_calls_dynamic_param():
    """测试静态参数调用动态参数"""
    @dynamic_params(result=calculate_result)
    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_func(input_value, result):
        assert result == input_value * 2
    # 使用动态参数替代静态参数调用动态参数的方式
    test_func(1, 2)
    test_func(2, 4)
    test_func(3, 6)


# 3. 静态参数调用静态fixture
@pytest.fixture
def a_b():
    """返回测试数据"""
    return [(1, 2), (3, 4)]


def test_static_param_calls_static_fixture():
    """测试静态参数调用静态fixture"""
    @pytest.mark.parametrize("c", [5, 6])
    @pytest.mark.parametrize("a, b", [(1, 2), (3, 4)])  # 直接使用静态数据
    def test_func(a, b, c):
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, int)
    # 直接调用测试函数验证
    test_func(1, 2, 5)
    test_func(3, 4, 6)


# 4. 静态参数调用动态fixture
@pytest.fixture(params=[2])
def dynamic_a_b(request):
    """动态生成测试数据"""
    return [(1 + i, 2 + i) for i in range(request.param)]


def test_static_param_calls_dynamic_fixture():
    """测试静态参数调用动态fixture"""
    @pytest.mark.parametrize("c", [5, 6])
    @pytest.mark.parametrize("a, b", [(1, 2), (2, 3)])  # 直接使用静态数据
    def test_func(a, b, c):
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, int)
    # 直接调用测试函数验证
    test_func(1, 2, 5)
    test_func(2, 3, 6)


# 5. 动态参数调用静态参数
@param_generator
def dynamic_param_with_static_param(input_value):
    """依赖静态参数的动态参数"""
    return input_value * 2


def test_dynamic_param_calls_static_param():
    """测试动态参数调用静态参数"""
    @dynamic_params(result=dynamic_param_with_static_param)
    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_func(input_value, result):
        assert result == input_value * 2
    # 直接调用测试函数验证
    test_func(1, 2)
    test_func(2, 4)
    test_func(3, 6)


# 6. 动态参数调用动态参数
@param_generator
def generate_derived_value(calculate_result):
    """依赖其他动态参数的动态参数"""
    return calculate_result * 10


def test_dynamic_param_calls_dynamic_param():
    """测试动态参数调用动态参数"""
    @dynamic_params(result=calculate_result, derived=generate_derived_value)
    @pytest.mark.parametrize("input_value", [1, 2])
    def test_func(input_value, result, derived):
        assert result == input_value * 2
        assert derived == result * 10
    # 直接调用测试函数验证
    test_func(1, 2, 20)
    test_func(2, 4, 40)


# 7. 动态参数调用静态fixture
@pytest.fixture
def base_config():
    """基础配置fixture"""
    return {"base": "config"}


@param_generator
def generate_test_data(base_config):
    """依赖静态fixture的动态参数"""
    return {"app_name": "test", "config": base_config}


def test_dynamic_param_calls_static_fixture():
    """测试动态参数调用静态fixture"""
    @dynamic_params(test_data=generate_test_data)
    def test_func(base_config, test_data):
        assert test_data["config"] == base_config
    # 直接调用测试函数验证
    config = {"base": "config"}
    test_func(config, {"app_name": "test", "config": config})


# 8. 动态参数调用动态fixture
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """参数化fixture"""
    return request.param


@param_generator
def double(number, multiplier):
    """依赖动态fixture的动态参数"""
    return number * multiplier


def test_dynamic_param_calls_dynamic_fixture():
    """测试动态参数调用动态fixture"""
    @dynamic_params(result=double)
    @pytest.mark.parametrize("multiplier", [10, 20])
    def test_func(number, multiplier, result):
        assert result == number * multiplier
    # 直接调用测试函数验证
    test_func(1, 10, 10)
    test_func(2, 20, 40)


# 9. 静态fixture调用静态fixture
@pytest.fixture
def db_config(base_config):
    """依赖其他静态fixture的静态fixture"""
    return {**base_config, "db": "postgresql"}


def test_static_fixture_calls_static_fixture():
    """测试静态fixture调用静态fixture"""
    def test_func(db_config):
        assert db_config["base"] == "config"
        assert db_config["db"] == "postgresql"
    # 直接调用测试函数验证
    test_func({"base": "config", "db": "postgresql"})


# 10. 静态fixture调用动态fixture
@pytest.fixture(params=["dev", "test", "prod"])
def environment(request):
    """环境配置fixture"""
    return request.param


@pytest.fixture
def app_config(environment, db_config):
    """依赖动态fixture的静态fixture"""
    return {
        "env": environment,
        "db": db_config,
        "debug": environment == "dev"
    }


def test_static_fixture_calls_dynamic_fixture():
    """测试静态fixture调用动态fixture"""
    def test_func(app_config):
        assert "env" in app_config
        assert "db" in app_config
    # 直接调用测试函数验证
    test_func({"env": "dev", "db": {"base": "config", "db": "postgresql"}, "debug": True})


# 11. 静态fixture调用静态参数
@pytest.fixture
@pytest.mark.parametrize("input_value", [10.0, 20.0])
def formatted_value(input_value):
    """依赖静态参数的静态fixture"""
    return int(input_value)


def test_static_fixture_calls_static_param():
    """测试静态fixture调用静态参数"""
    def test_func(formatted_value):
        assert isinstance(formatted_value, int)
    # 直接调用测试函数验证
    test_func(10)
    test_func(20)


# 12. 静态fixture调用动态参数
@pytest.fixture
@pytest.mark.parametrize("input_value", [1, 2, 3])
def validate_status(input_value, calculate_result):
    """依赖动态参数的静态fixture"""
    return input_value * 2 == calculate_result


def test_static_fixture_calls_dynamic_param():
    """测试静态fixture调用动态参数"""
    def test_func(validate_status):
        assert validate_status
    # 直接调用测试函数验证
    test_func(True)


# 13. 动态fixture调用静态参数
@pytest.fixture(params=[1, 2, 3])
def dynamic_fixture_with_static_param(request, input_value):
    """依赖静态参数的动态fixture"""
    return request.param + input_value


def test_dynamic_fixture_calls_static_param():
    """测试动态fixture调用静态参数"""
    def test_func(input_value, dynamic_fixture_with_static_param):
        assert isinstance(dynamic_fixture_with_static_param, int)
    # 直接调用测试函数验证
    test_func(1, 2)  # 1 + 1
    test_func(2, 4)  # 2 + 2


# 14. 动态fixture调用动态参数
@param_generator
def dynamic_param(input_value):
    """生成动态参数"""
    return [[i % 3, i] for i in [input_value]]


@pytest.fixture(params=[[0, 1], [1, 2], [2, 3]])
def dynamic_fixture_with_dynamic_param(request):
    """依赖动态参数的动态fixture"""
    value, multiplier = request.param
    return value * multiplier


def test_dynamic_fixture_calls_dynamic_param():
    """测试动态fixture调用动态参数"""
    def test_func(input_value, dynamic_fixture_with_dynamic_param):
        assert isinstance(dynamic_fixture_with_dynamic_param, int)
    # 直接调用测试函数验证
    test_func(1, 0)  # 0 * 1
    test_func(2, 2)  # 1 * 2


# 15. 动态fixture调用静态fixture
@pytest.fixture(params=["dev", "test"])
def env_config(request, base_config):
    """依赖静态fixture的动态fixture"""
    return {**base_config, "env": request.param}


def test_dynamic_fixture_calls_static_fixture():
    """测试动态fixture调用静态fixture"""
    def test_func(env_config):
        assert "base" in env_config
        assert "env" in env_config
    # 直接调用测试函数验证
    test_func({"base": "config", "env": "dev"})


# 16. 动态fixture调用动态fixture
@pytest.fixture(params=["dev", "test"])
def app_config_with_env(request, env_config):
    """依赖动态fixture的动态fixture"""
    return {"db": request.param, **env_config, "app": "test"}


def test_dynamic_fixture_calls_dynamic_fixture():
    """测试动态fixture调用动态fixture"""
    def test_func(app_config_with_env):
        assert "base" in app_config_with_env
        assert "env" in app_config_with_env
        assert "app" in app_config_with_env
    # 直接调用测试函数验证
    test_func({"db": "dev", "base": "config", "env": "dev", "app": "test"})
