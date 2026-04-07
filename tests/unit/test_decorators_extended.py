# Test decorators module

import warnings

import pytest
from dynamic_params.engine.generator.base import GeneratorBase
from dynamic_params.engine.generator.lazy import LazyGenerator
from dynamic_params.engine.generator.registry import registry as generator_registry
from dynamic_params.public.decorators.param_generator import param_generator
from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture
from dynamic_params.public.decorators.parametrize_generator import parametrize_generator
from dynamic_params.public.decorators.parametrize_test import parametrize_test


class TestParametrizeTestDecorator:
    """Test parametrize_test decorator"""
    
    def test_parametrize_test_basic(self):
        """Test parametrize_test with basic arguments"""
        @parametrize_test("a,b", [[1, 2], [3, 4]])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_empty_args(self):
        """Test parametrize_test with empty argvalues"""
        @parametrize_test("a", [])
        def test_func(a):
            return a
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_single_arg(self):
        """Test parametrize_test with single argument"""
        @parametrize_test("a", [[1]])
        def test_func(a):
            return a
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_kwargs(self):
        """Test parametrize_test with keyword arguments"""
        @parametrize_test("a,b", [[1, 2]], ids=["test1"])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_multiple_params(self):
        """Test parametrize_test with multiple parameters"""
        @parametrize_test("a,b,c", [[1, 2, 3], [4, 5, 6]])
        def test_func(a, b, c):
            return a + b + c
        
        assert hasattr(test_func, "_dynamic_parametrize")


class TestParametrizeFixtureDecorator:
    """Test parametrize_fixture decorator"""
    
    def test_parametrize_fixture_basic(self):
        """Test parametrize_fixture basic usage"""
        def my_fixture(value):
            return value * 2
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3])(my_fixture)
        assert result is not None
    
    def test_parametrize_fixture_with_scope(self):
        """Test parametrize_fixture with scope"""
        def my_fixture(value):
            return value * 2
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3], scope="module")(my_fixture)
        assert result is not None
    
    def test_parametrize_fixture_with_function_scope(self):
        """Test parametrize_fixture with function scope"""
        def my_fixture(value):
            return value * 2
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3], scope="function")(my_fixture)
        assert result is not None
    
    def test_parametrize_fixture_with_class_scope(self):
        """Test parametrize_fixture with class scope"""
        def my_fixture(value):
            return value * 2
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3], scope="class")(my_fixture)
        assert result is not None
    
    def test_parametrize_fixture_with_session_scope(self):
        """Test parametrize_fixture with session scope"""
        def my_fixture(value):
            return value * 2
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3], scope="session")(my_fixture)
        assert result is not None

    def test_parametrize_fixture_with_cache_support(self):
        """Test parametrize_fixture supports cache wrapping"""
        def gen_values():
            yield 1
            yield 2

        def my_fixture(value):
            return value * 2

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", gen_values, cache=True)(my_fixture)

        assert result is not None
        config = result._dynamic_fixture_parametrize[0]
        assert config["argnames"] == "value"
        assert config["argvalues"].__class__.__name__ == "GeneratorBase"

    def test_parametrize_fixture_with_lazy_support(self):
        """Test parametrize_fixture supports lazy wrapping"""
        def gen_values():
            yield 3
            yield 4

        def my_fixture(value):
            return value * 2

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", gen_values, lazy=True)(my_fixture)

        assert result is not None
        config = result._dynamic_fixture_parametrize[0]
        assert config["argnames"] == "value"
        assert config["argvalues"].__class__.__name__ == "LazyGenerator"

    def test_parametrize_fixture_warns_on_pytest_fixture_combination(self):
        """Test parametrize_fixture warns if function is already a pytest fixture"""
        def my_fixture(value):
            return value * 2

        py_fixture = pytest.fixture()(my_fixture)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = parametrize_fixture("value", [1, 2, 3])(py_fixture)

        assert result is not None
        assert any("not supported" in str(warn.message) for warn in w)


class TestParametrizeGeneratorDecorator:
    """Test parametrize_generator decorator"""
    
    def test_parametrize_generator_basic(self):
        """Test parametrize_generator basic usage"""
        def my_generator(start, end):
            for i in range(start, end):
                yield i
        
        result = parametrize_generator("start,end", [[1, 5], [6, 10]])(my_generator)
        assert result is not None
    
    def test_parametrize_generator_with_single_param(self):
        """Test parametrize_generator with single parameter"""
        def my_generator(value):
            yield value
        
        result = parametrize_generator("value", [[1], [2], [3]])(my_generator)
        assert result is not None
    
    def test_parametrize_generator_with_kwargs(self):
        """Test parametrize_generator with keyword arguments"""
        def my_generator(a, b):
            yield a + b
        
        result = parametrize_generator("a,b", [[1, 2], [3, 4]], ids=["test1", "test2"])(my_generator)
        assert result is not None


class TestParamGeneratorDecorator:
    """Test param_generator decorator"""
    
    def test_param_generator_without_parentheses(self):
        """Test param_generator without parentheses"""
        @param_generator
        def my_generator():
            yield 1
            yield 2
        
        assert "my_generator" in generator_registry.list()
        result = my_generator()
        assert result == [1, 2]
    
    def test_param_generator_with_parentheses(self):
        """Test param_generator with parentheses"""
        @param_generator()
        def my_generator():
            yield 1
            yield 2
        
        assert "my_generator" in generator_registry.list()
    
    def test_param_generator_with_scope(self):
        """Test param_generator with scope"""
        @param_generator(scope="session")
        def my_session_generator():
            yield 10
        
        assert "my_session_generator" in generator_registry.list()
    
    def test_param_generator_with_cache(self):
        """Test param_generator with cache"""
        call_count = 0
        
        @param_generator(cache=True)
        def my_cached_generator():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        result1 = my_cached_generator()
        result2 = my_cached_generator()
        
        assert result1 == [1]
        assert result2 == [1]
        assert call_count == 1
    
    def test_param_generator_with_lazy(self):
        """Test param_generator with lazy"""
        @param_generator(lazy=True)
        def my_lazy_generator():
            yield 5
        
        assert "my_lazy_generator" in generator_registry.list()
    
    def test_param_generator_with_all_options(self):
        """Test param_generator with all options"""
        @param_generator(scope="module", cache=True, lazy=False)
        def my_full_generator():
            yield 100
        
        assert "my_full_generator" in generator_registry.list()
    
    def test_param_generator_returns_generator_base(self):
        """Test param_generator returns GeneratorBase when not lazy"""
        @param_generator(lazy=False)
        def my_func():
            yield 1
        
        assert isinstance(my_func, GeneratorBase)
        assert not isinstance(my_func, LazyGenerator)
    
    def test_param_generator_returns_lazy_generator(self):
        """Test param_generator returns LazyGenerator when lazy"""
        @param_generator(lazy=True)
        def my_func():
            yield 1
        
        assert isinstance(my_func, LazyGenerator)
    
    def test_param_generator_registers_correct_name(self):
        """Test param_generator registers generator with correct name"""
        @param_generator
        def my_unique_name_generator():
            yield 1
        
        assert "my_unique_name_generator" in generator_registry.list()
    
    def test_param_generator_function_registry_access(self):
        """Test param_generator can access registered generator"""
        @param_generator
        def my_accessible_generator():
            yield 42
        
        retrieved = generator_registry.get("my_accessible_generator")
        result = retrieved()
        assert result == [42]
    
    def test_param_generator_with_list_return(self):
        """Test param_generator with list return"""
        @param_generator
        def my_list_generator():
            return [1, 2, 3]
        
        result = my_list_generator()
        assert result == [1, 2, 3]
    
    def test_param_generator_with_single_value(self):
        """Test param_generator with single value"""
        @param_generator
        def my_single_generator():
            return 42
        
        result = my_single_generator()
        assert result == [42]
    
    def test_param_generator_with_generator_function(self):
        """Test param_generator with generator function"""
        @param_generator
        def my_gen_func():
            for i in range(5):
                yield i * 2
        
        result = my_gen_func()
        assert result == [0, 2, 4, 6, 8]


# Clean up registry after tests
@pytest.fixture(autouse=True)
def clean_registry():
    """Clean up generator registry before and after tests"""
    original_generators = list(generator_registry._generators.keys())
    
    yield
    
    current_generators = list(generator_registry._generators.keys())
    for name in current_generators:
        if name not in original_generators:
            try:
                generator_registry.unregister(name)
            except:
                pass
