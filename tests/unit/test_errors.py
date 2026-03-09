"""错误处理模块的单元测试"""

import pytest

from src.dynamic_params.errors import (
    DynamicParamError,
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
            available_params=["param1"]
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
            available_params=["param1"]
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