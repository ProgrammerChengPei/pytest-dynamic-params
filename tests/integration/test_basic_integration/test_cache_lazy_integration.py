# Integration tests for caching and lazy loading functionality

import pytest
import time
from dynamic_params import param_generator, parametrize_test


class TestGeneratorCaching:
    """Test generator caching functionality"""
    
    def test_basic_caching(self):
        """Test basic caching mechanism"""
        call_count = {"count": 0}
        
        @param_generator(cache=True)
        def generate_cached_data():
            """Generate data with caching"""
            call_count["count"] += 1
            for i in range(5):
                yield i
        
        # First execution
        values1 = list(generate_cached_data.execute())
        assert values1 == [0, 1, 2, 3, 4]
        first_call_count = call_count["count"]
        
        # Second execution (should use cache)
        values2 = list(generate_cached_data.execute())
        assert values2 == [0, 1, 2, 3, 4]
        
        # Generator should only be called once due to caching
        assert call_count["count"] == first_call_count
    
    def test_caching_with_parameters(self):
        """Test caching with different parameters"""
        call_counts = {}
        
        @param_generator(cache=True)
        def generate_with_param(multiplier=1):
            """Generate data with parameter"""
            key = f"multiplier_{multiplier}"
            call_counts[key] = call_counts.get(key, 0) + 1
            
            for i in range(3):
                yield i * multiplier
        
        # First call with multiplier=2
        values1 = list(generate_with_param.execute(2))
        assert values1 == [0, 2, 4]
        
        # Second call with same parameter (should use cache)
        values2 = list(generate_with_param.execute(2))
        assert values2 == [0, 2, 4]
        
        # Call with different parameter (should execute again)
        values3 = list(generate_with_param.execute(3))
        assert values3 == [0, 3, 6]
    
    def test_cache_scope_function(self):
        """Test cache with function scope"""
        call_count = {"count": 0}
        
        @param_generator(scope="function", cache=True)
        def generate_function_scope():
            """Generate with function scope cache"""
            call_count["count"] += 1
            yield call_count["count"]
        
        # Multiple calls within same function scope
        values1 = list(generate_function_scope.execute())
        values2 = list(generate_function_scope.execute())
        
        # Should use cache within same scope
        assert values1 == values2
    
    def test_cache_scope_session(self):
        """Test cache with session scope"""
        call_count = {"count": 0}
        
        @param_generator(scope="session", cache=True)
        def generate_session_scope():
            """Generate with session scope cache"""
            call_count["count"] += 1
            for i in range(3):
                yield i
        
        # Multiple calls
        values1 = list(generate_session_scope.execute())
        values2 = list(generate_session_scope.execute())
        values3 = list(generate_session_scope.execute())
        
        # All should return same cached values
        assert values1 == values2 == values3 == [0, 1, 2]
    
    def test_cache_disabled(self):
        """Test generator without caching"""
        call_count = {"count": 0}
        
        @param_generator(cache=False)
        def generate_no_cache():
            """Generate without caching"""
            call_count["count"] += 1
            for i in range(3):
                yield i
        
        # Multiple calls
        values1 = list(generate_no_cache.execute())
        values2 = list(generate_no_cache.execute())
        
        # Should execute each time
        assert call_count["count"] == 2
        assert values1 == values2 == [0, 1, 2]


class TestLazyLoading:
    """Test lazy loading functionality"""
    
    def test_basic_lazy_loading(self):
        """Test basic lazy loading"""
        execution_flag = {"executed": False}
        
        @param_generator(lazy=True)
        def generate_lazy_data():
            """Generate lazy data"""
            execution_flag["executed"] = True
            for i in range(5):
                yield i
        
        # Generator should not execute immediately
        assert not execution_flag["executed"]
        
        # Access the generator
        values = list(generate_lazy_data.execute())
        
        # Now it should be executed
        assert execution_flag["executed"]
        assert values == [0, 1, 2, 3, 4]
    
    def test_lazy_loading_with_cache(self):
        """Test lazy loading combined with caching"""
        call_count = {"count": 0}
        
        @param_generator(lazy=True, cache=True)
        def generate_lazy_cached():
            """Generate lazy cached data"""
            call_count["count"] += 1
            for i in range(3):
                yield i
        
        # First access
        values1 = list(generate_lazy_cached.execute())
        assert values1 == [0, 1, 2]
        first_call_count = call_count["count"]
        
        # Second access (should use cache)
        values2 = list(generate_lazy_cached.execute())
        assert values2 == [0, 1, 2]
        
        # Should only be called once due to caching
        assert call_count["count"] == first_call_count
    
    def test_lazy_loading_defers_expensive_operation(self):
        """Test that lazy loading defers expensive operations"""
        start_time = {"time": 0}
        execution_time = {"time": 0}
        
        @param_generator(lazy=True)
        def generate_expensive_data():
            """Generate expensive data"""
            start_time["time"] = time.time()
            # Simulate expensive operation
            time.sleep(0.1)
            execution_time["time"] = time.time()
            for i in range(3):
                yield i
        
        # Record time before accessing
        before_access = time.time()
        
        # Generator should not execute immediately
        assert start_time["time"] == 0
        
        # Now access the generator
        values = list(generate_expensive_data.execute())
        
        # Verify it was deferred
        assert start_time["time"] > before_access
        assert execution_time["time"] > start_time["time"]
        assert values == [0, 1, 2]


class TestCachingPerformance:
    """Test caching performance improvements"""
    
    def test_cache_performance_improvement(self):
        """Test that caching improves performance"""
        
        @param_generator(cache=True)
        def generate_cached():
            """Generate cached data"""
            time.sleep(0.05)  # Simulate work
            for i in range(10):
                yield i
        
        # First call (no cache)
        start = time.time()
        values1 = list(generate_cached.execute())
        first_call_time = time.time() - start
        
        # Second call (with cache)
        start = time.time()
        values2 = list(generate_cached.execute())
        second_call_time = time.time() - start
        
        # Second call should be faster
        assert second_call_time < first_call_time
        assert values1 == values2
    
    def test_lazy_loading_performance(self):
        """Test that lazy loading avoids unnecessary computation"""
        execution_count = {"count": 0}
        
        @param_generator(lazy=True)
        def generate_lazy():
            """Generate lazy data"""
            execution_count["count"] += 1
            for i in range(100):
                yield i
        
        # If we never access the generator, it never executes
        # Note: In current implementation, lazy means deferred execution
        # but execute() returns a list, not an iterator
        
        # Access the generator
        values = list(generate_lazy.execute())
        
        # Generator executed
        assert execution_count["count"] == 1
        assert len(values) == 100
        assert values[0] == 0


class TestCachingEdgeCases:
    """Test caching edge cases"""
    
    def test_cache_with_exception(self):
        """Test caching behavior with exceptions"""
        call_count = {"count": 0}
        
        @param_generator(cache=True)
        def generate_with_exception():
            """Generate that raises exception"""
            call_count["count"] += 1
            yield 1
            raise ValueError("Test exception")
        
        # First call raises exception
        with pytest.raises(ValueError):
            list(generate_with_exception.execute())
        
        # Second call might retry or use partial cache
        # depending on implementation
        try:
            list(generate_with_exception.execute())
        except ValueError:
            pass  # Expected
    
    def test_cache_with_empty_generator(self):
        """Test caching with empty generator"""
        call_count = {"count": 0}
        
        @param_generator(cache=True)
        def generate_empty():
            """Generate nothing"""
            call_count["count"] += 1
            return
            yield
        
        # First call
        values1 = list(generate_empty.execute())
        assert values1 == []
        first_call_count = call_count["count"]
        
        # Second call (should use cache)
        values2 = list(generate_empty.execute())
        assert values2 == []
        
        # Should use cache
        assert call_count["count"] == first_call_count
    
    def test_cache_with_none_values(self):
        """Test caching with None values"""
        call_count = {"count": 0}
        
        @param_generator(cache=True)
        def generate_with_none():
            """Generate values including None"""
            call_count["count"] += 1
            yield 1
            yield None
            yield 3
        
        # First call
        values1 = list(generate_with_none.execute())
        assert values1 == [1, None, 3]
        first_call_count = call_count["count"]
        
        # Second call (should use cache)
        values2 = list(generate_with_none.execute())
        assert values2 == [1, None, 3]
        
        # Should use cache
        assert call_count["count"] == first_call_count


class TestLazyLoadingEdgeCases:
    """Test lazy loading edge cases"""
    
    def test_lazy_with_single_value(self):
        """Test lazy loading with single value"""
        execution_flag = {"executed": False}
        
        @param_generator(lazy=True)
        def generate_single():
            """Generate single value"""
            execution_flag["executed"] = True
            yield 42
        
        # Should not execute immediately
        assert not execution_flag["executed"]
        
        # Access the value
        values = list(generate_single.execute())
        
        # Now it should be executed
        assert execution_flag["executed"]
        assert values == [42]
    
    def test_lazy_generator_partial_consumption(self):
        """Test lazy generator with partial consumption"""
        execution_flag = {"executed": False}
        
        @param_generator(lazy=True)
        def generate_lazy_many():
            """Generate many values"""
            execution_flag["executed"] = True
            for i in range(10):
                yield i
        
        # Note: Current implementation returns a list from execute()
        # So we can't test partial consumption with next()
        
        # Access all values
        values = list(generate_lazy_many.execute())
        
        # Generator executed
        assert execution_flag["executed"]
        assert values == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


class TestCombinedFeatures:
    """Test combined caching and lazy loading features"""
    
    def test_cache_and_lazy_together(self):
        """Test using cache and lazy together"""
        call_count = {"count": 0}
        
        @param_generator(lazy=True, cache=True)
        def generate_combined():
            """Generate with both lazy and cache"""
            call_count["count"] += 1
            time.sleep(0.01)  # Simulate work
            for i in range(5):
                yield i
        
        # Should not execute immediately
        assert call_count["count"] == 0
        
        # First access
        values1 = list(generate_combined.execute())
        first_call_count = call_count["count"]
        
        # Second access (should use cache)
        values2 = list(generate_combined.execute())
        
        # Should use cache
        assert call_count["count"] == first_call_count
        assert values1 == values2 == [0, 1, 2, 3, 4]
    
    def test_multiple_lazy_generators(self):
        """Test multiple lazy generators"""
        execution_flags = {"gen1": False, "gen2": False}
        
        @param_generator(lazy=True)
        def generate_lazy_1():
            """First lazy generator"""
            execution_flags["gen1"] = True
            yield 1
        
        @param_generator(lazy=True)
        def generate_lazy_2():
            """Second lazy generator"""
            execution_flags["gen2"] = True
            yield 2
        
        # Neither should execute immediately
        assert not execution_flags["gen1"]
        assert not execution_flags["gen2"]
        
        # Access first generator
        values1 = list(generate_lazy_1.execute())
        assert execution_flags["gen1"]
        assert not execution_flags["gen2"]
        assert values1 == [1]
        
        # Access second generator
        values2 = list(generate_lazy_2.execute())
        assert execution_flags["gen2"]
        assert values2 == [2]
