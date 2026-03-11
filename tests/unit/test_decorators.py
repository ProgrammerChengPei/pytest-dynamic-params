"""装饰器模块的单元测试"""

import pytest

from dynamic_params.decorators import (
    _ParamGeneratorDecorator,
    param_generator,
    with_dynamic_params,
)


class TestParamGeneratorDecorator:
    """_ParamGeneratorDecorator类的测试类"""

    def test_initialization(self):
        """测试_ParamGeneratorDecorator初始化"""
        decorator = _ParamGeneratorDecorator(scope="session", cache=False, lazy=False)

        assert decorator.scope == "session"
        assert decorator.cache_enabled is False
        assert decorator.lazy_support is False

    def test_default_values(self):
        """测试_ParamGeneratorDecorator默认值"""
        decorator = _ParamGeneratorDecorator()

        assert decorator.scope == "function"
        assert decorator.cache_enabled is True
        assert decorator.lazy_support is True

    def test_call(self):
        """测试_ParamGeneratorDecorator调用"""
        decorator = _ParamGeneratorDecorator(scope="class", cache=False, lazy=True)

        def sample_func(x):
            return x * 2

        decorated_func = decorator(sample_func)

        # 检查装饰后的函数是否具有预期的属性
        assert hasattr(decorated_func, "_is_param_generator")
        assert decorated_func._is_param_generator is True
        assert hasattr(decorated_func, "_decorator_args")
        assert decorated_func._decorator_args["scope"] == "class"
        assert decorated_func._decorator_args["cache_enabled"] is False
        assert decorated_func._decorator_args["lazy_support"] is True

    def test_function_wrapping(self):
        """测试装饰器功能包装"""
        decorator = _ParamGeneratorDecorator(scope="module", cache=True, lazy=False)

        def sample_func():
            return "test_result"

        decorated_func = decorator(sample_func)

        # 验证装饰器设置的属性
        assert decorated_func._scope == "module"
        assert decorated_func._cache_enabled is True
        assert decorated_func._lazy_support is False
        assert decorated_func._decorator_args["scope"] == "module"


class TestParamGenerator:
    """param_generator函数的测试类"""

    def test_function_style_no_args(self):
        """测试param_generator函数风格 - 无参数"""

        def sample_func():
            return "test"

        decorated_func = param_generator(sample_func)

        assert hasattr(decorated_func, "_is_param_generator")
        assert decorated_func._is_param_generator is True
        assert decorated_func._decorator_args["scope"] == "function"

    def test_function_style_with_args(self):
        """测试param_generator函数风格 - 有参数"""

        def sample_func():
            return "test"

        decorated_func = param_generator(scope="session")(sample_func)

        assert hasattr(decorated_func, "_is_param_generator")
        assert decorated_func._is_param_generator is True
        assert decorated_func._decorator_args["scope"] == "session"

    def test_function_style_with_multiple_args(self):
        """测试param_generator函数风格 - 多个参数"""

        def sample_func():
            return "test"

        decorated_func = param_generator(scope="class", cache=False, lazy=False)(
            sample_func
        )

        assert hasattr(decorated_func, "_is_param_generator")
        assert decorated_func._is_param_generator is True
        assert decorated_func._decorator_args["scope"] == "class"
        assert decorated_func._decorator_args["cache_enabled"] is False
        assert decorated_func._decorator_args["lazy_support"] is False


class TestWithDynamicParams:
    """with_dynamic_params装饰器的测试类"""

    def test_decorator(self):
        """测试with_dynamic_params装饰器"""

        # 创建一个生成器函数
        @param_generator
        def sample_generator():
            return "generated_value"

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 使用with_dynamic_params装饰测试函数
        decorated_func = with_dynamic_params(dynamic_param=sample_generator)(test_func)

        # 验证装饰后的函数具有正确的属性
        assert hasattr(decorated_func, "_mapping")
        assert hasattr(decorated_func, "_requires")
        assert decorated_func._requires is True
        assert "dynamic_param" in decorated_func._mapping
        assert decorated_func._mapping["dynamic_param"] == sample_generator

    def test_decorator_validation(self):
        """测试with_dynamic_params装饰器验证功能"""

        def invalid_generator():  # 这不是一个用@param_generator装饰的函数
            return "not_a_generator"

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 应该抛出ValueError，因为invalid_generator不是用@param_generator装饰的
        with pytest.raises(ValueError):
            with_dynamic_params(dynamic_param=invalid_generator)(test_func)

    def test_callable_validation(self):
        """测试with_dynamic_params装饰器的可调用性验证"""

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 应该抛出ValueError，因为字符串不是可调用的
        with pytest.raises(ValueError):
            with_dynamic_params(dynamic_param="not_callable")(test_func)

    def test_multiple_params(self):
        """测试with_dynamic_params装饰器多参数"""

        @param_generator
        def generator1():
            return "value1"

        @param_generator
        def generator2():
            return "value2"

        def test_func(param1, param2):
            return f"{param1}, {param2}"

        decorated_func = with_dynamic_params(param1=generator1, param2=generator2)(
            test_func
        )

        assert "param1" in decorated_func._mapping
        assert "param2" in decorated_func._mapping
        assert decorated_func._mapping["param1"] == generator1
        assert decorated_func._mapping["param2"] == generator2

    def test_with_dynamic_params_wrapper_preserves_name(self):
        """测试with_dynamic_params装饰器保持函数名称"""

        @param_generator
        def sample_generator():
            return "generated_value"

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 使用with_dynamic_params装饰测试函数
        decorated_func = with_dynamic_params(dynamic_param=sample_generator)(test_func)

        # 验证装饰后的函数保持原始名称
        assert decorated_func.__name__ == test_func.__name__
