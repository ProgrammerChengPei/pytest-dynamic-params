"""
测试与其他pytest插件的兼容性
包括：pytest-cov、pytest-mock、pytest-rerunfailures、pytest-timeout
"""

import pytest

from dynamic_params import dynamic_params, param_generator


# 测试生成器
@param_generator(scope="function")
def generate_test_value():
    """生成测试值"""
    return [1, 2, 3]


@param_generator(scope="function")
def generate_config():
    """生成配置"""
    return {"debug": True, "timeout": 10}


class TestPluginCompatibility:
    """测试与其他pytest插件的兼容性"""

    @dynamic_params(value=generate_test_value)
    def test_with_cov(self, value):
        """测试与pytest-cov的兼容性"""
        assert isinstance(value, list)
        assert len(value) == 3
        assert all(item in [1, 2, 3] for item in value)

    @dynamic_params(value=generate_test_value)
    def test_with_mock(self, value, mocker):
        """测试与pytest-mock的兼容性"""
        # 模拟一个函数
        mock_func = mocker.patch("builtins.print")
        print(f"Test value: {value}")
        mock_func.assert_called_once_with(f"Test value: {value}")
        assert isinstance(value, list)
        assert len(value) == 3

    @dynamic_params(value=generate_test_value)
    @pytest.mark.timeout(5)
    def test_with_timeout(self, value):
        """测试与pytest-timeout的兼容性"""
        import time

        # 模拟一些耗时操作
        time.sleep(0.1)
        assert isinstance(value, list)
        assert len(value) == 3

    @dynamic_params(config=generate_config)
    def test_with_config(self, config):
        """测试配置生成与插件兼容性"""
        assert config["debug"] is True
        assert config["timeout"] == 10

    # 测试多个动态参数与插件的组合
    @dynamic_params(value=generate_test_value, config=generate_config)
    def test_multiple_params_with_plugins(self, value, config, mocker):
        """测试多个动态参数与插件的组合"""
        mock_func = mocker.patch("builtins.print")
        print(f"Value: {value}, Config: {config}")
        mock_func.assert_called_once_with(f"Value: {value}, Config: {config}")
        assert isinstance(value, list)
        assert len(value) == 3
        assert config["debug"] is True
