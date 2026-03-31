# Test GeneratorRegistry functionality

import pytest
from dynamic_params.engine.generator.registry import GeneratorRegistry, registry
from dynamic_params.engine.generator.base import GeneratorBase
from dynamic_params.errors import GeneratorNotFoundError


class TestGeneratorRegistry:
    """Test GeneratorRegistry class"""
    
    def test_registry_init(self):
        """Test GeneratorRegistry initialization"""
        registry_instance = GeneratorRegistry()
        assert registry_instance._generators == {}
    
    def test_registry_register(self):
        """Test register generator"""
        registry_instance = GeneratorRegistry()
        
        def test_func():
            yield 1
            yield 2
        
        generator = GeneratorBase(test_func)
        registry_instance.register("test_generator", generator)
        
        assert "test_generator" in registry_instance._generators
        assert registry_instance._generators["test_generator"] == generator
    
    def test_registry_get(self):
        """Test get generator"""
        registry_instance = GeneratorRegistry()
        
        def test_func():
            yield 1
            yield 2
        
        generator = GeneratorBase(test_func)
        registry_instance.register("test_generator", generator)
        
        result = registry_instance.get("test_generator")
        assert result == generator
    
    def test_registry_get_not_found(self):
        """Test get generator not found"""
        registry_instance = GeneratorRegistry()
        
        with pytest.raises(GeneratorNotFoundError):
            registry_instance.get("nonexistent")
    
    def test_registry_list(self):
        """Test list generators"""
        registry_instance = GeneratorRegistry()
        
        def test_func1():
            yield 1
        
        def test_func2():
            yield 2
        
        generator1 = GeneratorBase(test_func1)
        generator2 = GeneratorBase(test_func2)
        
        registry_instance.register("gen1", generator1)
        registry_instance.register("gen2", generator2)
        
        result = registry_instance.list()
        assert "gen1" in result
        assert "gen2" in result
        assert len(result) == 2
    
    def test_registry_list_empty(self):
        """Test list generators when empty"""
        registry_instance = GeneratorRegistry()
        result = registry_instance.list()
        assert result == []
    
    def test_registry_unregister(self):
        """Test unregister generator"""
        registry_instance = GeneratorRegistry()
        
        def test_func():
            yield 1
        
        generator = GeneratorBase(test_func)
        registry_instance.register("test_generator", generator)
        registry_instance.unregister("test_generator")
        
        assert "test_generator" not in registry_instance._generators
    
    def test_registry_unregister_nonexistent(self):
        """Test unregister nonexistent generator"""
        registry_instance = GeneratorRegistry()
        registry_instance.unregister("nonexistent")
        assert "nonexistent" not in registry_instance._generators
    
    def test_registry_clear(self):
        """Test clear registry"""
        registry_instance = GeneratorRegistry()
        
        def test_func1():
            yield 1
        
        def test_func2():
            yield 2
        
        generator1 = GeneratorBase(test_func1)
        generator2 = GeneratorBase(test_func2)
        
        registry_instance.register("gen1", generator1)
        registry_instance.register("gen2", generator2)
        
        registry_instance.clear()
        
        assert registry_instance._generators == {}
    
    def test_registry_overwrite(self):
        """Test overwrite generator"""
        registry_instance = GeneratorRegistry()
        
        def test_func1():
            yield 1
        
        def test_func2():
            yield 2
        
        generator1 = GeneratorBase(test_func1)
        generator2 = GeneratorBase(test_func2)
        
        registry_instance.register("test_generator", generator1)
        registry_instance.register("test_generator", generator2)
        
        result = registry_instance.get("test_generator")
        assert result == generator2
    
    def test_global_registry_instance(self):
        """Test global registry instance"""
        assert isinstance(registry, GeneratorRegistry)
