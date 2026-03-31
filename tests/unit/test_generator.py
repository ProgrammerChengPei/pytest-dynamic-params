# Test generator functionality

import pytest
from dynamic_params.engine.generator.base import GeneratorBase
from dynamic_params.engine.generator.lazy import LazyGenerator
from dynamic_params.engine.generator.registry import registry as generator_registry

class TestGenerator:
    """Test generator functionality"""
    
    def test_generator_base(self):
        """Test GeneratorBase class"""
        # Define a simple generator function
        def simple_generator():
            yield 1
            yield 2
            yield 3
        
        # Create generator instance
        generator = GeneratorBase(simple_generator)
        
        # Execute generator
        result = generator.execute()
        
        # Check result
        assert result == [1, 2, 3]
    
    def test_generator_cache(self):
        """Test generator caching"""
        # Define a generator function with side effect
        call_count = 0
        def cached_generator():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        # Create generator instance with cache enabled
        generator = GeneratorBase(cached_generator, cache=True)
        
        # First execution
        result1 = generator.execute()
        
        # Second execution (should use cache)
        result2 = generator.execute()
        
        # Check results
        assert result1 == [1]
        assert result2 == [1]  # Should be same as first result
    
    def test_lazy_generator(self):
        """Test LazyGenerator class"""
        # Define a simple generator function
        def simple_generator():
            yield 4
            yield 5
            yield 6
        
        # Create lazy generator instance
        generator = LazyGenerator(simple_generator)
        
        # Execute generator
        result1 = generator.execute()
        
        # Execute again (should return cached result)
        result2 = generator.execute()
        
        # Check results
        assert result1 == [4, 5, 6]
        assert result2 == [4, 5, 6]
    
    def test_generator_registry(self):
        """Test generator registry"""
        # Define a simple generator function
        def registered_generator():
            yield 7
            yield 8
            yield 9
        
        # Create generator instance
        generator = GeneratorBase(registered_generator)
        
        # Register generator
        generator_registry.register("test_generator", generator)
        
        # Get generator from registry
        retrieved_generator = generator_registry.get("test_generator")
        
        # Execute retrieved generator
        result = retrieved_generator.execute()
        
        # Check result
        assert result == [7, 8, 9]
        
        # Unregister generator
        generator_registry.unregister("test_generator")
        
        # Check that generator is no longer in registry
        with pytest.raises(Exception):
            generator_registry.get("test_generator")
