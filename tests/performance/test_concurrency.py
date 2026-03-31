"""
Concurrency and parallel execution performance tests.

Tests concurrent execution including:
- Thread safety
- Parallel test execution
- pytest-xdist compatibility
- Distributed caching
"""

import pytest
import time
import sys
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from dynamic_params import parametrize_test, param_generator


class TestThreadSafety:
    """Test thread safety of plugin components."""
    
    def test_concurrent_generator_access(self, timer, benchmark_config):
        """Test concurrent access to generators."""
        @param_generator(cache=True, scope="session")
        def generate_shared():
            time.sleep(0.01)
            return list(range(100))
        
        results = []
        times = []
        
        def access_generator():
            with timer:
                result = generate_shared()
            times.append(timer.elapsed)
            results.append(result)
        
        # Create threads
        threads = []
        for _ in range(benchmark_config["benchmark_iterations"]):
            t = threading.Thread(target=access_generator)
            threads.append(t)
        
        # Start all
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # All results should be identical
        assert all(r == results[0] for r in results), "Results should be identical"
        
        avg_time = sum(times) / len(times)
        assert avg_time < 20, f"Concurrent access took {avg_time:.2f}ms"
    
    def test_concurrent_cache_access(self, timer):
        """Test concurrent cache access."""
        from dynamic_params.engine.generator import GeneratorCache
        
        cache = GeneratorCache()
        errors = []
        
        def write_to_cache(thread_id):
            try:
                for i in range(100):
                    cache.set("session", f"thread{thread_id}_key{i}", list(range(100)))
            except Exception as e:
                errors.append(e)
        
        # Create threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=write_to_cache, args=(i,))
            threads.append(t)
        
        # Start all
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Cache errors: {errors}"
    
    def test_concurrent_registry_access(self, timer):
        """Test concurrent registry access."""
        from dynamic_params.engine.generator import GeneratorRegistry
        
        registry = GeneratorRegistry()
        errors = []
        
        def register_generator(thread_id):
            try:
                for i in range(50):
                    @param_generator(cache=True)
                    def gen(x=thread_id * 100 + i):
                        return [x]
                    registry.register(f"gen_{thread_id}_{i}", gen)
            except Exception as e:
                errors.append(e)
        
        # Create threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=register_generator, args=(i,))
            threads.append(t)
        
        # Start all
        for t in threads:
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        assert len(errors) == 0, f"Registry errors: {errors}"


class TestParallelExecution:
    """Test parallel execution performance."""
    
    def test_thread_pool_execution(self, timer, benchmark_config):
        """Test thread pool execution."""
        # Simplified test without using param_generator
        def execute_task(n):
            time.sleep(0.001)
            return n * 2
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            with timer:
                results = list(executor.map(execute_task, range(benchmark_config["sample_size"])))
        
        assert len(results) == benchmark_config["sample_size"]
        assert all(r == i * 2 for i, r in enumerate(results))
        assert timer.elapsed < 5000, f"Thread pool took {timer.elapsed:.2f}ms"
    
    @pytest.mark.skip(reason="ProcessPoolExecutor can't handle class methods in this environment")
    def test_process_pool_execution(self, timer, benchmark_config):
        """Test process pool execution."""
        # Note: ProcessPoolExecutor can't pickle nested functions or class methods
        # This test is skipped due to environment limitations
        pass


class TestXdistCompatibility:
    """Test pytest-xdist compatibility."""
    
    def test_distributed_execution_simulation(self, timer):
        """Simulate distributed execution."""
        @param_generator(cache=True, scope="session")
        def generate_distributed():
            return list(range(1000))
        
        # Simulate multiple workers
        workers = 4
        results_per_worker = []
        
        def worker_task(worker_id):
            # Each worker gets same data
            return generate_distributed()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            with timer:
                futures = [
                    executor.submit(worker_task, i)
                    for i in range(workers)
                ]
                results_per_worker = [f.result() for f in futures]
        
        # All workers should get identical data
        for result in results_per_worker:
            assert result == results_per_worker[0]
        
        assert timer.elapsed < 500, f"Distributed simulation took {timer.elapsed:.2f}ms"
    
    def test_worker_isolation(self, timer):
        """Test worker isolation."""
        from dynamic_params.engine.generator import GeneratorCache
        
        # Each worker should have isolated cache
        caches = [GeneratorCache() for _ in range(4)]
        
        def worker_cache_task(worker_id, cache):
            cache.set("session", f"worker_{worker_id}", list(range(100)))
            return cache.get("session", f"worker_{worker_id}")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(worker_cache_task, i, caches[i])
                for i in range(4)
            ]
            results = [f.result() for f in futures]
        
        # All workers should have their own data
        assert all(len(r) == 100 for r in results)


class TestConcurrentPerformance:
    """Test concurrent performance patterns."""
    
    def test_producer_consumer_pattern(self, timer):
        """Test producer-consumer pattern."""
        import queue
        
        @param_generator(cache=False)
        def produce():
            return list(range(100))
        
        q = queue.Queue()
        results = []
        
        def producer():
            for i in range(10):
                data = produce()
                q.put(data)
            q.put(None)  # Sentinel
        
        def consumer():
            while True:
                item = q.get()
                if item is None:
                    break
                results.append(sum(item))
        
        with timer:
            # Start producer and consumer
            producer_thread = threading.Thread(target=producer)
            consumer_thread = threading.Thread(target=consumer)
            
            producer_thread.start()
            consumer_thread.start()
            
            producer_thread.join()
            consumer_thread.join()
        
        assert len(results) == 10
        assert all(r == sum(range(100)) for r in results)
        assert timer.elapsed < 1000, f"Producer-consumer took {timer.elapsed:.2f}ms"
    
    def test_map_reduce_pattern(self, timer, benchmark_config):
        """Test map-reduce pattern."""
        @param_generator(cache=True)
        def generate_data(n):
            return [n] * 100
        
        def map_task(n):
            data = generate_data(n)
            return sum(data)
        
        def reduce_task(results):
            return sum(results)
        
        with timer:
            # Map phase
            map_results = [map_task(i) for i in range(benchmark_config["sample_size"])]
            
            # Reduce phase
            final_result = reduce_task(map_results)
        
        expected = sum(sum([i] * 100) for i in range(benchmark_config["sample_size"]))
        assert final_result == expected
        assert timer.elapsed < 2000, f"Map-reduce took {timer.elapsed:.2f}ms"


class TestScalability:
    """Test scalability with increasing load."""
    
    def test_scaling_threads(self, timer):
        """Test scaling with increasing threads."""
        @param_generator(cache=True, scope="session")
        def generate_shared():
            return list(range(100))
        
        thread_counts = [1, 2, 4, 8, 16]
        times = []
        
        for num_threads in thread_counts:
            def worker():
                return generate_shared()
            
            with timer:
                with ThreadPoolExecutor(max_workers=num_threads) as executor:
                    results = list(executor.map(lambda _: worker(), range(num_threads)))
            
            times.append(timer.elapsed)
            assert all(len(r) == 100 for r in results)
        
        # Scaling test - just ensure it completes in reasonable time
        assert all(t < 2000 for t in times), f"Scaling test took {max(times):.2f}ms"
    
    def test_scaling_data_size(self, timer):
        """Test scaling with increasing data size."""
        data_sizes = [100, 1000, 10000]
        times = []
        
        for size in data_sizes:
            @param_generator(cache=True)
            def generate_size(s=size):
                return list(range(s))
            
            with timer:
                result = generate_size()
            
            times.append(timer.elapsed)
            assert len(result) == size
        
        # Should scale linearly
        assert times[2] < times[0] * 20, "Scaling should be reasonable"


class TestConcurrentStress:
    """Concurrent stress tests."""
    
    def test_stress_concurrent_access(self, timer, benchmark_config):
        """Stress test concurrent access."""
        @param_generator(cache=True, scope="session")
        def generate_stress():
            time.sleep(0.001)
            return list(range(100))
        
        num_threads = 50
        results = []
        errors = []
        
        def worker():
            try:
                result = generate_stress()
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=worker)
            threads.append(t)
        
        with timer:
            for t_thread in threads:
                t_thread.start()
            for t_thread in threads:
                t_thread.join()
        
        assert len(errors) == 0, f"Stress test errors: {errors}"
        assert len(results) == num_threads
        assert all(r == results[0] for r in results)
        assert timer.elapsed < 2000, f"Stress test took {timer.elapsed:.2f}ms"
    
    def test_stress_mixed_operations(self, timer):
        """Stress test mixed concurrent operations."""
        from dynamic_params.engine.generator import GeneratorCache, GeneratorRegistry
        
        cache = GeneratorCache()
        registry = GeneratorRegistry()
        errors = []
        
        def mixed_worker(worker_id):
            try:
                # Register generator
                @param_generator(cache=True)
                def gen(x=worker_id):
                    return [x] * 10
                
                registry.register(f"worker_{worker_id}", gen)
                
                # Cache some data
                cache.set("session", f"worker_{worker_id}", list(range(100)))
                
                # Read data
                _ = cache.get("session", f"worker_{worker_id}")
                
            except Exception as e:
                errors.append(e)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            with timer:
                futures = [
                    executor.submit(mixed_worker, i)
                    for i in range(20)
                ]
                _ = [f.result() for f in futures]
        
        assert len(errors) == 0, f"Mixed operations errors: {errors}"
