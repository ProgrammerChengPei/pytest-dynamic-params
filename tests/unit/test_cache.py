# Test GeneratorCache functionality

import pytest
from dynamic_params.engine.generator.cache import GeneratorCache


class TestGeneratorCache:
    """Test GeneratorCache class"""
    
    def test_cache_init(self):
        """Test GeneratorCache initialization"""
        cache = GeneratorCache()
        assert "function" in cache._cache
        assert "class" in cache._cache
        assert "module" in cache._cache
        assert "session" in cache._cache
    
    def test_cache_set_and_get(self):
        """Test cache set and get"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        result = cache.get("function", "key1")
        assert result == "value1"
    
    def test_cache_get_not_found(self):
        """Test cache get with non-existent key"""
        cache = GeneratorCache()
        result = cache.get("function", "nonexistent")
        assert result is None
    
    def test_cache_get_invalid_scope(self):
        """Test cache get with invalid scope"""
        cache = GeneratorCache()
        result = cache.get("invalid_scope", "key1")
        assert result is None
    
    def test_cache_set_invalid_scope(self):
        """Test cache set with invalid scope"""
        cache = GeneratorCache()
        cache.set("invalid_scope", "key1", "value1")
        result = cache.get("invalid_scope", "key1")
        assert result == "value1"
    
    def test_cache_clear_scope(self):
        """Test cache clear with specific scope"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("class", "key2", "value2")
        cache.clear("function")
        assert cache.get("function", "key1") is None
        assert cache.get("class", "key2") == "value2"
    
    def test_cache_clear_all(self):
        """Test cache clear all scopes"""
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
    
    def test_cache_get_cache_size_scope(self):
        """Test get_cache_size with specific scope"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("function", "key2", "value2")
        cache.set("class", "key3", "value3")
        size = cache.get_cache_size("function")
        assert size == 2
    
    def test_cache_get_cache_size_all(self):
        """Test get_cache_size with all scopes"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("class", "key2", "value2")
        cache.set("module", "key3", "value3")
        cache.set("session", "key4", "value4")
        size = cache.get_cache_size()
        assert size == 4
    
    def test_cache_get_cache_size_invalid_scope(self):
        """Test get_cache_size with invalid scope"""
        cache = GeneratorCache()
        size = cache.get_cache_size("invalid_scope")
        assert size == 0
    
    def test_cache_overwrite(self):
        """Test cache overwrite"""
        cache = GeneratorCache()
        cache.set("function", "key1", "value1")
        cache.set("function", "key1", "value2")
        result = cache.get("function", "key1")
        assert result == "value2"
    
    def test_cache_different_types(self):
        """Test cache with different types of values"""
        cache = GeneratorCache()
        cache.set("function", "int", 42)
        cache.set("function", "str", "hello")
        cache.set("function", "list", [1, 2, 3])
        cache.set("function", "dict", {"a": 1})
        cache.set("function", "tuple", (1, 2))
        
        assert cache.get("function", "int") == 42
        assert cache.get("function", "str") == "hello"
        assert cache.get("function", "list") == [1, 2, 3]
        assert cache.get("function", "dict") == {"a": 1}
        assert cache.get("function", "tuple") == (1, 2)
