# Test decorators and public API imports

import pytest
from unittest.mock import patch, MagicMock
from dynamic_params.public.decorators.parametrize_test import parametrize_test
from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture
from dynamic_params.public.decorators.parametrize_generator import parametrize_generator
from dynamic_params.public.decorators.param_generator import param_generator
from dynamic_params.public.api import (
    parametrize_test as api_parametrize_test,
    parametrize_fixture as api_parametrize_fixture,
    parametrize_generator as api_parametrize_generator,
    param_generator as api_param_generator,
    DynRef as api_DynRef,
)


class TestPublicAPIImports:
    """Test public API imports from api.py"""
    
    def test_api_decorators_match(self):
        """Test that decorators from api.py match direct imports"""
        assert api_parametrize_test is parametrize_test
        assert api_parametrize_fixture is parametrize_fixture
        assert api_parametrize_generator is parametrize_generator
        assert api_param_generator is param_generator
    
    def test_api_dynref_match(self):
        """Test that DynRef from api.py matches"""
        from dynamic_params.engine.dependency.dynref import DynRef
        assert api_DynRef is DynRef


class TestParametrizeTestDecoratorExecution:
    """Test parametrize_test decorator execution paths"""
    
    def test_parametrize_test_decorator_no_args(self):
        """Test parametrize_test decorator with basic use case"""
        @parametrize_test("x", [1, 2, 3])
        def test_func(x):
            return x
        
        # Verify the decorator is applied
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_ids(self):
        """Test parametrize_test with ids"""
        @parametrize_test("x", [1, 2, 3], ids=["one", "two", "three"])
        def test_func(x):
            return x
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_multiple_params(self):
        """Test parametrize_test with multiple parameters"""
        @parametrize_test("a,b", [[1, 2], [3, 4]])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")


class TestParametrizeFixtureDecoratorExecution:
    """Test parametrize_fixture decorator execution paths"""
    
    def test_parametrize_fixture_decorator(self):
        """Test parametrize_fixture decorator basic usage"""
        def my_fixture(value):
            return value * 2
        
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3])(my_fixture)
        
        assert result is not None
    
    def test_parametrize_fixture_with_scopes(self):
        """Test parametrize_fixture with various scopes"""
        scopes = ["function", "class", "module", "session"]
        
        def my_fixture(value):
            return value
        
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for scope in scopes:
                result = parametrize_fixture("value", [1], scope=scope)(my_fixture)
                assert result is not None


class TestParametrizeGeneratorDecoratorExecution:
    """Test parametrize_generator decorator execution paths"""
    
    def test_parametrize_generator_decorator(self):
        """Test parametrize_generator decorator basic usage"""
        def my_generator(start, end):
            for i in range(start, end):
                yield i
        
        result = parametrize_generator("start,end", [[1, 5], [6, 10]])(my_generator)
        assert result is not None
    
    def test_parametrize_generator_single_param(self):
        """Test parametrize_generator with single parameter"""
        def my_generator(value):
            yield value
        
        result = parametrize_generator("value", [[1], [2], [3]])(my_generator)
        assert result is not None


class TestParamGeneratorDecoratorComprehensive:
    """Comprehensive test for param_generator decorator"""
    
    def test_param_generator_direct(self):
        """Test param_generator without parentheses"""
        @param_generator
        def my_gen():
            yield 1
            yield 2
        
        result = my_gen()
        assert result == [1, 2]
    
    def test_param_generator_with_parentheses(self):
        """Test param_generator with parentheses"""
        @param_generator()
        def my_gen2():
            yield 3
            yield 4
        
        result = my_gen2()
        assert result == [3, 4]
    
    def test_param_generator_with_scope(self):
        """Test param_generator with scope parameter"""
        @param_generator(scope="session")
        def my_session_gen():
            yield 10
        
        result = my_session_gen()
        assert result == [10]
    
    def test_param_generator_with_cache(self):
        """Test param_generator with cache parameter"""
        call_count = 0
        
        @param_generator(cache=True)
        def cached_gen():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        result1 = cached_gen()
        result2 = cached_gen()
        
        assert result1 == [1]
        assert result2 == [1]
        assert call_count == 1
    
    def test_param_generator_with_lazy(self):
        """Test param_generator with lazy parameter"""
        from dynamic_params.engine.generator.lazy import LazyGenerator
        from dynamic_params.engine.generator.base import GeneratorBase
        
        @param_generator(lazy=True)
        def lazy_gen():
            yield 42
        
        assert isinstance(lazy_gen, LazyGenerator)
        
        @param_generator(lazy=False)
        def eager_gen():
            yield 43
        
        assert isinstance(eager_gen, GeneratorBase)
        assert not isinstance(eager_gen, LazyGenerator)
    
    def test_param_generator_with_all_options(self):
        """Test param_generator with all possible options"""
        @param_generator(scope="module", cache=True, lazy=False)
        def full_options_gen():
            yield "test"
        
        result = full_options_gen()
        assert result == ["test"]
    
    def test_param_generator_function_name_registration(self):
        """Test that param_generator registers with correct function name"""
        from dynamic_params.engine.generator.registry import registry
        
        @param_generator
        def uniquely_named_function():
            yield 1
        
        assert "uniquely_named_function" in registry.list()
        
        # Clean up
        registry.unregister("uniquely_named_function")


class TestDecoratorImports:
    """Test direct imports from decorators module"""
    
    def test_all_decorators_available(self):
        """Test that all decorators are available from public module"""
        from dynamic_params.public.decorators import (
            parametrize_test,
            parametrize_fixture,
            parametrize_generator,
            param_generator,
        )
        
        assert parametrize_test is not None
        assert parametrize_fixture is not None
        assert parametrize_generator is not None
        assert param_generator is not None


@pytest.fixture(autouse=True)
def cleanup_registry():
    """Clean up registry after tests"""
    from dynamic_params.engine.generator.registry import registry
    original = list(registry._generators.keys())
    yield
    for name in list(registry._generators.keys()):
        if name not in original:
            registry.unregister(name)
