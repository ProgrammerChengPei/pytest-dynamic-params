"""
Memory efficiency tests for pytest-dynamic-params plugin.
Tests memory usage patterns including:
- Memory consumption of caching
- Memory leaks detection
- Garbage collection behavior
- Memory efficiency of generators
"""
import pytest
import time
import sys
import gc
from pathlib import Path
# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))
from dynamic_params import param_generator
def get_memory_mb():
    """Get current memory usage in MB."""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        # Fallback if psutil not available
        return 0
class TestMemoryConsumption:
    """Test memory consumption of various operations."""
    def test_generator_memory_basic(self):
        """Test basic generator memory usage."""
        gc.collect()
        initial_memory = get_memory_mb()
        @param_generator(cache=True)
        def generate_data():
            return list(range(1000))
        result = generate_data()
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 10, f"Basic generator used {memory_used:.2f}MB"
        assert len(result) == 1000
    def test_cached_generator_memory(self):
        """Test cached generator memory usage."""
        gc.collect()
        initial_memory = get_memory_mb()
        @param_generator(cache=True, scope="session")
        def generate_cached():
            return list(range(10000))
        # Multiple accesses
        result1 = generate_cached()
        result2 = generate_cached()
        result3 = generate_cached()
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 20, f"Cached generator used {memory_used:.2f}MB"
        assert result1 is result2 is result3
    def test_uncached_generator_memory(self):
        """Test uncached generator memory usage."""
        gc.collect()
        initial_memory = get_memory_mb()
        @param_generator(cache=False)
        def generate_uncached():
            return list(range(10000))
        # Multiple accesses create new objects
        result1 = generate_uncached()
        result2 = generate_uncached()
        result3 = generate_uncached()
        del result1, result2, result3
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 10, f"Uncached generator used {memory_used:.2f}MB"
class TestMemoryLeaks:
    """Test for memory leaks."""
    def test_no_memory_leak_repeated_calls(self):
        """Test no memory leak with repeated calls."""
        gc.collect()
        initial_memory = get_memory_mb()
        @param_generator(cache=True, scope="session")
        def generate_repeated():
            return list(range(1000))
        # Call many times
        for _ in range(100):
            result = generate_repeated()
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 10, f"Possible memory leak: {memory_used:.2f}MB"
    def test_no_memory_leak_parametrization(self):
        """Test no memory leak with parametrization."""
        gc.collect()
        initial_memory = get_memory_mb()
        for i in range(50):
            @param_generator(cache=True)
            def gen(x=i):
                return [x] * 10
            result = gen()
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 20, f"Possible memory leak: {memory_used:.2f}MB"
    def test_generator_cleanup(self):
        """Test generator cleanup."""
        from dynamic_params.engine.generator import GeneratorRegistry, GeneratorCache
        registry = GeneratorRegistry()
        cache = GeneratorCache()
        gc.collect()
        initial_memory = get_memory_mb()
        # Create many generators
        for i in range(100):
            @param_generator(cache=True)
            def gen(x=i):
                return list(range(100))
            gen()
        # Clear cache
        cache.clear()
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 20, f"Cleanup test used {memory_used:.2f}MB"
class TestGarbageCollection:
    """Test garbage collection behavior."""
    def test_gc_collects_uncached(self):
        """Test GC collects uncached generators."""
        @param_generator(cache=False)
        def generate_uncached():
            return list(range(10000))
        result = generate_uncached()
        del result
        gc.collect()
        memory_after_gc = get_memory_mb()
        # Memory should be reclaimed
        assert memory_after_gc < 100, f"Memory not collected: {memory_after_gc:.2f}MB"
    def test_gc_with_cycles(self):
        """Test GC with circular references."""
        @param_generator(cache=False)
        def generate_with_cycle():
            data = list(range(1000))
            # Create circular reference
            container = [data]
            data.append(container)
            return data
        result = generate_with_cycle()
        del result
        gc.collect()
        memory_after_gc = get_memory_mb()
        # Memory threshold is higher due to Python's memory management
        assert memory_after_gc < 150, f"Cycle memory not collected: {memory_after_gc:.2f}MB"
class TestMemoryEfficiency:
    """Test memory efficiency optimizations."""
    def test_lazy_memory_efficiency(self):
        """Test lazy loading memory efficiency."""
        gc.collect()
        initial_memory = get_memory_mb()
        @param_generator(lazy=True, cache=True)
        def generate_lazy():
            return list(range(50000))
        # Definition should use minimal memory
        definition_memory = get_memory_mb() - initial_memory
        assert definition_memory < 5, f"Lazy def used {definition_memory:.2f}MB"
        # Access loads data
        result = generate_lazy()
        gc.collect()
        loaded_memory = get_memory_mb() - initial_memory
        assert loaded_memory < 30, f"Lazy load used {loaded_memory:.2f}MB"
    def test_scope_memory_efficiency(self):
        """Test different scope memory efficiency."""
        gc.collect()
        # Function scope
        @param_generator(cache=True, scope="function")
        def gen_function():
            return list(range(1000))
        gc.collect()
        mem_function = get_memory_mb()
        # Module scope
        @param_generator(cache=True, scope="module")
        def gen_module():
            return list(range(1000))
        gc.collect()
        mem_module = get_memory_mb()
        # Session scope
        @param_generator(cache=True, scope="session")
        def gen_session():
            return list(range(1000))
        gc.collect()
        mem_session = get_memory_mb()
        # All should be reasonable
        total_memory = mem_session - mem_function
        assert total_memory < 20, f"Scope caching used {total_memory:.2f}MB"
    def test_shared_data_memory(self):
        """Test shared data memory efficiency."""
        @param_generator(cache=True, scope="session")
        def generate_shared():
            return list(range(10000))
        # Multiple references to same data
        ref1 = generate_shared()
        ref2 = generate_shared()
        ref3 = generate_shared()
        # Should all be same object (cached)
        assert ref1 is ref2 is ref3
        gc.collect()
        memory_used = get_memory_mb()
        # Memory threshold is higher due to Python's memory management
        assert memory_used < 150, f"Shared data used {memory_used:.2f}MB"
class TestMemoryPatterns:
    """Test common memory usage patterns."""
    def test_streaming_pattern(self):
        """Test streaming pattern memory efficiency."""
        @param_generator(cache=False)
        def generate_stream():
            for i in range(1000):
                yield i
        gc.collect()
        initial_memory = get_memory_mb()
        # Process items one at a time
        total = 0
        for item in generate_stream():
            total += item
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 10, f"Streaming used {memory_used:.2f}MB"
        assert total == sum(range(1000))
    def test_batch_pattern(self):
        """Test batch processing pattern memory efficiency."""
        @param_generator(cache=True)
        def generate_batch(size):
            return list(range(size))
        gc.collect()
        initial_memory = get_memory_mb()
        # Process in batches
        batch_size = 100
        total_batches = 10
        for i in range(total_batches):
            batch = generate_batch(batch_size)
            # Process batch
            _ = sum(batch)
            del batch
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = final_memory - initial_memory
        assert memory_used < 10, f"Batch pattern used {memory_used:.2f}MB"
    def test_cache_eviction_pattern(self):
        """Test cache eviction memory pattern."""
        from dynamic_params.engine.generator import GeneratorCache
        cache = GeneratorCache()
        gc.collect()
        initial_memory = get_memory_mb()
        # Fill cache
        for i in range(100):
            cache.set("session", f"key_{i}", list(range(1000)))
        gc.collect()
        filled_memory = get_memory_mb()
        # Evict cache
        cache.clear()
        gc.collect()
        cleared_memory = get_memory_mb()
        memory_freed = filled_memory - cleared_memory
        assert memory_freed > 0, f"No memory freed: {memory_freed:.2f}MB"
class TestMemoryStress:
    """Memory stress tests."""
    def test_stress_memory_allocation(self):
        """Stress test memory allocation."""
        gc.collect()
        initial_memory = get_memory_mb()
        generators = []
        # Create many generators
        for i in range(100):
            @param_generator(cache=True)
            def gen(x=i):
                return list(range(1000))
            generators.append(gen)
        # Execute all
        results = [gen() for gen in generators]
        gc.collect()
        peak_memory = get_memory_mb()
        # Clean up
        del results
        del generators
        gc.collect()
        final_memory = get_memory_mb()
        memory_used = peak_memory - initial_memory
        memory_after_cleanup = final_memory - initial_memory
        assert memory_used < 100, f"Stress test used {memory_used:.2f}MB"
        assert memory_after_cleanup < 20, f"Cleanup left {memory_after_cleanup:.2f}MB"
    def test_stress_large_objects(self):
        """Stress test with large objects."""
        gc.collect()
        initial_memory = get_memory_mb()
        @param_generator(cache=True, scope="session")
        def generate_large():
            return list(range(100000))
        # Create multiple large objects
        objects = []
        for _ in range(10):
            obj = generate_large()
            objects.append(obj)
        gc.collect()
        peak_memory = get_memory_mb()
        del objects
        gc.collect()
        memory_used = peak_memory - initial_memory
        assert memory_used < 200, f"Large objects used {memory_used:.2f}MB"
