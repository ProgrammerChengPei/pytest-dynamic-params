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
from dynamic_params import param_generator
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
        @pytest.mark.parametrize("x", [[i] for i in range(10)])
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
        @pytest.mark.parametrize("x", param_values)
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
        @pytest.mark.parametrize("x", [[i] for i in range(10)])
        @pytest.mark.parametrize("y", [[i] for i in range(10)])
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
class TestBenchmarks:
    """Benchmark tests for operations."""
    def test_dynref_creation(self, timer, benchmark_config):
        """Benchmark creation."""
        from dynamic_params import param_generator
        creation_times = []
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                ref =("param_name")
            creation_times.append(timer.elapsed)
            assert ref.name == "param_name"
        avg_time = sum(creation_times) / len(creation_times)
        assert avg_time < 1, f" creation took {avg_time:.2f}ms (expected < 1ms)"
    def test_dynref_expression_building(self, timer, benchmark_config):
        """Benchmark expression building."""
        from dynamic_params import param_generator
        expression_times = []
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                ref1 =("a")
                ref2 =("b")
                expr = ref1 + ref2 * 2 -("c") /("d")
            expression_times.append(timer.elapsed)
        avg_time = sum(expression_times) / len(expression_times)
        assert avg_time < 2, f" expression building took {avg_time:.2f}ms (expected < 2ms)"
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
    def test__decorator(self, timer, benchmark_config):
        """Benchmark @ decorator application."""
        decorator_times = []
        for _ in range(benchmark_config["benchmark_iterations"]):
            with timer:
                @pytest.mark.parametrize("x", [[1], [2], [3]])
                def temp_test(x):
                    return x
            decorator_times.append(timer.elapsed)
        avg_time = sum(decorator_times) / len(decorator_times)
        assert avg_time < 10, f"@ decorator took {avg_time:.2f}ms (expected < 10ms)"
class TestOverallPerformance:
    """Overall performance benchmarks."""
    def test_end_to_end_parametrization(self, timer, benchmark_config):
        """Benchmark end-to-end parametrization workflow."""
        @param_generator(cache=True)
        def generate_data():
            return list(range(50))
        @pytest.mark.parametrize("value", generate_data)
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
        @pytest.mark.parametrize("static", [[1], [2], [3]])
        @pytest.mark.parametrize("dynamic", generate_dynamic)
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
