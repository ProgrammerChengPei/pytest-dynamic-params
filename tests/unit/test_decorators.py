# Test public decorators functionality

import pytest
from dynamic_params.public.decorators.parametrize_test import parametrize_test
from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture
from dynamic_params.public.decorators.parametrize_generator import parametrize_generator
from dynamic_params.public.decorators.param_generator import param_generator
from dynamic_params.engine.generator.registry import registry as generator_registry


class TestParametrizeTest:
    """Test parametrize_test decorator"""
    
    def test_parametrize_test_basic(self):
        """Test parametrize_test with basic arguments"""
        @parametrize_test("a,b", [[1, 2], [3, 4]])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")
    
    def test_parametrize_test_with_kwargs(self):
        """Test parametrize_test with kwargs"""
        @parametrize_test("a,b", [[1, 2]], ids=["test1"])
        def test_func(a, b):
            return a + b
        
        assert hasattr(test_func, "_dynamic_parametrize")


class TestParametrizeGenerator:
    """Test parametrize_generator decorator"""
    
    def test_parametrize_generator_basic(self):
        """Test parametrize_generator with basic arguments"""
        @parametrize_generator("start,end", [[1, 5], [6, 10]])
        def my_generator(start, end):
            for i in range(start, end):
                yield i
        
        assert hasattr(my_generator, "pytestmark")


class TestParamGenerator:
    """Test param_generator decorator"""
    
    def test_param_generator_basic(self):
        """Test param_generator with basic function"""
        @param_generator
        def my_generator():
            yield 1
            yield 2
            yield 3
        
        assert "my_generator" in generator_registry.list()
        result = my_generator()
        assert result == [1, 2, 3]
    
    def test_param_generator_with_scope(self):
        """Test param_generator with scope"""
        @param_generator(scope="session")
        def my_session_generator():
            yield 10
            yield 20
        
        assert "my_session_generator" in generator_registry.list()
    
    def test_param_generator_with_cache(self):
        """Test param_generator with cache"""
        @param_generator(cache=True)
        def my_cached_generator():
            yield 100
        
        assert "my_cached_generator" in generator_registry.list()
        result1 = my_cached_generator()
        result2 = my_cached_generator()
        assert result1 == result2
    
    def test_param_generator_with_lazy(self):
        """Test param_generator with lazy loading"""
        @param_generator(lazy=True)
        def my_lazy_generator():
            yield 5
            yield 6
        
        assert "my_lazy_generator" in generator_registry.list()
    
    def test_param_generator_list_result(self):
        """Test param_generator with list result"""
        @param_generator
        def my_list_generator():
            return [7, 8, 9]
        
        result = my_list_generator()
        assert result == [7, 8, 9]
    
    def test_param_generator_single_value(self):
        """Test param_generator with single value"""
        @param_generator
        def my_single_generator():
            return 42
        
        result = my_single_generator()
        assert result == [42]
