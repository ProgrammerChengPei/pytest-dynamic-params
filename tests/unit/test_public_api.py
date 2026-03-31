# Test public decorators and API

import pytest
import warnings
from unittest.mock import patch, Mock
from dynamic_params.public.api import (
    parametrize_test,
    parametrize_fixture,
    parametrize_generator,
    param_generator,
    DynRef,
)
from dynamic_params.public.decorators.parametrize_test import parametrize_test as decorator_parametrize_test
from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture as decorator_parametrize_fixture
from dynamic_params.public.decorators.parametrize_generator import parametrize_generator as decorator_parametrize_generator
from dynamic_params.public.decorators.param_generator import param_generator as decorator_param_generator
from dynamic_params.engine.dependency.dynref import DynRef as engine_DynRef
from dynamic_params.engine.generator.registry import registry as generator_registry


class TestPublicAPI:
    """Test public API exports"""
    
    def test_parametrize_test_export(self):
        """Test that parametrize_test is exported correctly"""
        assert parametrize_test is not None
        assert parametrize_test is decorator_parametrize_test
    
    def test_parametrize_fixture_export(self):
        """Test that parametrize_fixture is exported correctly"""
        assert parametrize_fixture is not None
        assert parametrize_fixture is decorator_parametrize_fixture
    
    def test_parametrize_generator_export(self):
        """Test that parametrize_generator is exported correctly"""
        assert parametrize_generator is not None
        assert parametrize_generator is decorator_parametrize_generator
    
    def test_param_generator_export(self):
        """Test that param_generator is exported correctly"""
        assert param_generator is not None
        assert param_generator is decorator_param_generator
    
    def test_dynref_export(self):
        """Test that DynRef is exported correctly"""
        assert DynRef is not None
        assert DynRef is engine_DynRef


class TestParametrizeTestDecorator:
    """Test parametrize_test decorator"""
    
    def test_parametrize_test_with_args(self):
        """Test parametrize_test with arguments"""
        @parametrize_test("a,b", [[1, 2], [3, 4]])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_kwargs(self):
        """Test parametrize_test with keyword arguments"""
        @parametrize_test("a,b", [[1, 2]], ids=["test1"])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_no_args(self):
        """Test parametrize_test with no arguments should not raise error"""
        def test_func(a, b):
            return a + b
        
        # Should not raise when used as decorator
        result = parametrize_test("a,b", [[1, 2]])(test_func)
        assert result is not None


class TestParamGeneratorDecorator:
    """Test param_generator decorator"""
    
    def test_param_generator_basic(self):
        """Test param_generator with basic function"""
        @param_generator
        def my_generator():
            yield 1
            yield 2
        
        assert "my_generator" in generator_registry.list()
        result = my_generator()
        assert result == [1, 2]
    
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
        """Test param_generator with lazy loading"""
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
    
    def test_param_generator_with_generator(self):
        """Test param_generator with generator function"""
        @param_generator
        def my_gen_func():
            for i in range(5):
                yield i * 2
        
        result = my_gen_func()
        assert result == [0, 2, 4, 6, 8]


class TestParametrizeFixtureDecorator:
    """Test parametrize_fixture decorator"""
    
    def test_parametrize_fixture_basic(self):
        """Test parametrize_fixture basic usage"""
        def my_fixture(value):
            return value * 2
        
        # Should not raise error, even though it warns
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3])(my_fixture)
        assert result is not None
    
    def test_parametrize_fixture_with_scope(self):
        """Test parametrize_fixture with scope"""
        def my_fixture(value):
            return value * 2
        
        # Should not raise error, even though it warns
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = parametrize_fixture("value", [1, 2, 3], scope="module")(my_fixture)
        assert result is not None


class TestParametrizeGeneratorDecorator:
    """Test parametrize_generator decorator"""
    
    def test_parametrize_generator_basic(self):
        """Test parametrize_generator basic usage"""
        def my_generator(start, end):
            for i in range(start, end):
                yield i
        
        result = parametrize_generator("start,end", [[1, 5], [6, 10]])(my_generator)
        assert result is not None


class TestDynRefAPIAccess:
    """Test DynRef API access"""
    
    def test_dynref_creation(self):
        """Test creating DynRef instance through public API"""
        ref = DynRef("test_param")
        assert ref.name == "test_param"
    
    def test_dynref_resolution(self):
        """Test DynRef resolution through public API"""
        ref = DynRef("a")
        context = {"a": 42}
        result = ref.resolve(context)
        assert result == 42
    
    def test_dynref_operators(self):
        """Test DynRef operators through public API"""
        a = DynRef("a")
        b = DynRef("b")
        
        expr = a + b
        context = {"a": 10, "b": 20}
        result = expr.resolve(context)
        assert result == 30


class TestPublicModuleStructure:
    """Test public module structure"""
    
    def test_public_init_has_all_exports(self):
        """Test that public/__init__.py has all expected exports"""
        import dynamic_params.public
        
        # Check that all expected symbols are in __all__
        expected_exports = [
            "parametrize_test",
            "parametrize_fixture",
            "parametrize_generator",
            "param_generator",
            "DynRef",
        ]
        
        for export in expected_exports:
            assert export in dynamic_params.public.__all__
    
    def test_api_has_all_exports(self):
        """Test that public/api.py has all expected exports"""
        import dynamic_params.public.api
        
        expected_exports = [
            "parametrize_test",
            "parametrize_fixture",
            "parametrize_generator",
            "param_generator",
            "DynRef",
        ]
        
        for export in expected_exports:
            assert export in dynamic_params.public.api.__all__
    
    def test_main_module_exports(self):
        """Test that main module exports public API"""
        import dynamic_params
        
        expected_exports = [
            "parametrize_test",
            "parametrize_fixture",
            "parametrize_generator",
            "param_generator",
            "DynRef",
        ]
        
        for export in expected_exports:
            assert hasattr(dynamic_params, export)


# Clean up registry after tests
@pytest.fixture(autouse=True)
def clean_registry():
    """Clean up generator registry before and after tests"""
    # Save original generators
    original_generators = list(generator_registry._generators.keys())
    
    yield
    
    # Clean up test generators
    current_generators = list(generator_registry._generators.keys())
    for name in current_generators:
        if name not in original_generators:
            generator_registry.unregister(name)
