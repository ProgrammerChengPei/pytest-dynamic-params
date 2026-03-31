# Test registry module comprehensively

import pytest
from dynamic_params.engine.generator.registry import GeneratorRegistry
from dynamic_params.engine.generator.base import GeneratorBase


class TestGeneratorRegistryExtended:
    """Extended tests for GeneratorRegistry"""
    
    def test_registry_list_empty(self):
        """Test list() on empty registry"""
        registry = GeneratorRegistry()
        assert registry.list() == []
    
    def test_registry_unregister_not_exists(self):
        """Test unregistering a non-existent generator should not raise"""
        registry = GeneratorRegistry()
        try:
            registry.unregister("nonexistent")
        except Exception as e:
            pytest.fail(f"unregister should not raise, but got: {e}")
    
    def test_registry_unregister_then_get(self):
        """Test unregister then get"""
        registry = GeneratorRegistry()
        
        def test_generator():
            yield 1
        
        gen = GeneratorBase(test_generator)
        registry.register("test_gen", gen)
        assert registry.get("test_gen") is not None
        
        registry.unregister("test_gen")
        with pytest.raises(Exception):
            registry.get("test_gen")
    
    def test_registry_has_equivalent(self):
        """Test checking if generator exists"""
        registry = GeneratorRegistry()
        
        def test_generator():
            yield 1
        
        gen = GeneratorBase(test_generator)
        assert "test_gen" not in registry.list()
        registry.register("test_gen", gen)
        assert "test_gen" in registry.list()
        registry.unregister("test_gen")
        assert "test_gen" not in registry.list()
    
    def test_registry_clear(self):
        """Test clear() method"""
        registry = GeneratorRegistry()
        
        def gen1():
            yield 1
        
        def gen2():
            yield 2
        
        registry.register("gen1", GeneratorBase(gen1))
        registry.register("gen2", GeneratorBase(gen2))
        assert len(registry.list()) == 2
        
        registry.clear()
        assert len(registry.list()) == 0
        assert "gen1" not in registry.list()
        assert "gen2" not in registry.list()
    
    def test_registry_register_multiple(self):
        """Test registering multiple generators"""
        registry = GeneratorRegistry()
        
        def gen1():
            yield 1
        
        def gen2():
            yield 2
        
        def gen3():
            yield 3
        
        registry.register("gen1", GeneratorBase(gen1))
        registry.register("gen2", GeneratorBase(gen2))
        registry.register("gen3", GeneratorBase(gen3))
        
        assert set(registry.list()) == {"gen1", "gen2", "gen3"}
    
    def test_registry_overwrite_existing(self):
        """Test registering with existing name overwrites"""
        registry = GeneratorRegistry()
        
        def gen_v1():
            yield 1
        
        def gen_v2():
            yield 2
        
        registry.register("test_gen", GeneratorBase(gen_v1))
        result1 = registry.get("test_gen")()
        assert result1 == [1]
        
        registry.register("test_gen", GeneratorBase(gen_v2))
        result2 = registry.get("test_gen")()
        assert result2 == [2]
