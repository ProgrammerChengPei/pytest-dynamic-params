"""
Compatibility tests with pytest-xdist plugin.
Tests to verify that pytest-dynamic-params works correctly with pytest-xdist
for parallel test execution.
"""
class TestXDistBasicCompatibility:
    """Test basic compatibility with pytest-xdist."""
    def test_xdist_parallel_execution(self, isolated_test_env, run_pytest_cmd):
        """Test that dynamic params work with parallel execution."""
        test_file = isolated_test_env / "test_parallel.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(scope="session", cache=True)
def generate_numbers():
    '''Generate numbers for parallel testing'''
    for i in range(10):
        yield i
@pytest.mark.parametrize("num", generate_numbers)
def test_parallel_parametrization(num):
    '''Test parametrization with parallel execution'''
    assert isinstance(num, int)
    assert num >= 0
    assert num < 10
@pytest.mark.parametrize("x, y", [[1, 2], [3, 4], [5, 6]])
def test_parallel_basic(x, y):
    '''Test basic parametrization with parallel execution'''
    assert x < y
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v"],
            cwd=isolated_test_env
        )
        print(f"Return code: {result['returncode']}")
        print(f"STDOUT:\n{result['stdout']}")
        print(f"STDERR:\n{result['stderr']}")
        assert result["success"], f"Test failed with return code {result['returncode']}"
        # Check if any tests passed
        assert "passed" in result["stdout"], f"No tests passed: {result['stdout']}"
    def test_xdist_with_fixture_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test fixture parametrization compatibility with parallel execution."""
        test_file = isolated_test_env / "test_fixture_xdist.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(scope="function")
def generate_values():
    '''Generate values for fixture'''
    yield from [10, 20, 30]
@parametrize_fixture("value", generate_values)
@pytest.fixture
def fixture_value(value):
    '''Parametrized fixture'''
    return value * 2
def test_fixture_parallel(fixture_value):
    '''Test fixture with parallel execution'''
    assert fixture_value in [20, 40, 60]
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestXDistDistributedCaching:
    """Test distributed caching with pytest-xdist."""
    def test_cache_consistency_across_workers(self, isolated_test_env, run_pytest_cmd):
        """Test that cache is consistent across different workers."""
        test_file = isolated_test_env / "test_cache_consistency.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
import time
call_count = 0
@param_generator(scope="session", cache=True)
def generate_expensive_data():
    '''Expensive data generation that should be cached'''
    global call_count
    call_count += 1
    time.sleep(0.1)  # Simulate expensive operation
    return [i * 2 for i in range(5)]
@pytest.mark.parametrize("value", generate_expensive_data)
def test_cache_consistency(value):
    '''Test that cached values are consistent'''
    assert value in [0, 2, 4, 6, 8]
    assert isinstance(value, int)
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v", "-s"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
    def test_session_scope_caching_xdist(self, isolated_test_env, run_pytest_cmd):
        """Test session-scoped caching with parallel execution."""
        test_file = isolated_test_env / "test_session_cache.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(scope="session", cache=True)
def generate_session_data():
    '''Session-scoped cached data'''
    return {"key": "value", "count": 42}
@pytest.mark.parametrize("data", [generate_session_data])
def test_session_cache(data):
    '''Test session-scoped cache'''
    assert isinstance(data, dict)
    assert "key" in data
    assert "count" in data
    assert data["count"] == 42
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestXDistLoadBalancing:
    """Test load balancing with pytest-xdist."""
    def test_load_balancing_with_generators(self, isolated_test_env, run_pytest_cmd):
        """Test that load balancing works correctly with generators."""
        test_file = isolated_test_env / "test_load_balance.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(scope="module")
def generate_test_cases():
    '''Generate many test cases for load balancing'''
    for i in range(20):
        yield i
@pytest.mark.parametrize("case_id", generate_test_cases)
def test_load_balancing(case_id):
    '''Test load balancing with many generated cases'''
    assert isinstance(case_id, int)
    assert 0 <= case_id < 20
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "4", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
        assert "20 passed" in result["stdout"]
    def test_load_balancing_mixed_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test load balancing with mixed parametrization."""
        test_file = isolated_test_env / "test_mixed_load_balance.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator
def generate_base_values():
    '''Generate base values'''
    yield from [1, 2, 3, 4, 5]
@pytest.mark.parametrize("base", generate_base_values)
@pytest.mark.parametrize("multiplier", [2, 3])
def test_mixed_parametrization(base, multiplier):
    '''Test mixed parametrization with load balancing'''
    result = base * multiplier
    assert result > 0
    assert isinstance(result, int)
@pytest.mark.parametrize("x, y, sum", [
    [1, 2("x") +("y")],
    [3, 4("x") +("y")],
])
def test_dynref_load_balance(x, y, sum):
    '''Test with load balancing'''
    assert x + y == sum
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestXDistEdgeCases:
    """Test edge cases with pytest-xdist."""
    def test_xdist_with_lazy_loading(self, isolated_test_env, run_pytest_cmd):
        """Test lazy loading compatibility with parallel execution."""
        test_file = isolated_test_env / "test_lazy_xdist.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(lazy=True, cache=True)
def generate_lazy_data():
    '''Lazy loaded data'''
    return [i for i in range(5)]
@pytest.mark.parametrize("value", generate_lazy_data)
def test_lazy_loading_parallel(value):
    '''Test lazy loading with parallel execution'''
    assert value in [0, 1, 2, 3, 4]
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
    def test_xdist_with_nested_generators(self, isolated_test_env, run_pytest_cmd):
        """Test nested generators with parallel execution."""
        test_file = isolated_test_env / "test_nested_xdist.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator
def generate_base():
    '''Base generator'''
    yield from [1, 2, 3]
@("base_value", generate_base)
@param_generator
def generate_nested(base_value):
    '''Nested generator'''
    yield base_value * 2
@pytest.mark.parametrize("value", generate_nested)
def test_nested_generators_parallel(value):
    '''Test nested generators with parallel execution'''
    assert value in [2, 4, 6]
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "2", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
    def test_xdist_single_worker(self, isolated_test_env, run_pytest_cmd):
        """Test with single worker (n=1) to ensure compatibility."""
        test_file = isolated_test_env / "test_single_worker.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(scope="session", cache=True)
def generate_data():
    '''Generate data'''
    yield from range(10)
@pytest.mark.parametrize("num", generate_data)
def test_single_worker(num):
    '''Test with single worker'''
    assert isinstance(num, int)
@pytest.mark.parametrize("a, b", [[1, 2], [3, 4]])
def test_single_worker_dynref(a, b):
    '''Test with single worker'''
    assert a < b
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "1", "-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestXDistStressTests:
    """Stress tests for pytest-xdist compatibility."""
    def test_high_volume_parallel_execution(self, isolated_test_env, run_pytest_cmd):
        """Test high volume of tests with parallel execution."""
        test_file = isolated_test_env / "test_stress.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
@param_generator(scope="session")
def generate_stress_cases():
    '''Generate many test cases'''
    for i in range(100):
        yield i
@pytest.mark.parametrize("case_id", generate_stress_cases)
def test_stress_parallel(case_id):
    '''Stress test with many cases'''
    assert isinstance(case_id, int)
    assert 0 <= case_id < 100
""")
        result = run_pytest_cmd(
            test_file,
            args=["-n", "4", "-q"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
        assert "100 passed" in result["stdout"]
