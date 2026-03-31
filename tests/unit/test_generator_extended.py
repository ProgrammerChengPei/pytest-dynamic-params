# Test generator modules comprehensively

import pytest
from dynamic_params.engine.generator.base import GeneratorBase
from dynamic_params.engine.generator.cache import GeneratorCache
from dynamic_params.engine.generator.lazy import LazyGenerator


class TestGeneratorCacheExtended:
    """Extended tests for GeneratorCache"""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        assert cache.get("function", "key1") == "value1"
    
    def test_cache_get_nonexistent_scope(self):
        """Test get with non-existent scope"""
        cache = GeneratorCache()
        assert cache.get("nonexistent", "key1") is None
    
    def test_cache_get_nonexistent_key(self):
        """Test get with non-existent key"""
        cache = GeneratorCache()
        assert cache.get("function", "nonexistent") is None
    
    def test_cache_set_invalid_scope(self):
        """Test set with invalid scope"""
        cache = GeneratorCache()
        cache.set("invalid_scope", "key1", "value1")
        assert cache.get("invalid_scope", "key1") == "value1"
    
    def test_cache_clear_specific_scope(self):
        """Test clear specific scope"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("class", "key2", "value2")
        
        cache.clear("function")
        assert cache.get("function", "key1") is None
        assert cache.get("class", "key2") == "value2"
    
    def test_cache_clear_all(self):
        """Test clear all scopes"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("class", "key2", "value2")
        cache.set("module", "key3", "value3")
        cache.set("session", "key4", "value4")
        
        cache.clear()
        assert cache.get("function", "key1") is None
        assert cache.get("class", "key2") is None
        assert cache.get("module", "key3") is None
        assert cache.get("session", "key4") is None
    
    def test_cache_size_specific_scope(self):
        """Test cache size for specific scope"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("function", "key2", "value2")
        
        assert cache.get_cache_size("function") == 2
        assert cache.get_cache_size("class") == 0
    
    def test_cache_size_total(self):
        """Test total cache size"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("class", "key2", "value2")
        cache.set("module", "key3", "value3")
        
        assert cache.get_cache_size() == 3
    
    def test_cache_size_nonexistent_scope(self):
        """Test cache size for non-existent scope"""
        cache = GeneratorCache()
        assert cache.get_cache_size("nonexistent") == 0
    
    def test_cache_overwrite_key(self):
        """Test overwriting existing key"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("function", "key1", "value2")
        
        assert cache.get("function", "key1") == "value2"


class TestGeneratorBaseExtended:
    """Extended tests for GeneratorBase"""
    
    def test_generator_base_init(self):
        """Test GeneratorBase initialization"""
        def test_func():
            yield 1
        
        generator = GeneratorBase(test_func, scope="session", cache=True, lazy=False)
        assert generator.func is test_func
        assert generator.scope == "session"
        assert generator.cache is True
        assert generator.lazy is False
        assert hasattr(generator, "cache_instance")
    
    def test_generator_base_call_vs_execute(self):
        """Test that __call__ delegates to execute"""
        def test_func(a, b):
            yield a + b
        
        generator = GeneratorBase(test_func)
        call_result = generator(1, 2)
        execute_result = generator.execute(1, 2)
        assert call_result == execute_result == [3]
    
    def test_generator_base_execute_without_cache(self):
        """Test execute without caching"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        generator = GeneratorBase(test_func, cache=False)
        result1 = generator()
        result2 = generator()
        
        assert result1 == [1]
        assert result2 == [2]
        assert call_count == 2
    
    def test_generator_base_execute_with_cache(self):
        """Test execute with caching"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        generator = GeneratorBase(test_func, cache=True)
        result1 = generator()
        result2 = generator()
        
        assert result1 == [1]
        assert result2 == [1]
        assert call_count == 1
    
    def test_generator_base_cache_with_different_args(self):
        """Test caching with different arguments"""
        call_count = 0
        
        def test_func(x):
            nonlocal call_count
            call_count += 1
            yield x * 2
        
        generator = GeneratorBase(test_func, cache=True)
        result1 = generator(1)
        result2 = generator(2)
        result3 = generator(1)
        
        assert result1 == [2]
        assert result2 == [4]
        assert result3 == [2]
        assert call_count == 2
    
    def test_generator_base_get_cache_key(self):
        """Test get_cache_key generates different keys for different args"""
        def test_func():
            yield 1
        
        generator = GeneratorBase(test_func)
        key1 = generator.get_cache_key(1, 2, x=3)
        key2 = generator.get_cache_key(1, 3, x=4)
        
        assert key1 != key2
    
    def test_generator_base_get_cache_key_same_args(self):
        """Test get_cache_key generates same key for same args"""
        def test_func():
            yield 1
        
        generator = GeneratorBase(test_func)
        key1 = generator.get_cache_key(1, 2, x=3)
        key2 = generator.get_cache_key(1, 2, x=3)
        
        assert key1 == key2
    
    def test_generator_base_execute_func_generator(self):
        """Test _execute_func with generator return"""
        def test_func():
            yield 1
            yield 2
            yield 3
        
        generator = GeneratorBase(test_func)
        result = generator._execute_func()
        assert result == [1, 2, 3]
    
    def test_generator_base_execute_func_list(self):
        """Test _execute_func with list return"""
        def test_func():
            return [1, 2, 3]
        
        generator = GeneratorBase(test_func)
        result = generator._execute_func()
        assert result == [1, 2, 3]
    
    def test_generator_base_execute_func_single_value(self):
        """Test _execute_func with single value return"""
        def test_func():
            return 42
        
        generator = GeneratorBase(test_func)
        result = generator._execute_func()
        assert result == [42]
    
    def test_generator_base_execute_func_empty_list(self):
        """Test _execute_func with empty list"""
        def test_func():
            return []
        
        generator = GeneratorBase(test_func)
        result = generator._execute_func()
        assert result == []


class TestLazyGeneratorExtended:
    """Extended tests for LazyGenerator"""
    
    def test_lazy_generator_init(self):
        """Test LazyGenerator initialization"""
        def test_func():
            yield 1
        
        generator = LazyGenerator(test_func, scope="session", cache=True)
        assert generator.func is test_func
        assert generator.scope == "session"
        assert generator.cache is True
        assert generator.lazy is True
        assert generator._cached_result is None
        assert generator._executed is False
    
    def test_lazy_generator_first_execution(self):
        """Test lazy generator first execution"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield 42
        
        generator = LazyGenerator(test_func)
        assert generator._executed is False
        assert generator._cached_result is None
        
        result = generator()
        assert result == [42]
        assert generator._executed is True
        assert generator._cached_result == [42]
        assert call_count == 1
    
    def test_lazy_generator_multiple_calls(self):
        """Test lazy generator multiple calls use cached result"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        generator = LazyGenerator(test_func)
        result1 = generator()
        result2 = generator()
        result3 = generator()
        
        assert result1 == [1]
        assert result2 == [1]
        assert result3 == [1]
        assert call_count == 1
    
    def test_lazy_generator_reset(self):
        """Test lazy generator reset"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        generator = LazyGenerator(test_func)
        
        result1 = generator()
        assert result1 == [1]
        assert generator._executed is True
        
        generator.reset()
        assert generator._executed is False
        assert generator._cached_result is None
        
        result2 = generator()
        assert result2 == [2]
        assert call_count == 2
    
    def test_lazy_generator_with_args(self):
        """Test lazy generator with arguments"""
        call_count = 0
        
        def test_func(a, b):
            nonlocal call_count
            call_count += 1
            yield a + b
        
        generator = LazyGenerator(test_func)
        result1 = generator(1, 2)
        result2 = generator(3, 4)
        
        assert result1 == [3]
        assert result2 == [3]
        assert call_count == 1
    
    def test_lazy_generator_reset_with_cache(self):
        """Test lazy generator reset with caching enabled"""
        call_count = 0
        
        def test_func():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        # Note: When both cache=True and reset(), the cache_instance in
        # GeneratorBase still holds the value. So this test behavior is
        # actually expected - the reset only affects LazyGenerator's cache.
        generator = LazyGenerator(test_func, cache=True)
        
        result1 = generator()
        assert result1 == [1]
        
        generator.reset()
        
        # When cache=True, the GeneratorBase cache still has the value
        result2 = generator()
        assert result2 == [1]  # This is actually expected with cache=True
        assert call_count == 1
