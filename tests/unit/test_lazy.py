# Test LazyGenerator functionality

import pytest
from dynamic_params.engine.generator.lazy import LazyGenerator
from dynamic_params.engine.generator.base import GeneratorBase


class TestLazyGenerator:
    """Test LazyGenerator class"""
    
    def test_lazy_generator_init(self):
        """Test LazyGenerator initialization"""
        def test_func():
            yield 1
        
        generator = LazyGenerator(test_func)
        assert generator._cached_result is None
        assert generator._executed is False
    
    def test_lazy_generator_first_execution(self):
        """Test LazyGenerator first execution"""
        def test_func():
            yield 1
            yield 2
            yield 3
        
        generator = LazyGenerator(test_func)
        result = generator.execute()
        
        assert result == [1, 2, 3]
        assert generator._executed is True
        assert generator._cached_result == [1, 2, 3]
    
    def test_lazy_generator_second_execution(self):
        """Test LazyGenerator second execution (cached)"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        generator = LazyGenerator(test_func)
        
        # First execution
        result1 = generator.execute()
        assert result1 == [1]
        assert call_count == 1
        
        # Second execution (should use cache)
        result2 = generator.execute()
        assert result2 == [1]
        assert call_count == 1  # Function should not be called again
    
    def test_lazy_generator_reset(self):
        """Test LazyGenerator reset"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        generator = LazyGenerator(test_func)
        
        # First execution
        result1 = generator.execute()
        assert result1 == [1]
        
        # Reset
        generator.reset()
        assert generator._cached_result is None
        assert generator._executed is False
        
        # Second execution (should execute again)
        result2 = generator.execute()
        assert result2 == [2]
        assert call_count == 2
    
    def test_lazy_generator_with_args(self):
        """Test LazyGenerator with arguments"""
        def test_func(x, y):
            yield x + y
        
        generator = LazyGenerator(test_func)
        result = generator.execute(5, 3)
        
        assert result == [8]
    
    def test_lazy_generator_with_kwargs(self):
        """Test LazyGenerator with keyword arguments"""
        def test_func(x, y=10):
            yield x + y
        
        generator = LazyGenerator(test_func)
        result = generator.execute(5, y=20)
        
        assert result == [25]
    
    def test_lazy_generator_caching(self):
        """Test LazyGenerator caching behavior"""
        def test_func():
            return [1, 2, 3]
        
        generator = LazyGenerator(test_func, cache=True)
        
        result1 = generator.execute()
        result2 = generator.execute()
        
        assert result1 == result2
    
    def test_lazy_generator_scope(self):
        """Test LazyGenerator with different scopes"""
        def test_func():
            yield 1
        
        generator_function = LazyGenerator(test_func, scope="function")
        generator_class = LazyGenerator(test_func, scope="class")
        generator_module = LazyGenerator(test_func, scope="module")
        generator_session = LazyGenerator(test_func, scope="session")
        
        assert generator_function.scope == "function"
        assert generator_class.scope == "class"
        assert generator_module.scope == "module"
        assert generator_session.scope == "session"
    
    def test_lazy_generator_empty_result(self):
        """Test LazyGenerator with empty result"""
        def test_func():
            return []
        
        generator = LazyGenerator(test_func)
        result = generator.execute()
        
        assert result == []
    
    def test_lazy_generator_single_value(self):
        """Test LazyGenerator with single value"""
        def test_func():
            return 42
        
        generator = LazyGenerator(test_func)
        result = generator.execute()
        
        assert result == [42]
    
    def test_lazy_generator_list_return(self):
        """Test LazyGenerator with list return"""
        def test_func():
            return [1, 2, 3]
        
        generator = LazyGenerator(test_func)
        result = generator.execute()
        
        assert result == [1, 2, 3]
    
    def test_lazy_generator_generator_return(self):
        """Test LazyGenerator with generator return"""
        def test_func():
            yield from [4, 5, 6]
        
        generator = LazyGenerator(test_func)
        result = generator.execute()
        
        assert result == [4, 5, 6]
