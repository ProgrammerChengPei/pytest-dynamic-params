"""
Performance tests for large-scale parametrization.

Tests performance with large numbers of parameters including:
- Large parameter sets
- Many test cases
- Combinatorial explosion
- Parameter combination generation
"""

import pytest
import time
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from dynamic_params import parametrize_test, param_generator


class TestLargeParameterSets:
    """Test performance with large parameter sets."""
    
    def test_hundred_parameters(self, timer):
        """Test with 100 parameters."""
        param_values = [[i] for i in range(100)]
        
        @parametrize_test("x", param_values)
        def test_func(x):
            return x * 2
        
        execution_times = []
        for i in range(100):
            with timer:
                result = test_func(i)
            execution_times.append(timer.elapsed)
            assert result == i * 2
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"100 params avg took {avg_time:.2f}ms"
    
    def test_thousand_parameters(self, timer, benchmark_config):
        """Test with 1000 parameters."""
        num_params = 1000
        param_values = [[i] for i in range(num_params)]
        
        @parametrize_test("x", param_values)
        def test_func(x):
            return x + 1
        
        # Test subset for performance
        test_count = min(100, num_params)
        execution_times = []
        
        for i in range(test_count):
            with timer:
                result = test_func(i)
            execution_times.append(timer.elapsed)
            assert result == i + 1
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"1000 params avg took {avg_time:.2f}ms"
    
    def test_large_parameter_values(self, timer):
        """Test with large parameter values."""
        # Each parameter is a large list
        param_values = [[list(range(1000))] for _ in range(100)]
        
        @parametrize_test("data", param_values)
        def test_func(data):
            return len(data)
        
        execution_times = []
        for i in range(100):
            with timer:
                result = test_func(list(range(1000)))
            execution_times.append(timer.elapsed)
            assert result == 1000
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 10, f"Large values avg took {avg_time:.2f}ms"


class TestCombinatorialParametrization:
    """Test combinatorial parametrization performance."""
    
    def test_cartesian_product_small(self, timer):
        """Test small Cartesian product."""
        @parametrize_test("x", [[i] for i in range(10)])
        @parametrize_test("y", [[i] for i in range(10)])
        def test_func(x, y):
            return x + y
        
        execution_times = []
        for i in range(10):
            for j in range(10):
                with timer:
                    result = test_func(i, j)
                execution_times.append(timer.elapsed)
                assert result == i + j
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Small Cartesian product took {avg_time:.2f}ms"
    
    def test_cartesian_product_medium(self, timer):
        """Test medium Cartesian product."""
        @parametrize_test("x", [[i] for i in range(20)])
        @parametrize_test("y", [[i] for i in range(20)])
        @parametrize_test("z", [[i] for i in range(5)])
        def test_func(x, y, z):
            return x + y + z
        
        # Test subset
        test_count = 0
        execution_times = []
        
        for i in range(20):
            for j in range(20):
                for k in range(5):
                    with timer:
                        result = test_func(i, j, k)
                    execution_times.append(timer.elapsed)
                    assert result == i + j + k
                    test_count += 1
                    
                    if test_count >= 200:  # Limit test count
                        break
                if test_count >= 200:
                    break
            if test_count >= 200:
                break
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Medium Cartesian product took {avg_time:.2f}ms"
    
    def test_many_parameters_combination(self, timer):
        """Test many parameter combinations."""
        @parametrize_test("a", [[1], [2]])
        @parametrize_test("b", [[1], [2]])
        @parametrize_test("c", [[1], [2]])
        @parametrize_test("d", [[1], [2]])
        @parametrize_test("e", [[1], [2]])
        def test_func(a, b, c, d, e):
            return a + b + c + d + e
        
        execution_times = []
        for a in [1, 2]:
            for b in [1, 2]:
                for c in [1, 2]:
                    for d in [1, 2]:
                        for e in [1, 2]:
                            with timer:
                                result = test_func(a, b, c, d, e)
                            execution_times.append(timer.elapsed)
                            assert result == a + b + c + d + e
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Many params took {avg_time:.2f}ms"


class TestGeneratorScalePerformance:
    """Test generator performance at scale."""
    
    def test_generator_many_params(self, timer):
        """Test generator with many parameters."""
        @param_generator(cache=True)
        def generate_many():
            return list(range(500))
        
        with timer:
            result = generate_many()
        
        assert len(result) == 500
        assert timer.elapsed < 100, f"Generator with many params took {timer.elapsed:.2f}ms"
    
    def test_generator_large_output(self, timer):
        """Test generator producing large output."""
        @param_generator(cache=True, scope="session")
        def generate_large_output():
            return list(range(10000))
        
        with timer:
            result = generate_large_output()
        
        assert len(result) == 10000
        assert timer.elapsed < 200, f"Large output generator took {timer.elapsed:.2f}ms"
    
    def test_multiple_generators(self, timer, benchmark_config):
        """Test multiple generators."""
        generators = []
        
        for i in range(10):
            @param_generator(cache=True)
            def gen(x=i):
                time.sleep(0.001)
                return [x] * 10
            generators.append(gen)
        
        execution_times = []
        for gen in generators:
            with timer:
                result = gen()
            execution_times.append(timer.elapsed)
            assert len(result) == 10
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 50, f"Multiple generators took {avg_time:.2f}ms"


class TestParametrizationMemory:
    """Test memory usage with large parametrization."""
    
    def test_memory_large_parametrization(self, memory_tracker):
        """Test memory with large parametrization."""
        param_values = [[list(range(1000))] for _ in range(1000)]
        
        with memory_tracker:
            @parametrize_test("data", param_values)
            def test_func(data):
                return len(data)
        
        memory_delta = memory_tracker.get_delta()
        assert memory_delta < 100, f"Large parametrization used {memory_delta:.2f}MB"
    
    def test_memory_generator_caching(self, memory_tracker, benchmark_config):
        """Test memory usage of generator caching."""
        @param_generator(cache=True, scope="session")
        def generate_cached_large():
            return list(range(benchmark_config["sample_size"]))
        
        with memory_tracker:
            result = generate_cached_large()
        
        assert len(result) == benchmark_config["sample_size"]
        memory_delta = memory_tracker.get_delta()
        assert memory_delta < 50, f"Cached generator used {memory_delta:.2f}MB"


class TestStressParametrization:
    """Stress tests for parametrization."""
    
    def test_stress_many_test_cases(self, timer, benchmark_config):
        """Stress test with many test cases."""
        num_tests = benchmark_config["sample_size"]
        param_values = [[i] for i in range(num_tests)]
        
        @parametrize_test("x", param_values)
        def test_func(x):
            return x * 2
        
        # Run all tests
        execution_times = []
        for i in range(num_tests):
            with timer:
                result = test_func(i)
            execution_times.append(timer.elapsed)
            assert result == i * 2
        
        avg_time = sum(execution_times) / len(execution_times)
        total_time = sum(execution_times)
        
        assert avg_time < 5, f"Stress test avg took {avg_time:.2f}ms"
        assert total_time < 10000, f"Total stress test took {total_time:.2f}ms"
    
    def test_stress_nested_generators(self, timer):
        """Stress test with nested generators."""
        @param_generator(cache=True)
        def generate_base():
            return list(range(100))
        
        @param_generator(cache=True)
        def generate_nested():
            base = generate_base()
            return [x * 2 for x in base]
        
        @param_generator(cache=True)
        def generate_deep_nested():
            nested = generate_nested()
            return [x + 1 for x in nested]
        
        with timer:
            result = generate_deep_nested()
        
        assert len(result) == 100
        assert result[0] == 1
        assert timer.elapsed < 100, f"Nested generators took {timer.elapsed:.2f}ms"
    
    def test_stress_parameter_combinations(self, timer, benchmark_config):
        """Stress test parameter combinations."""
        @param_generator(cache=True)
        def generate_params(n):
            return list(range(n))
        
        @parametrize_test("x", generate_params(50))
        @parametrize_test("y", generate_params(50))
        def test_func(x, y):
            return x + y
        
        execution_times = []
        test_count = 0
        
        for i in range(50):
            for j in range(50):
                with timer:
                    result = test_func(i, j)
                execution_times.append(timer.elapsed)
                assert result == i + j
                test_count += 1
                
                if test_count >= 500:  # Limit
                    break
            if test_count >= 500:
                break
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Parameter combinations took {avg_time:.2f}ms"


class TestEdgeCases:
    """Test edge cases in large-scale parametrization."""
    
    def test_empty_parameter_list(self, timer):
        """Test with empty parameter list."""
        @parametrize_test("x", [])
        def test_func(x):
            return x
        
        # Should not execute
        assert timer.elapsed < 1
    
    def test_single_large_parameter(self, timer):
        """Test with single very large parameter."""
        large_data = list(range(100000))
        
        @parametrize_test("data", [[large_data]])
        def test_func(data):
            return len(data)
        
        with timer:
            result = test_func(large_data)
        
        assert result == 100000
        assert timer.elapsed < 50, f"Single large param took {timer.elapsed:.2f}ms"
    
    def test_duplicate_parameters(self, timer):
        """Test with duplicate parameters."""
        param_values = [[i % 10] for i in range(1000)]
        
        @parametrize_test("x", param_values)
        def test_func(x):
            return x
        
        execution_times = []
        for i in range(1000):
            with timer:
                result = test_func(i % 10)
            execution_times.append(timer.elapsed)
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Duplicate params took {avg_time:.2f}ms"
