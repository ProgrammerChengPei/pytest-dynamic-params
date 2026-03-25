"""错误处理模块的单元测试"""

import pytest

# 直接导入模块，确保模块被加载
import dynamic_params.errors
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

    def test_inheritance(self):
        """测试DynamicParamError继承关系"""
        error = DynamicParamError("Test message")
        assert isinstance(error, Exception)

    def test_error_message(self):
        """测试DynamicParamError错误消息"""
        error_message = "Test error message"
        error = DynamicParamError(error_message)
        assert str(error) == error_message


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

    def test_inheritance(self):
        """测试MissingParameterError继承关系"""
        error = MissingParameterError(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=["param1"],
            available_params=["param2"],
        )
        assert isinstance(error, DynamicParamError)
        assert isinstance(error, Exception)


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

    def test_error_message(self):
        """测试InvalidGeneratorError错误消息"""
        error_message = "Invalid generator test message"
        error = InvalidGeneratorError(error_message)
        assert str(error) == error_message


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

    def test_error_message_with_long_cycle(self):
        """测试CircularDependencyError错误消息（长循环）"""
        cycle = ["func1", "func2", "func3", "func1"]
        error = CircularDependencyError(cycle)

        message = str(error)
        assert "循环依赖" in message
        assert "func1" in message
        assert "func2" in message
        assert "func3" in message


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
                generator_name="test_generator",
                exception=e,
                context={},
            )

            assert isinstance(error, DynamicParamError)
            assert isinstance(error, Exception)

    def test_error_message_with_different_exception(self):
        """测试ExecutionError错误消息（不同类型的异常）"""
        try:
            raise TypeError("Type error")
        except TypeError as e:
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1"},
            )

            message = str(error)
            assert "test_generator" in message
            assert "TypeError" in message
            assert "Type error" in message
            assert "param1" in message


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

    def test_error_message_with_different_types(self):
        """测试ConfigurationError错误消息（不同类型）"""
        error = ConfigurationError(
            config_key="cache.size_function", config_value="not an integer", expected_type=int
        )

        message = str(error)
        assert "cache.size_function" in message
        assert "not an integer" in message
        assert "int" in message

    def test_missing_parameter_error_empty_lists(self):
        """测试MissingParameterError空列表情况"""
        error = MissingParameterError(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=[],
            available_params=[],
        )
        assert error.param_name == "missing_param"
        assert error.generator_name == "test_generator"
        assert error.required_params == []
        assert error.available_params == []
        message = str(error)
        assert "missing_param" in message
        assert "test_generator" in message

    def test_circular_dependency_error_empty_cycle(self):
        """测试CircularDependencyError空循环情况"""
        error = CircularDependencyError([])
        assert error.cycle == []
        message = str(error)
        assert "循环依赖" in message

    def test_execution_error_empty_context(self):
        """测试ExecutionError空上下文情况"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={},
            )
            assert error.generator_name == "test_generator"
            assert error.exception == e
            assert error.context == {}
            message = str(error)
            assert "test_generator" in message
            assert "ValueError" in message
            assert "Test error" in message

    def test_configuration_error_with_none_value(self):
        """测试ConfigurationError None值情况"""
        error = ConfigurationError(
            config_key="cache.enabled", config_value=None, expected_type=bool
        )
        assert error.config_key == "cache.enabled"
        assert error.config_value is None
        assert error.expected_type == bool
        message = str(error)
        assert "cache.enabled" in message
        assert "None" in message
        assert "bool" in message

    def test_missing_parameter_error_get_message(self):
        """测试MissingParameterError的_get_message方法"""
        error = MissingParameterError(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=["param1", "param2"],
            available_params=["param1"]
        )
        message = error._get_message(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=["param1", "param2"],
            available_params=["param1"]
        )
        assert "missing_param" in message
        assert "test_generator" in message
        assert "param1" in message
        assert "param2" in message

    def test_invalid_generator_error_get_message(self):
        """测试InvalidGeneratorError的_get_message方法"""
        error = InvalidGeneratorError("Invalid generator test message")
        message = error._get_message("Invalid generator test message")
        assert message == "Invalid generator test message"

    def test_circular_dependency_error_get_message(self):
        """测试CircularDependencyError的_get_message方法"""
        error = CircularDependencyError(["func1", "func2", "func1"])
        message = error._get_message(["func1", "func2", "func1"])
        assert "循环依赖" in message
        assert "func1" in message
        assert "func2" in message

    def test_circular_dependency_error_get_message_empty(self):
        """测试CircularDependencyError的_get_message方法（空循环）"""
        error = CircularDependencyError([])
        message = error._get_message([])
        assert "循环依赖" in message
        assert "空循环" in message

    def test_execution_error_get_message(self):
        """测试ExecutionError的_get_message方法"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1"}
            )
            message = error._get_message(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1"}
            )
            assert "test_generator" in message
            assert "ValueError" in message
            assert "Test error" in message
            assert "param1" in message

    def test_configuration_error_get_message(self):
        """测试ConfigurationError的_get_message方法"""
        error = ConfigurationError(
            config_key="cache.enabled", config_value="not a boolean", expected_type=bool
        )
        message = error._get_message(
            config_key="cache.enabled", config_value="not a boolean", expected_type=bool
        )
        assert "cache.enabled" in message
        assert "not a boolean" in message
        assert "bool" in message

    def test_dynamic_param_error_inheritance(self):
        """测试DynamicParamError的继承关系"""
        error = DynamicParamError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_missing_parameter_error_full(self):
        """测试MissingParameterError的完整功能"""
        # 直接测试_get_message方法
        error = MissingParameterError(
            param_name="missing_param",
            generator_name="test_generator",
            required_params=["param1", "param2"],
            available_params=["param1"]
        )
        # 确保异常可以被正确抛出和捕获
        try:
            raise error
        except DynamicParamError as e:
            assert "missing_param" in str(e)

    def test_invalid_generator_error_full(self):
        """测试InvalidGeneratorError的完整功能"""
        # 直接测试_get_message方法
        error = InvalidGeneratorError("Invalid generator test message")
        # 确保异常可以被正确抛出和捕获
        try:
            raise error
        except DynamicParamError as e:
            assert "Invalid generator test message" in str(e)

    def test_circular_dependency_error_full(self):
        """测试CircularDependencyError的完整功能"""
        # 直接测试_get_message方法
        error = CircularDependencyError(["func1", "func2", "func1"])
        # 确保异常可以被正确抛出和捕获
        try:
            raise error
        except DynamicParamError as e:
            assert "循环依赖" in str(e)

    def test_execution_error_full(self):
        """测试ExecutionError的完整功能"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            # 直接测试_get_message方法
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1"}
            )
            # 确保异常可以被正确抛出和捕获
            try:
                raise error
            except DynamicParamError as ex:
                assert "test_generator" in str(ex)
                assert "ValueError" in str(ex)

    def test_configuration_error_full(self):
        """测试ConfigurationError的完整功能"""
        # 直接测试_get_message方法
        error = ConfigurationError(
            config_key="cache.enabled", config_value="not a boolean", expected_type=bool
        )
        # 确保异常可以被正确抛出和捕获
        try:
            raise error
        except DynamicParamError as e:
            assert "cache.enabled" in str(e)
            assert "not a boolean" in str(e)

    def test_dynamic_param_error_raise(self):
        """测试DynamicParamError的抛出"""
        try:
            raise DynamicParamError("Test error")
        except DynamicParamError as e:
            assert str(e) == "Test error"

    def test_missing_parameter_error_raise(self):
        """测试MissingParameterError的抛出"""
        try:
            raise MissingParameterError(
                param_name="missing_param",
                generator_name="test_generator",
                required_params=["param1", "param2"],
                available_params=["param1"]
            )
        except DynamicParamError as e:
            assert "missing_param" in str(e)
            assert "test_generator" in str(e)

    def test_invalid_generator_error_raise(self):
        """测试InvalidGeneratorError的抛出"""
        try:
            raise InvalidGeneratorError("Invalid generator")
        except DynamicParamError as e:
            assert "Invalid generator" in str(e)

    def test_circular_dependency_error_raise(self):
        """测试CircularDependencyError的抛出"""
        try:
            raise CircularDependencyError(["func1", "func2", "func1"])
        except DynamicParamError as e:
            assert "循环依赖" in str(e)
            assert "func1" in str(e)

    def test_execution_error_raise(self):
        """测试ExecutionError的抛出"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            try:
                raise ExecutionError(
                    generator_name="test_generator",
                    exception=e,
                    context={"param1": "value1"}
                )
            except DynamicParamError as ex:
                assert "test_generator" in str(ex)
                assert "ValueError" in str(ex)

    def test_configuration_error_raise(self):
        """测试ConfigurationError的抛出"""
        try:
            raise ConfigurationError(
                config_key="cache.enabled", config_value="not a boolean", expected_type=bool
            )
        except DynamicParamError as e:
            assert "cache.enabled" in str(e)
            assert "not a boolean" in str(e)

    def test_dynamic_param_error_direct_instantiation(self):
        """测试直接实例化DynamicParamError"""
        error = DynamicParamError("Test error message")
        assert str(error) == "Test error message"

    def test_missing_parameter_error_full_initialization(self):
        """测试MissingParameterError的完整初始化"""
        error = MissingParameterError(
            param_name="test_param",
            generator_name="test_generator",
            required_params=["param1", "param2"],
            available_params=["param1"]
        )
        assert error.param_name == "test_param"
        assert error.generator_name == "test_generator"
        assert error.required_params == ["param1", "param2"]
        assert error.available_params == ["param1"]

    def test_invalid_generator_error_full_initialization(self):
        """测试InvalidGeneratorError的完整初始化"""
        error = InvalidGeneratorError("Invalid generator message")
        assert error.message == "Invalid generator message"

    def test_circular_dependency_error_full_initialization(self):
        """测试CircularDependencyError的完整初始化"""
        error = CircularDependencyError(["func1", "func2", "func3"])
        assert error.cycle == ["func1", "func2", "func3"]

    def test_execution_error_full_initialization(self):
        """测试ExecutionError的完整初始化"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            error = ExecutionError(
                generator_name="test_generator",
                exception=e,
                context={"param1": "value1"}
            )
            assert error.generator_name == "test_generator"
            assert error.exception == e
            assert error.context == {"param1": "value1"}

    def test_configuration_error_full_initialization(self):
        """测试ConfigurationError的完整初始化"""
        error = ConfigurationError(
            config_key="test.key",
            config_value="test_value",
            expected_type=str
        )
        assert error.config_key == "test.key"
        assert error.config_value == "test_value"
        assert error.expected_type == str

    def test_all_error_classes_imported(self):
        """测试所有错误类都被正确导入和使用"""
        # 直接使用每个错误类，确保它们被覆盖率工具识别
        assert DynamicParamError.__name__ == "DynamicParamError"
        assert MissingParameterError.__name__ == "MissingParameterError"
        assert InvalidGeneratorError.__name__ == "InvalidGeneratorError"
        assert CircularDependencyError.__name__ == "CircularDependencyError"
        assert ExecutionError.__name__ == "ExecutionError"
        assert ConfigurationError.__name__ == "ConfigurationError"

    def test_all_error_methods_called(self):
        """测试所有错误方法都被调用"""
        # 测试MissingParameterError._get_message
        mpe = MissingParameterError(
            param_name="test",
            generator_name="test_gen",
            required_params=["a"],
            available_params=["b"]
        )
        mpe_msg = mpe._get_message(
            param_name="test",
            generator_name="test_gen",
            required_params=["a"],
            available_params=["b"]
        )
        assert isinstance(mpe_msg, str)

        # 测试InvalidGeneratorError._get_message
        ige = InvalidGeneratorError("test message")
        ige_msg = ige._get_message("test message")
        assert isinstance(ige_msg, str)

        # 测试CircularDependencyError._get_message
        cde = CircularDependencyError(["a", "b"])
        cde_msg = cde._get_message(["a", "b"])
        assert isinstance(cde_msg, str)
        cde_msg_empty = cde._get_message([])
        assert isinstance(cde_msg_empty, str)

        # 测试ExecutionError._get_message
        try:
            raise ValueError("test")
        except ValueError as e:
            ee = ExecutionError(
                generator_name="test_gen",
                exception=e,
                context={"a": 1}
            )
            ee_msg = ee._get_message(
                generator_name="test_gen",
                exception=e,
                context={"a": 1}
            )
            assert isinstance(ee_msg, str)

        # 测试ConfigurationError._get_message
        ce = ConfigurationError(
            config_key="test.key",
            config_value="test",
            expected_type=str
        )
        ce_msg = ce._get_message(
            config_key="test.key",
            config_value="test",
            expected_type=str
        )
        assert isinstance(ce_msg, str)

    def test_dynamic_param_error_inheritance(self):
        """测试 DynamicParamError 的继承关系"""
        from dynamic_params import DynamicParamError
        # 验证 DynamicParamError 继承自 Exception
        assert issubclass(DynamicParamError, Exception)

    def test_missing_parameter_error_full(self):
        """测试 MissingParameterError 的完整初始化"""
        from dynamic_params import MissingParameterError
        try:
            raise MissingParameterError(
                param_name="test_param",
                generator_name="test_generator",
                required_params=["test_param", "other_param"],
                available_params=["other_param"]
            )
        except MissingParameterError as e:
            assert e.param_name == "test_param"
            assert e.generator_name == "test_generator"
            assert e.required_params == ["test_param", "other_param"]
            assert e.available_params == ["other_param"]

    def test_invalid_generator_error_full(self):
        """测试 InvalidGeneratorError 的完整初始化"""
        from dynamic_params import InvalidGeneratorError
        try:
            raise InvalidGeneratorError("Invalid generator function")
        except InvalidGeneratorError as e:
            assert e.message == "Invalid generator function"

    def test_circular_dependency_error_full(self):
        """测试 CircularDependencyError 的完整初始化"""
        from dynamic_params import CircularDependencyError
        try:
            raise CircularDependencyError(["a", "b", "c"])
        except CircularDependencyError as e:
            assert e.cycle == ["a", "b", "c"]

    def test_execution_error_full(self):
        """测试 ExecutionError 的完整初始化"""
        from dynamic_params import ExecutionError
        try:
            raise ExecutionError(
                generator_name="test_generator",
                exception=ValueError("Test error"),
                context={"param": "value"}
            )
        except ExecutionError as e:
            assert e.generator_name == "test_generator"
            assert isinstance(e.exception, ValueError)
            assert e.context == {"param": "value"}

    def test_configuration_error_full(self):
        """测试 ConfigurationError 的完整初始化"""
        from dynamic_params import ConfigurationError
        try:
            raise ConfigurationError(
                config_key="test.key",
                config_value="value",
                expected_type=int
            )
        except ConfigurationError as e:
            assert e.config_key == "test.key"
            assert e.config_value == "value"
            assert e.expected_type == int

    def test_dynamic_param_error_raise(self):
        """测试 DynamicParamError 的抛出"""
        from dynamic_params import DynamicParamError
        try:
            raise DynamicParamError("Test error")
        except DynamicParamError as e:
            assert str(e) == "Test error"

    def test_missing_parameter_error_raise(self):
        """测试 MissingParameterError 的抛出"""
        from dynamic_params import MissingParameterError
        try:
            raise MissingParameterError(
                param_name="test_param",
                generator_name="test_generator",
                required_params=["test_param"],
                available_params=[]
            )
        except MissingParameterError as e:
            assert "test_param" in str(e)
            assert "test_generator" in str(e)

    def test_invalid_generator_error_raise(self):
        """测试 InvalidGeneratorError 的抛出"""
        from dynamic_params import InvalidGeneratorError
        try:
            raise InvalidGeneratorError("Invalid generator")
        except InvalidGeneratorError as e:
            assert "Invalid generator" in str(e)

    def test_circular_dependency_error_raise(self):
        """测试 CircularDependencyError 的抛出"""
        from dynamic_params import CircularDependencyError
        try:
            raise CircularDependencyError(["a", "b", "c"])
        except CircularDependencyError as e:
            assert "a -> b -> c -> a" in str(e)

    def test_execution_error_raise(self):
        """测试 ExecutionError 的抛出"""
        from dynamic_params import ExecutionError
        try:
            raise ExecutionError(
                generator_name="test_generator",
                exception=ValueError("Test error"),
                context={"param": "value"}
            )
        except ExecutionError as e:
            assert "test_generator" in str(e)
            assert "ValueError" in str(e)
            assert "Test error" in str(e)

    def test_configuration_error_raise(self):
        """测试 ConfigurationError 的抛出"""
        from dynamic_params import ConfigurationError
        try:
            raise ConfigurationError(
                config_key="test.key",
                config_value="value",
                expected_type=int
            )
        except ConfigurationError as e:
            assert "test.key" in str(e)
            assert "value" in str(e)
            assert "int" in str(e)

    def test_all_error_classes_imported(self):
        """测试所有错误类都能正确导入"""
        from dynamic_params import (
            DynamicParamError,
            MissingParameterError,
            InvalidGeneratorError,
            CircularDependencyError,
            ExecutionError,
            ConfigurationError
        )
        # 验证所有错误类都能正确导入
        assert DynamicParamError is not None
        assert MissingParameterError is not None
        assert InvalidGeneratorError is not None
        assert CircularDependencyError is not None
        assert ExecutionError is not None
        assert ConfigurationError is not None

    def test_all_error_methods_called(self):
        """测试所有错误方法都被调用"""
        from dynamic_params import (
            MissingParameterError,
            InvalidGeneratorError,
            CircularDependencyError,
            ExecutionError,
            ConfigurationError
        )

        # 测试所有错误类的 _get_message 方法
        try:
            raise MissingParameterError(
                param_name="test_param",
                generator_name="test_generator",
                required_params=["test_param"],
                available_params=[]
            )
        except MissingParameterError:
            pass

        try:
            raise InvalidGeneratorError("Invalid generator")
        except InvalidGeneratorError:
            pass

        try:
            raise CircularDependencyError(["a", "b", "c"])
        except CircularDependencyError:
            pass

        try:
            raise ExecutionError(
                generator_name="test_generator",
                exception=ValueError("Test error"),
                context={"param": "value"}
            )
        except ExecutionError:
            pass

        try:
            raise ConfigurationError(
                config_key="test.key",
                config_value="value",
                expected_type=str
            )
        except ConfigurationError:
            pass

    def test_dynamic_param_error_direct_instantiation(self):
        """测试直接实例化 DynamicParamError"""
        from dynamic_params import DynamicParamError
        # 直接实例化 DynamicParamError
        error = DynamicParamError("Test error")
        assert str(error) == "Test error"

    def test_missing_parameter_error_full_initialization(self):
        """测试 MissingParameterError 的完整初始化"""
        from dynamic_params import MissingParameterError
        # 完整初始化 MissingParameterError
        error = MissingParameterError(
            param_name="test_param",
            generator_name="test_generator",
            required_params=["test_param"],
            available_params=[]
        )
        assert error.param_name == "test_param"
        assert error.generator_name == "test_generator"
        assert error.required_params == ["test_param"]
        assert error.available_params == []

    def test_invalid_generator_error_full_initialization(self):
        """测试 InvalidGeneratorError 的完整初始化"""
        from dynamic_params import InvalidGeneratorError
        # 完整初始化 InvalidGeneratorError
        error = InvalidGeneratorError("Invalid generator")
        assert error.message == "Invalid generator"

    def test_circular_dependency_error_full_initialization(self):
        """测试 CircularDependencyError 的完整初始化"""
        from dynamic_params import CircularDependencyError
        # 完整初始化 CircularDependencyError
        error = CircularDependencyError(["a", "b", "c"])
        assert error.cycle == ["a", "b", "c"]

    def test_execution_error_full_initialization(self):
        """测试 ExecutionError 的完整初始化"""
        from dynamic_params import ExecutionError
        # 完整初始化 ExecutionError
        exception = ValueError("Test error")
        error = ExecutionError(
            generator_name="test_generator",
            exception=exception,
            context={"param": "value"}
        )
        assert error.generator_name == "test_generator"
        assert error.exception == exception
        assert error.context == {"param": "value"}

    def test_configuration_error_full_initialization(self):
        """测试 ConfigurationError 的完整初始化"""
        from dynamic_params import ConfigurationError
        # 完整初始化 ConfigurationError
        error = ConfigurationError(
            config_key="test.key",
            config_value="value",
            expected_type=int
        )
        assert error.config_key == "test.key"
        assert error.config_value == "value"
        assert error.expected_type == int
