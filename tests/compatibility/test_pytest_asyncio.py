"""
Compatibility tests with pytest-asyncio plugin.

Tests to verify that pytest-dynamic-params works correctly with pytest-asyncio
for async test functions.
"""
import pytest
import sys
import subprocess
from pathlib import Path


class TestAsyncioBasicCompatibility:
    """Test basic compatibility with pytest-asyncio."""
    
    def test_asyncio_with_dynamic_params(self, isolated_test_env, run_pytest_cmd):
        """Test that dynamic params work with async test functions."""
        test_file = isolated_test_env / "test_asyncio_basic.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import parametrize_test

pytest_plugins = ('pytest_asyncio',)

@parametrize_test("x, y", [[1, 2], [3, 4], [5, 6]])
@pytest.mark.asyncio
async def test_async_parametrization(x, y):
    '''Test async function with parametrization'''
    await asyncio.sleep(0.01)
    result = x + y
    assert result > 0
    assert isinstance(result, int)

@parametrize_test("value", [1, 2, 3])
@pytest.mark.asyncio
async def test_async_basic(value):
    '''Test basic async parametrization'''
    await asyncio.sleep(0.001)
    assert value > 0
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_asyncio_with_generators(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with generator-based parametrization."""
        test_file = isolated_test_env / "test_asyncio_generator.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import param_generator, parametrize_test

pytest_plugins = ('pytest_asyncio',)

@param_generator(scope="session", cache=True)
def generate_numbers():
    '''Generate numbers for async testing'''
    for i in range(5):
        yield i

@parametrize_test("num", generate_numbers)
@pytest.mark.asyncio
async def test_async_generator(num):
    '''Test async function with generator'''
    await asyncio.sleep(0.001)
    assert isinstance(num, int)
    assert 0 <= num < 5
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestAsyncioWithDynRef:
    """Test pytest-asyncio with DynRef functionality."""
    
    def test_asyncio_dynref_basic(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with basic DynRef usage."""
        test_file = isolated_test_env / "test_asyncio_dynref.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import parametrize_test, DynRef

pytest_plugins = ('pytest_asyncio',)

@parametrize_test("a, b, expected", [
    [1, 2, DynRef("a") + DynRef("b")],
    [3, 4, DynRef("a") + DynRef("b")],
    [5, 6, DynRef("a") + DynRef("b")],
])
@pytest.mark.asyncio
async def test_async_dynref(a, b, expected):
    '''Test async function with DynRef'''
    await asyncio.sleep(0.001)
    result = a + b
    assert result == expected
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestAsyncioWithFixtures:
    """Test pytest-asyncio with fixture parametrization."""
    
    def test_asyncio_fixture_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with parametrized fixtures."""
        test_file = isolated_test_env / "test_asyncio_fixture.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import parametrize_fixture, param_generator

pytest_plugins = ('pytest_asyncio',)

@param_generator
def generate_values():
    '''Generate values for async fixture'''
    yield from [10, 20, 30]

@parametrize_fixture("value", generate_values)
@pytest.fixture
def async_fixture_value(value):
    '''Parametrized fixture for async tests'''
    return value * 2

@pytest.mark.asyncio
async def test_async_fixture(async_fixture_value):
    '''Test async function with parametrized fixture'''
    await asyncio.sleep(0.001)
    assert async_fixture_value in [20, 40, 60]
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_asyncio_async_fixture(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with async fixtures."""
        test_file = isolated_test_env / "test_asyncio_async_fixture.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import parametrize_test

pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
@pytest.mark.asyncio
async def async_fixture():
    '''Async fixture'''
    await asyncio.sleep(0.001)
    return {"key": "value"}

@parametrize_test("multiplier", [2, 3, 4])
@pytest.mark.asyncio
async def test_async_with_async_fixture(async_fixture, multiplier):
    '''Test async function with async fixture'''
    await asyncio.sleep(0.001)
    assert async_fixture["key"] == "value"
    assert multiplier > 1
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestAsyncioWithCaching:
    """Test pytest-asyncio with caching features."""
    
    def test_asyncio_caching(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with generator caching."""
        test_file = isolated_test_env / "test_asyncio_cache.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import param_generator, parametrize_test

pytest_plugins = ('pytest_asyncio',)

@param_generator(scope="session", cache=True)
def generate_cached_data():
    '''Cached generator for async tests'''
    return [i for i in range(5)]

@parametrize_test("value", generate_cached_data)
@pytest.mark.asyncio
async def test_async_caching(value):
    '''Test async function with caching'''
    await asyncio.sleep(0.001)
    assert value in [0, 1, 2, 3, 4]
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_asyncio_lazy_loading(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with lazy loading."""
        test_file = isolated_test_env / "test_asyncio_lazy.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import param_generator, parametrize_test

pytest_plugins = ('pytest_asyncio',)

@param_generator(lazy=True, cache=True)
def generate_lazy_data():
    '''Lazy loaded data for async tests'''
    return [i * 2 for i in range(5)]

@parametrize_test("value", generate_lazy_data)
@pytest.mark.asyncio
async def test_async_lazy(value):
    '''Test async function with lazy loading'''
    await asyncio.sleep(0.001)
    assert value in [0, 2, 4, 6, 8]
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestAsyncioEdgeCases:
    """Test edge cases with pytest-asyncio."""
    
    def test_asyncio_nested_generators(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with nested generators."""
        test_file = isolated_test_env / "test_asyncio_nested.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import param_generator, parametrize_generator, parametrize_test

pytest_plugins = ('pytest_asyncio',)

@param_generator
def generate_base():
    '''Base generator'''
    yield from [1, 2, 3]

@parametrize_generator("base", generate_base)
@param_generator
def generate_nested(base):
    '''Nested generator'''
    yield base * 2

@parametrize_test("value", generate_nested)
@pytest.mark.asyncio
async def test_async_nested(value):
    '''Test async function with nested generators'''
    await asyncio.sleep(0.001)
    assert value in [2, 4, 6]
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_asyncio_mixed_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test async tests with mixed parametrization."""
        test_file = isolated_test_env / "test_asyncio_mixed.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import parametrize_test, param_generator, DynRef

pytest_plugins = ('pytest_asyncio',)

@param_generator
def generate_values():
    '''Generate values'''
    yield from [1, 2, 3]

@parametrize_test("base", generate_values)
@parametrize_test("multiplier", [2, 3])
@pytest.mark.asyncio
async def test_async_mixed(base, multiplier):
    '''Test async function with mixed parametrization'''
    await asyncio.sleep(0.001)
    result = base * multiplier
    assert result > 0

@parametrize_test("x, y, sum", [
    [1, 2, DynRef("x") + DynRef("y")],
    [3, 4, DynRef("x") + DynRef("y")],
])
@pytest.mark.asyncio
async def test_async_dynref_mixed(x, y, sum):
    '''Test async function with DynRef'''
    await asyncio.sleep(0.001)
    assert x + y == sum
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_asyncio_concurrent_execution(self, isolated_test_env, run_pytest_cmd):
        """Test concurrent async test execution."""
        test_file = isolated_test_env / "test_asyncio_concurrent.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import parametrize_test

pytest_plugins = ('pytest_asyncio',)

@parametrize_test("delay", [0.01, 0.02, 0.03])
@pytest.mark.asyncio
async def test_concurrent(delay):
    '''Test concurrent async execution'''
    await asyncio.sleep(delay)
    assert delay > 0
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestAsyncioStressTests:
    """Stress tests for pytest-asyncio compatibility."""
    
    def test_asyncio_high_volume(self, isolated_test_env, run_pytest_cmd):
        """Test high volume of async tests."""
        test_file = isolated_test_env / "test_asyncio_stress.py"
        test_file.write_text("""
import pytest
import asyncio
from dynamic_params import param_generator, parametrize_test

pytest_plugins = ('pytest_asyncio',)

@param_generator(scope="session")
def generate_stress_cases():
    '''Generate many async test cases'''
    for i in range(50):
        yield i

@parametrize_test("case_id", generate_stress_cases)
@pytest.mark.asyncio
async def test_async_stress(case_id):
    '''Stress test with many async cases'''
    await asyncio.sleep(0.001)
    assert isinstance(case_id, int)
    assert 0 <= case_id < 50
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["-v", "--asyncio-mode=auto", "-q"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
