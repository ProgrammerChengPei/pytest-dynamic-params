"""
Benchmark tests for core operations.

Tests the performance of basic operations including:
- Generator creation
- Parameter resolution
- Test parametrization
- Decorator application
"""

import pytest
import time
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from dynamic_params import parametrize_test, param_generator


class TestGeneratorBenchmarks:
    """Benchmark tests for generator operations."""
    
    def test_generator_creation_time(self, timer, benchmark_config):
        """Benchmark generator creation time."""
        creation_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                @param_generator(cache=False)
                def temp_generator():
                    return [1, 2, 3]
            
            creation_times.append(timer.elapsed)
        
        avg_time = sum(creation_times) / len(creation_times)
        assert avg_time < 10, f"Generator creation took {avg_time:.2f}ms (expected < 10ms)"
    
    def test_simple_generator_execution(self, timer, benchmark_config):
        """Benchmark simple generator execution."""
        @param_generator(cache=False)
        def generate_simple():
            return list(range(100))
        
        execution_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                result = generate_simple()
            
            execution_times.append(timer.elapsed)
            assert len(result) == 100
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 50, f"Simple generator execution took {avg_time:.2f}ms (expected < 50ms)"
    
    def test_generator_with_parameters(self, timer, benchmark_config):
        """Benchmark generator with parameters."""
        @param_generator(cache=False)
        def generate_with_params(start, end):
            return list(range(start, end))
        
        execution_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                result = generate_with_params(0, 100)
            
            execution_times.append(timer.elapsed)
            assert len(result) == 100
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 50, f"Parameterized generator took {avg_time:.2f}ms (expected < 50ms)"


class TestParametrizationBenchmarks:
    """Benchmark tests for parametrization operations."""
    
    def test_parametrization_overhead(self, timer, benchmark_config):
        """Benchmark parametrization overhead."""
        @parametrize_test("x", [[i] for i in range(10)])
        def test_func(x):
            return x * 2
        
        execution_times = []
        
        for i in range(10):
            with timer:
                result = test_func(i)
            
            execution_times.append(timer.elapsed)
            assert result == i * 2
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Parametrization overhead took {avg_time:.2f}ms (expected < 5ms)"
    
    def test_large_parametrization(self, timer, benchmark_config):
        """Benchmark large parametrization."""
        num_params = 1000
        param_values = [[i] for i in range(num_params)]
        
        @parametrize_test("x", param_values)
        def test_func(x):
            return x + 1
        
        execution_times = []
        
        for i in range(min(100, num_params)):
            with timer:
                result = test_func(i)
            
            execution_times.append(timer.elapsed)
            assert result == i + 1
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 10, f"Large parametrization took {avg_time:.2f}ms (expected < 10ms)"
    
    def test_multiple_parametrization_decorators(self, timer, benchmark_config):
        """Benchmark multiple parametrization decorators."""
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
        assert avg_time < 5, f"Multiple decorators took {avg_time:.2f}ms (expected < 5ms)"


class TestDynRefBenchmarks:
    """Benchmark tests for DynRef operations."""
    
    def test_dynref_creation(self, timer, benchmark_config):
        """Benchmark DynRef creation."""
        from dynamic_params import DynRef
        
        creation_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                ref = DynRef("param_name")
            
            creation_times.append(timer.elapsed)
            assert ref.name == "param_name"
        
        avg_time = sum(creation_times) / len(creation_times)
        assert avg_time < 1, f"DynRef creation took {avg_time:.2f}ms (expected < 1ms)"
    
    def test_dynref_expression_building(self, timer, benchmark_config):
        """Benchmark DynRef expression building."""
        from dynamic_params import DynRef
        
        expression_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                ref1 = DynRef("a")
                ref2 = DynRef("b")
                expr = ref1 + ref2 * 2 - DynRef("c") / DynRef("d")
            
            expression_times.append(timer.elapsed)
        
        avg_time = sum(expression_times) / len(expression_times)
        assert avg_time < 2, f"DynRef expression building took {avg_time:.2f}ms (expected < 2ms)"


class TestDecoratorBenchmarks:
    """Benchmark tests for decorator operations."""
    
    def test_param_generator_decorator(self, timer, benchmark_config):
        """Benchmark @param_generator decorator application."""
        decorator_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                @param_generator(cache=False, lazy=False)
                def temp_gen():
                    return [1, 2, 3]
            
            decorator_times.append(timer.elapsed)
        
        avg_time = sum(decorator_times) / len(decorator_times)
        assert avg_time < 10, f"@param_generator decorator took {avg_time:.2f}ms (expected < 10ms)"
    
    def test_parametrize_test_decorator(self, timer, benchmark_config):
        """Benchmark @parametrize_test decorator application."""
        decorator_times = []
        
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                @parametrize_test("x", [[1], [2], [3]])
                def temp_test(x):
                    return x
            
            decorator_times.append(timer.elapsed)
        
        avg_time = sum(decorator_times) / len(decorator_times)
        assert avg_time < 10, f"@parametrize_test decorator took {avg_time:.2f}ms (expected < 10ms)"


class TestOverallPerformance:
    """Overall performance benchmarks."""
    
    def test_end_to_end_parametrization(self, timer, benchmark_config):
        """Benchmark end-to-end parametrization workflow."""
        @param_generator(cache=True)
        def generate_data():
            return list(range(50))
        
        @parametrize_test("value", generate_data)
        def test_process(value):
            return value * 2
        
        execution_times = []
        
        for value in range(50):
            with timer:
                result = test_process(value)
            
            execution_times.append(timer.elapsed)
            assert result == value * 2
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"End-to-end took {avg_time:.2f}ms (expected < 5ms)"
    
    def test_mixed_parametrization(self, timer, benchmark_config):
        """Benchmark mixed parametrization (static + dynamic)."""
        @param_generator(cache=False)
        def generate_dynamic():
            return [10, 20, 30]
        
        @parametrize_test("static", [[1], [2], [3]])
        @parametrize_test("dynamic", generate_dynamic)
        def test_mixed(static, dynamic):
            return static + dynamic
        
        execution_times = []
        
        for s in [1, 2, 3]:
            for d in [10, 20, 30]:
                with timer:
                    result = test_mixed(s, d)
                
                execution_times.append(timer.elapsed)
                assert result == s + d
        
        avg_time = sum(execution_times) / len(execution_times)
        assert avg_time < 5, f"Mixed parametrization took {avg_time:.2f}ms (expected < 5ms)"
