"""装饰器模块的单元测试"""

import pytest

from dynamic_params import generator, use_generators
from dynamic_params.public.decorators.generator import _GeneratorDecorator


class TestGeneratorDecorator:
    """_GeneratorDecorator类的测试类"""

    def test_initialization(self):
        """测试_GeneratorDecorator初始化"""
        decorator = _GeneratorDecorator(scope="session", cache=False, lazy=False)

        assert decorator.scope == "session"
        assert decorator.cache_enabled is False
        assert decorator.lazy_support is False

    def test_default_values(self):
        """测试_GeneratorDecorator默认值"""
        decorator = _GeneratorDecorator()

        assert decorator.scope == "function"
        assert decorator.cache_enabled is True
        assert decorator.lazy_support is True

    def test_call(self):
        """测试_GeneratorDecorator调用"""
        decorator = _GeneratorDecorator(scope="class", cache=False, lazy=True)

        def sample_func(x):
            return x * 2

        decorated_func = decorator(sample_func)

        # 检查装饰后的函数是否具有预期的属性
        assert hasattr(decorated_func, "_is_generator")
        assert decorated_func._is_generator is True
        assert hasattr(decorated_func, "_decorator_args")
        assert decorated_func._decorator_args["scope"] == "class"
        assert decorated_func._decorator_args["cache_enabled"] is False
        assert decorated_func._decorator_args["lazy_support"] is True

    def test_function_wrapping(self):
        """测试装饰器功能包装"""
        decorator = _GeneratorDecorator(scope="module", cache=True, lazy=False)

        def sample_func():
            return "test_result"

        decorated_func = decorator(sample_func)

        # 验证装饰器设置的属性
        assert decorated_func._scope == "module"
        assert decorated_func._cache_enabled is True
        assert decorated_func._lazy_support is False
        assert decorated_func._decorator_args["scope"] == "module"


class TestGenerator:
    """generator函数的测试类"""

    def test_function_style_no_args(self):
        """测试generator函数风格 - 无参数"""

        def sample_func():
            return "test"

        decorated_func = generator(sample_func)

        assert hasattr(decorated_func, "_is_generator")
        assert decorated_func._is_generator is True
        assert decorated_func._decorator_args["scope"] == "function"

    def test_function_style_with_args(self):
        """测试generator函数风格 - 有参数"""

        def sample_func():
            return "test"

        decorated_func = generator(scope="session")(sample_func)

        assert hasattr(decorated_func, "_is_generator")
        assert decorated_func._is_generator is True
        assert decorated_func._decorator_args["scope"] == "session"

    def test_function_style_with_multiple_args(self):
        """测试generator函数风格 - 多个参数"""

        def sample_func():
            return "test"

        decorated_func = generator(scope="class", cache=False, lazy=False)(sample_func)

        assert hasattr(decorated_func, "_is_generator")
        assert decorated_func._is_generator is True
        assert decorated_func._decorator_args["scope"] == "class"
        assert decorated_func._decorator_args["cache_enabled"] is False
        assert decorated_func._decorator_args["lazy_support"] is False

    def test_generator_decorator_calls_original(self):
        """测试generator装饰器的包装函数调用原始函数"""
        call_count = 0

        @generator
        def sample_func():
            nonlocal call_count
            call_count += 1
            return "test"

        # 调用包装函数
        result = sample_func()
        assert result == "test"
        assert call_count == 1

    def test_generator_decorator_preserves_function_name(self):
        """测试generator装饰器保留函数名称"""

        @generator
        def custom_generator():
            return "test"

        assert custom_generator.__name__ == "custom_generator"

    def test_generator_decorator_with_session_scope(self):
        """测试generator装饰器使用session作用域"""

        @generator(scope="session")
        def session_generator():
            return "session_value"

        assert hasattr(session_generator, "_is_generator")
        assert session_generator._is_generator is True
        assert session_generator._scope == "session"

    def test_generator_decorator_with_cache_disabled(self):
        """测试generator装饰器禁用缓存"""

        @generator(cache=False)
        def no_cache_generator():
            return "no_cache_value"

        assert hasattr(no_cache_generator, "_is_generator")
        assert no_cache_generator._is_generator is True
        assert no_cache_generator._cache_enabled is False

    def test_generator_decorator_with_lazy_disabled(self):
        """测试generator装饰器禁用延迟加载"""

        @generator(lazy=False)
        def no_lazy_generator():
            return "no_lazy_value"

        assert hasattr(no_lazy_generator, "_is_generator")
        assert no_lazy_generator._is_generator is True
        assert no_lazy_generator._lazy_support is False


class TestUseGenerators:
    """use_generators装饰器的测试类"""

    def test_decorator(self):
        """测试use_generators装饰器"""

        # 创建一个生成器函数
        @generator
        def sample_generator():
            return "generatorerated_value"

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 使用use_generators装饰测试函数
        decorated_func = use_generators(dynamic_param=sample_generator)(test_func)

        # 验证装饰后的函数具有正确的属性
        assert hasattr(decorated_func, "_mapping")
        assert hasattr(decorated_func, "_is_mapped")
        assert decorated_func._is_mapped is True
        assert "dynamic_param" in decorated_func._mapping
        assert decorated_func._mapping["dynamic_param"] == sample_generator

    def test_decorator_validation(self):
        """测试use_generators装饰器验证功能"""

        def invalid_generator():  # 这不是一个用@generator装饰的函数
            return "not_a_generator"

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 应该抛出InvalidGeneratorError，因为invalid_generator不是用@generator 装饰的
        from dynamic_params import InvalidGeneratorError

        with pytest.raises(InvalidGeneratorError):
            use_generators(dynamic_param=invalid_generator)(test_func)

    def test_callable_validation(self):
        """测试use_generators装饰器的可调用性验证"""

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 应该抛出ValueError，因为字符串不是可调用的
        with pytest.raises(ValueError):
            use_generators(dynamic_param="not_callable")(test_func)

    def test_multiple_params(self):
        """测试use_generators装饰器多参数"""

        @generator
        def generator1():
            return "value1"

        @generator
        def generator2():
            return "value2"

        def test_func(param1, param2):
            return f"{param1}, {param2}"

        decorated_func = use_generators(param1=generator1, param2=generator2)(test_func)

        assert "param1" in decorated_func._mapping
        assert "param2" in decorated_func._mapping
        assert decorated_func._mapping["param1"] == generator1
        assert decorated_func._mapping["param2"] == generator2

    def test_use_generators_wrapper_preserves_name(self):
        """测试use_generators装饰器保持函数名称"""

        @generator
        def sample_generator():
            return "generatorerated_value"

        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 使用use_generators装饰测试函数
        decorated_func = use_generators(dynamic_param=sample_generator)(test_func)

        # 验证装饰后的函数保持原始名称
        assert decorated_func.__name__ == test_func.__name__

    def test_use_generators_wrapper_calls_original(self):
        """测试use_generators装饰器的包装函数调用原始函数"""
        call_count = 0

        @generator
        def sample_generator():
            return "test_value"

        def test_func(dynamic_param):
            nonlocal call_count
            call_count += 1
            return f"result: {dynamic_param}"

        # 使用use_generators装饰测试函数
        decorated_func = use_generators(dynamic_param=sample_generator)(test_func)

        # 调用包装函数
        result = decorated_func("test_value")
        assert result == "result: test_value"
        assert call_count == 1

    def test_use_generators_preserves_pytestmark(self):
        """测试use_generators装饰器保留pytestmark"""
        import pytest

        @generator
        def sample_generator():
            return "test_value"

        @pytest.mark.skip
        def test_func(dynamic_param):
            return f"result: {dynamic_param}"

        # 使用use_generators装饰测试函数
        decorated_func = use_generators(dynamic_param=sample_generator)(test_func)

        # 验证装饰后的函数保留pytestmark
        assert hasattr(decorated_func, "pytestmark")
        assert len(decorated_func.pytestmark) == 2  # 原始的skip标记 + use_generators标记
