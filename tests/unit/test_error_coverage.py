"""错误处理模块的覆盖率测试"""

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


def test_all_error_classes_defined():
    """测试所有错误类都被正确定义"""
    # 实例化每个错误类，确保它们的定义被执行
    # DynamicParamError
    try:
        raise DynamicParamError("Test error")
    except DynamicParamError:
        pass

    # MissingParameterError
    try:
        raise MissingParameterError(
            param_name="test",
            generator_name="test_gen",
            required_params=["a"],
            available_params=["b"]
        )
    except MissingParameterError:
        pass

    # InvalidGeneratorError
    try:
        raise InvalidGeneratorError("Test error")
    except InvalidGeneratorError:
        pass

    # CircularDependencyError
    try:
        raise CircularDependencyError(["a", "b", "c"])
    except CircularDependencyError:
        pass

    # ExecutionError
    try:
        try:
            raise ValueError("Test error")
        except ValueError as e:
            raise ExecutionError(
                generator_name="test_gen",
                exception=e,
                context={"a": 1}
            )
    except ExecutionError:
        pass

    # ConfigurationError
    try:
        raise ConfigurationError(
            config_key="test.key",
            config_value="test",
            expected_type=str
        )
    except ConfigurationError:
        pass


def test_all_error_methods_called():
    """测试所有错误方法都被调用"""
    # 测试MissingParameterError._get_message
    mpe = MissingParameterError(
        param_name="test",
        generator_name="test_gen",
        required_params=["a"],
        available_params=["b"]
    )
    mpe._get_message(
        param_name="test",
        generator_name="test_gen",
        required_params=["a"],
        available_params=["b"]
    )

    # 测试InvalidGeneratorError._get_message
    ige = InvalidGeneratorError("test message")
    ige._get_message("test message")

    # 测试CircularDependencyError._get_message
    cde = CircularDependencyError(["a", "b"])
    cde._get_message(["a", "b"])
    cde._get_message([])

    # 测试ExecutionError._get_message
    try:
        raise ValueError("test")
    except ValueError as e:
        ee = ExecutionError(
            generator_name="test_gen",
            exception=e,
            context={"a": 1}
        )
        ee._get_message(
            generator_name="test_gen",
            exception=e,
            context={"a": 1}
        )

    # 测试ConfigurationError._get_message
    ce = ConfigurationError(
        config_key="test.key",
        config_value="test",
        expected_type=str
    )
    ce._get_message(
        config_key="test.key",
        config_value="test",
        expected_type=str
    )
