"""错误处理模块的单元测试"""

import pytest

from dynamic_params.errors import (
    CircularDependencyError,
    ConfigurationError,
    DynamicParamError,
    ExecutionError,
    InvalidGeneratorError,
    MissingParameterError,
)


class TestDynamicParamError:
    """DynamicParamError基础异常的测试类"""

    def test_base_exception(self):
        """测试DynamicParamError基础异常"""
        with pytest.raises(DynamicParamError):
            raise DynamicParamError("Base exception test")


class TestMissingParameterError:
    """MissingParameterError异常的测试类"""

    def test_initialization(self):
        """测试MissingParameterError初始化"""
        error = MissingParameterError(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=["param1", "param2"],
            available_params=["param1"],
        )

        assert error.param_name == "missing_param"
        assert error.generator_name == "test_generator"
        assert error.required_params == ["param1", "param2"]
        assert error.available_params == ["param1"]

    def test_error_message(self):
        """测试MissingParameterError错误消息"""
        error = MissingParameterError(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=["param1", "param2"],
            available_params=["param1"],
        )

        message = str(error)
        assert "missing_param" in message
        assert "test_generator" in message
        assert "param1" in message
        assert "param2" in message


class TestInvalidGeneratorError:
    """InvalidGeneratorError异常的测试类"""

    def test_initialization(self):
        """测试InvalidGeneratorError初始化"""
        error = InvalidGeneratorError("Invalid generator test message")

        assert str(error) == "Invalid generator test message"

    def test_inheritance(self):
        """测试InvalidGeneratorError继承关系"""
        error = InvalidGeneratorError("Test message")

        assert isinstance(error, DynamicParamError)
        assert isinstance(error, Exception)


class TestCircularDependencyError:
    """CircularDependencyError异常的测试类"""

    def test_initialization(self):
        """测试CircularDependencyError初始化"""
        cycle = ["func1", "func2", "func1"]
        error = CircularDependencyError(cycle)

        assert error.cycle == cycle

    def test_error_message(self):
        """测试CircularDependencyError错误消息"""
        cycle = ["func1", "func2", "func1"]
        error = CircularDependencyError(cycle)

        message = str(error)
        assert "循环依赖" in message
        assert "func1" in message
        assert "func2" in message

    def test_inheritance(self):
        """测试CircularDependencyError继承关系"""
        cycle = ["func1", "func2", "func1"]
        error = CircularDependencyError(cycle)

        assert isinstance(error, DynamicParamError)
        assert isinstance(error, Exception)


class TestExecutionError:
    """ExecutionError异常的测试类"""

    def test_initialization(self):
        """测试ExecutionError初始化"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1", "param2": "value2"},
            )

            assert error.generator_name == "test_generator"
            assert error.exception == e
            assert error.context == {"param1": "value1", "param2": "value2"}

    def test_error_message(self):
        """测试ExecutionError错误消息"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1"},
            )

            message = str(error)
            assert "test_generator" in message
            assert "ValueError" in message
            assert "Test error" in message
            assert "param1" in message

    def test_inheritance(self):
        """测试ExecutionError继承关系"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error = ExecutionError(
                generator_name="test_generator", exception=e, context={}
            )

            assert isinstance(error, DynamicParamError)
            assert isinstance(error, Exception)


class TestConfigurationError:
    """ConfigurationError异常的测试类"""

    def test_initialization(self):
        """测试ConfigurationError初始化"""
        error = ConfigurationError(
            config_key="cache.enabled", config_value="not a boolean", expected_type=bool
        )

        assert error.config_key == "cache.enabled"
        assert error.config_value == "not a boolean"
        assert error.expected_type == bool

    def test_error_message(self):
        """测试ConfigurationError错误消息"""
        error = ConfigurationError(
            config_key="cache.enabled", config_value="not a boolean", expected_type=bool
        )

        message = str(error)
        assert "cache.enabled" in message
        assert "not a boolean" in message
        assert "bool" in message

    def test_inheritance(self):
        """测试ConfigurationError继承关系"""
        error = ConfigurationError(
            config_key="cache.enabled", config_value="not a boolean", expected_type=bool
        )

        assert isinstance(error, DynamicParamError)
        assert isinstance(error, Exception)
