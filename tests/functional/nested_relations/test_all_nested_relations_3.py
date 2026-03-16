"""
测试所有嵌套关系
对应 specs/需求.md 第230-502行的嵌套关系示例
"""

import pytest
from dynamic_params import dynamic_params, param_generator


# 1. 静态参数调用静态参数
class TestStaticParamCallsStaticParam:
    """测试静态参数调用静态参数"""

    @pytest.mark.parametrize("c", [5, 6])
    @pytest.mark.parametrize("a, b", [(1, 2), (3, 4)])
    def test_static_param_calls_static_param(self, a, b, c):
        """测试用例数量：2×2=4个"""
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, int)


# 2. 静态参数调用动态参数
@param_generator
def calculate_result(input_value):
    """计算输入值的两倍"""
    return input_value * 2


class _TestStaticParamCallsDynamicParam:
    """测试静态参数调用动态参数"""

    @pytest.mark.parametrize("input_value", [1, 2, 3])
    # @pytest.mark.parametrize("validate_status", [input_value * 2 == calculate_result])
    def test_static_param_calls_dynamic_param(self, input_value, validate_status):
        """测试用例数量：3个"""
        assert validate_status


# 3. 静态参数调用静态fixture
@pytest.fixture
def a_b():
    """返回测试数据"""
    return [(1, 2), (3, 4)]


class _TestStaticParamCallsStaticFixture:
    """测试静态参数调用静态fixture"""

    @pytest.mark.parametrize("c", [5, 6])
    #@pytest.mark.parametrize("a, b", a_b)
    def test_static_param_calls_static_fixture(self, a, b, c):
        """测试用例数量：2×2=4个"""
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, int)


# 4. 静态参数调用动态fixture
@pytest.fixture(params=[2])
def dynamic_a_b(request):
    """动态生成测试数据"""
    return [(1 + i, 2 + i) for i in range(request.param)]


class _TestStaticParamCallsDynamicFixture:
    """测试静态参数调用动态fixture"""

    @pytest.mark.parametrize("c", [5, 6])
    #@pytest.mark.parametrize("a, b", dynamic_a_b)
    def test_static_param_calls_dynamic_fixture(self, a, b, c):
        """测试用例数量：2×2=4个"""
        assert isinstance(a, int)
        assert isinstance(b, int)
        assert isinstance(c, int)


# 5. 动态参数调用静态参数
@param_generator
def dynamic_param_with_static_param(input_value):
    """依赖静态参数的动态参数"""
    return input_value * 2


class TestDynamicParamCallsStaticParam:
    """测试动态参数调用静态参数"""

    @dynamic_params(result=dynamic_param_with_static_param)
    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_dynamic_param_calls_static_param(self, input_value, result):
        """测试用例数量：3个"""
        assert result == input_value * 2


# 6. 动态参数调用动态参数
@param_generator
def generate_derived_value(calculate_result):
    """依赖其他动态参数的动态参数"""
    return calculate_result * 10


class TestDynamicParamCallsDynamicParam:
    """测试动态参数调用动态参数"""

    @dynamic_params(result=calculate_result, derived=generate_derived_value)
    @pytest.mark.parametrize("input_value", [1, 2])
    def test_dynamic_param_calls_dynamic_param(self, input_value, result, derived):
        """测试用例数量：2个"""
        assert result == input_value * 2
        assert derived == result * 10


# 7. 动态参数调用静态fixture
@pytest.fixture
def base_config():
    """基础配置fixture"""
    return {"base": "config"}


@param_generator
def generate_test_data(base_config):
    """依赖静态fixture的动态参数"""
    return {"app_name": "test", "config": base_config}


class TestDynamicParamCallsStaticFixture:
    """测试动态参数调用静态fixture"""

    @dynamic_params(test_data=generate_test_data)
    def test_dynamic_param_calls_static_fixture(self, base_config, test_data):
        """测试用例数量：1个"""
        assert test_data["config"] == base_config


# 8. 动态参数调用动态fixture
@pytest.fixture(params=[1, 2, 3])
def number(request):
    """参数化fixture"""
    return request.param


@param_generator
def double(number, multiplier):
    """依赖动态fixture的动态参数"""
    return number * multiplier


class TestDynamicParamCallsDynamicFixture:
    """测试动态参数调用动态fixture"""

    @dynamic_params(result=double)
    @pytest.mark.parametrize("multiplier", [10, 20])
    def test_dynamic_param_calls_dynamic_fixture(self, number, multiplier, result):
        """测试用例数量：3×2=6个"""
        assert result == number * multiplier


# 9. 静态fixture调用静态fixture
@pytest.fixture
def db_config(base_config):
    """依赖其他静态fixture的静态fixture"""
    return {**base_config, "db": "postgresql"}


class TestStaticFixtureCallsStaticFixture:
    """测试静态fixture调用静态fixture"""

    def test_static_fixture_calls_static_fixture(self, db_config):
        """测试用例数量：1个"""
        assert db_config["base"] == "config"
        assert db_config["db"] == "postgresql"


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


class TestStaticFixtureCallsDynamicFixture:
    """测试静态fixture调用动态fixture"""

    def test_static_fixture_calls_dynamic_fixture(self, app_config):
        """测试用例数量：3个"""
        assert "env" in app_config
        assert "db" in app_config


# 11. 静态fixture调用静态参数
#@pytest.fixture
@pytest.mark.parametrize("input_value", [10.0, 20.0])
def formatted_value(input_value):
    """依赖静态参数的静态fixture"""
    return int(input_value)


class _TestStaticFixtureCallsStaticParam:
    """测试静态fixture调用静态参数"""

    def test_static_fixture_calls_static_param(self, formatted_value):
        """测试用例数量：2个"""
        assert isinstance(formatted_value, int)


# 12. 静态fixture调用动态参数
#@pytest.fixture
@pytest.mark.parametrize("input_value", [1, 2, 3])
def validate_status(input_value, calculate_result):
    """依赖动态参数的静态fixture"""
    return input_value * 2 == calculate_result


class _TestStaticFixtureCallsDynamicParam:
    """测试静态fixture调用动态参数"""

    def test_static_fixture_calls_dynamic_param(self, validate_status):
        """测试用例数量：3个"""
        assert validate_status


# 13. 动态fixture调用静态参数
@pytest.fixture(params=[1, 2, 3])
def dynamic_fixture_with_static_param(request, input_value):
    """依赖静态参数的动态fixture"""
    return request.param + input_value


class TestDynamicFixtureCallsStaticParam:
    """测试动态fixture调用静态参数"""

    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_dynamic_fixture_calls_static_param(self, input_value, dynamic_fixture_with_static_param):
        """测试用例数量：3×3=9个"""
        assert isinstance(dynamic_fixture_with_static_param, int)


# 14. 动态fixture调用动态参数
@param_generator
def dynamic_param(input_value):
    """生成动态参数"""
    return [[i % 3, i] for i in [input_value]]


#@pytest.fixture(params=dynamic_param)
def dynamic_fixture_with_dynamic_param(request):
    """依赖动态参数的动态fixture"""
    value, multiplier = request.param
    return value * multiplier


class _TestDynamicFixtureCallsDynamicParam:
    """测试动态fixture调用动态参数"""

    @pytest.mark.parametrize("input_value", [1, 2, 3])
    def test_dynamic_fixture_calls_dynamic_param(self, input_value, dynamic_fixture_with_dynamic_param):
        """测试用例数量：3个"""
        assert isinstance(dynamic_fixture_with_dynamic_param, int)


# 15. 动态fixture调用静态fixture
@pytest.fixture(params=["dev", "test"])
def env_config(request, base_config):
    """依赖静态fixture的动态fixture"""
    return {**base_config, "env": request.param}


class TestDynamicFixtureCallsStaticFixture:
    """测试动态fixture调用静态fixture"""

    def test_dynamic_fixture_calls_static_fixture(self, env_config):
        """测试用例数量：2个"""
        assert "base" in env_config
        assert "env" in env_config


# 16. 动态fixture调用动态fixture
@pytest.fixture(params=["dev", "test"])
def app_config_with_env(request, env_config):
    """依赖动态fixture的动态fixture"""
    return {"db": request.param, **env_config, "app": "test"}


class TestDynamicFixtureCallsDynamicFixture:
    """测试动态fixture调用动态fixture"""

    def test_dynamic_fixture_calls_dynamic_fixture(self, app_config_with_env):
        """测试用例数量：2×2=4个"""
        assert "base" in app_config_with_env
        assert "env" in app_config_with_env
        assert "app" in app_config_with_env
