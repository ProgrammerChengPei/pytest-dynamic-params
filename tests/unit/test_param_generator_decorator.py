# Test param_generator decorator functionality

import pytest
from dynamic_params.public.decorators.param_generator import param_generator
from dynamic_params.engine.generator.registry import registry as generator_registry


class TestParamGeneratorBasic:
    """Test basic param_generator functionality"""
    
    def test_basic_generator_registration(self):
        """Test basic generator registration"""
        @param_generator
        def basic_generator():
            yield 1
            yield 2
            yield 3
        
        assert "basic_generator" in generator_registry.list()
        results = basic_generator()
        assert results == [1, 2, 3]
    
    def test_function_name_preservation(self):
        """Test that function name is preserved after decoration"""
        @param_generator
        def my_generator_function():
            """A generator function"""
            yield 5
        
        assert my_generator_function.__name__ == "my_generator_function"
        assert my_generator_function.__doc__ == "A generator function"
        assert "my_generator_function" in generator_registry.list()
    
    def test_generator_with_return_list(self):
        """Test generator that returns a list directly"""
        @param_generator
        def list_generator():
            return [10, 20, 30]
        
        results = list_generator()
        assert results == [10, 20, 30]
        assert "list_generator" in generator_registry.list()


class TestParamGeneratorWithOptions:
    """Test param_generator with various decorator options"""
    
    def test_with_scope_option(self):
        """Test generator with scope option"""
        @param_generator(scope="session")
        def session_generator():
            yield 100
            yield 200
        
        generator_info = generator_registry.get("session_generator")
        assert generator_info.scope == "session"
        assert generator_info.name == "session_generator"
    
    def test_with_cache_option(self):
        """Test generator with caching enabled"""
        call_count = 0
        
        @param_generator(cache=True)
        def cached_generator():
            nonlocal call_count
            call_count += 1
            yield call_count
        
        # First call should execute the function
        result1 = cached_generator()
        assert result1 == [1]
        
        # Second call should use cache
        result2 = cached_generator()
        assert result2 == [1]
        assert call_count == 1  # Function should only be called once
    
    def test_with_lazy_option(self):
        """Test generator with lazy loading"""
        evaluation_count = 0
        
        @param_generator(lazy=True)
        def lazy_generator():
            nonlocal evaluation_count
            evaluation_count += 1
            yield 50
            yield 60
        
        # Generator should not be evaluated until called
        assert evaluation_count == 0
        results = lazy_generator()
        assert evaluation_count == 1
        assert results == [50, 60]
    
    def test_with_autouse_option(self):
        """Test generator with autouse option"""
        @param_generator(autouse=True)
        def autouse_generator():
            yield 7
        
        generator_info = generator_registry.get("autouse_generator")
        assert generator_info.autouse is True


class TestParamGeneratorReturnTypes:
    """Test various return types from generators"""
    
    def test_single_value_return(self):
        """Test returning a single value"""
        @param_generator
        def single_value_generator():
            return 42
        
        results = single_value_generator()
        assert results == [42]
    
    def test_empty_generator(self):
        """Test generator with no values"""
        @param_generator
        def empty_generator():
            return []
        
        results = empty_generator()
        assert results == []
    
    def test_none_return_handling(self):
        """Test generator returning None"""
        @param_generator
        def none_generator():
            return None
        
        results = none_generator()
        assert results == []
    
    def test_tuple_return_conversion(self):
        """Test returning a tuple"""
        @param_generator
        def tuple_generator():
            return (1, 2, 3)
        
        results = tuple_generator()
        assert results == [1, 2, 3]


class TestParamGeneratorErrorHandling:
    """Test error scenarios for param_generator"""
    
    def test_generator_with_exception(self):
        """Test generator that raises an exception"""
        @param_generator
        def failing_generator():
            raise ValueError("Generator failure")
        
        with pytest.raises(ValueError, match="Generator failure"):
            failing_generator()
    
    def test_duplicate_generator_names(self):
        """Test registering generators with duplicate names"""
        @param_generator
        def duplicate_generator():
            yield 1
        
        # Should be able to register with same name (previous gets replaced)
        @param_generator
        def duplicate_generator():
            yield 2
        
        results = duplicate_generator()
        assert results == [2]
    
    def test_invalid_options_combination(self):
        """Test invalid option combinations"""
        with pytest.raises(ValueError):
            @param_generator(scope="invalid_scope")
            def invalid_scope_generator():
                yield 5


class TestParamGeneratorRegistryIntegration:
    """Test integration with generator registry"""
    
    def test_generator_unregistration(self):
        """Test generator cleanup on scope change"""
        @param_generator(scope="function")
        def temp_generator():
            yield 99
        
        assert "temp_generator" in generator_registry.list()
        # Simulate scope cleanup (would normally be handled by pytest)
        generator_registry.cleanup_scope("function")
        assert "temp_generator" not in generator_registry.list()
    
    def test_generator_metadata_preservation(self):
        """Test that generator metadata is preserved"""
        @param_generator(name="custom_name", scope="module")
        def custom_generator():
            """Custom generator"""
            yield 25
        
        generator_info = generator_registry.get("custom_name")
        assert generator_info.name == "custom_name"
        assert generator_info.scope == "module"
        assert generator_info.func.__name__ == "custom_generator"
        assert generator_info.func.__doc__ == "Custom generator"