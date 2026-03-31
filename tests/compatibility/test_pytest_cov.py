"""
Compatibility tests with pytest-cov plugin.

Tests to verify that pytest-dynamic-params works correctly with pytest-cov
for test coverage measurement.
"""
import pytest
import sys
import subprocess
from pathlib import Path


class TestCovBasicCompatibility:
    """Test basic compatibility with pytest-cov."""
    
    def test_cov_with_dynamic_params(self, isolated_test_env, run_pytest_cmd):
        """Test that coverage works with dynamic params."""
        test_file = isolated_test_env / "test_cov_basic.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test

@parametrize_test("x, y", [[1, 2], [3, 4], [5, 6]])
def test_basic_coverage(x, y):
    '''Test basic parametrization with coverage'''
    result = x + y
    assert result > 0
    assert isinstance(result, int)
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "--cov-report=term-missing", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
        assert "coverage" in result["stdout"].lower() or "passed" in result["stdout"]
    
    def test_cov_with_generators(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with generator-based parametrization."""
        test_file = isolated_test_env / "test_cov_generator.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator, parametrize_test

@param_generator(scope="session", cache=True)
def generate_numbers():
    '''Generate numbers for coverage testing'''
    for i in range(10):
        yield i

@parametrize_test("num", generate_numbers)
def test_generator_coverage(num):
    '''Test generator with coverage'''
    assert isinstance(num, int)
    assert 0 <= num < 10
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "--cov-report=term", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestCovWithDynRef:
    """Test coverage with DynRef functionality."""
    
    def test_cov_dynref_basic(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with basic DynRef usage."""
        test_file = isolated_test_env / "test_cov_dynref.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test, DynRef

@parametrize_test("a, b, expected", [
    [1, 2, DynRef("a") + DynRef("b")],
    [3, 4, DynRef("a") + DynRef("b")],
    [5, 6, DynRef("a") + DynRef("b")],
])
def test_dynref_coverage(a, b, expected):
    '''Test DynRef with coverage'''
    result = a + b
    assert result == expected
    assert isinstance(result, int)
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_cov_dynref_complex(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with complex DynRef expressions."""
        test_file = isolated_test_env / "test_cov_dynref_complex.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test, DynRef

@parametrize_test("x, y, result", [
    [10, 5, DynRef("x") - DynRef("y")],
    [20, 4, DynRef("x") / DynRef("y")],
    [3, 7, DynRef("x") * DynRef("y")],
])
def test_complex_dynref_coverage(x, y, result):
    '''Test complex DynRef with coverage'''
    assert result > 0
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "--cov-report=term-missing", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestCovWithFixtures:
    """Test coverage with fixture parametrization."""
    
    def test_cov_fixture_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with parametrized fixtures."""
        test_file = isolated_test_env / "test_cov_fixture.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_fixture, param_generator

@param_generator
def generate_values():
    '''Generate values for fixture'''
    yield from [10, 20, 30, 40, 50]

@parametrize_fixture("value", generate_values)
@pytest.fixture
def fixture_value(value):
    '''Parametrized fixture'''
    return value * 2

def test_fixture_coverage(fixture_value):
    '''Test fixture with coverage'''
    assert fixture_value in [20, 40, 60, 80, 100]
    assert isinstance(fixture_value, int)
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestCovWithCaching:
    """Test coverage with caching enabled."""
    
    def test_cov_caching_enabled(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with generator caching."""
        test_file = isolated_test_env / "test_cov_cache.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator, parametrize_test
import time

call_count = 0

@param_generator(scope="session", cache=True)
def generate_cached_data():
    '''Cached generator data'''
    global call_count
    call_count += 1
    time.sleep(0.01)
    return [i for i in range(5)]

@parametrize_test("value", generate_cached_data)
def test_caching_coverage(value):
    '''Test caching with coverage'''
    assert value in [0, 1, 2, 3, 4]
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "--cov-report=term", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_cov_lazy_loading(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with lazy loading."""
        test_file = isolated_test_env / "test_cov_lazy.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator, parametrize_test

@param_generator(lazy=True, cache=True)
def generate_lazy_data():
    '''Lazy loaded data'''
    return [i * 2 for i in range(5)]

@parametrize_test("value", generate_lazy_data)
def test_lazy_coverage(value):
    '''Test lazy loading with coverage'''
    assert value in [0, 2, 4, 6, 8]
    assert isinstance(value, int)
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestCovReportGeneration:
    """Test coverage report generation."""
    
    def test_cov_html_report(self, isolated_test_env, run_pytest_cmd):
        """Test HTML coverage report generation."""
        test_file = isolated_test_env / "test_cov_html.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test, param_generator

@param_generator
def generate_data():
    '''Generate data'''
    yield from range(10)

@parametrize_test("num", generate_data)
def test_html_report(num):
    '''Test for HTML report'''
    assert isinstance(num, int)
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "--cov-report=html", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_cov_xml_report(self, isolated_test_env, run_pytest_cmd):
        """Test XML coverage report generation."""
        test_file = isolated_test_env / "test_cov_xml.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test

@parametrize_test("x, y", [[i, i+1] for i in range(5)])
def test_xml_report(x, y):
    '''Test for XML report'''
    assert x < y
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "--cov-report=xml", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_cov_multiple_reports(self, isolated_test_env, run_pytest_cmd):
        """Test generating multiple coverage reports."""
        test_file = isolated_test_env / "test_cov_multiple.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test, DynRef

@parametrize_test("a, b, sum", [
    [1, 2, DynRef("a") + DynRef("b")],
    [3, 4, DynRef("a") + DynRef("b")],
])
def test_multiple_reports(a, b, sum):
    '''Test for multiple reports'''
    assert a + b == sum
""")
        
        result = run_pytest_cmd(
            test_file,
            args=[
                "--cov=dynamic_params",
                "--cov-report=term",
                "--cov-report=html",
                "--cov-report=xml",
                "-v"
            ],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"


class TestCovEdgeCases:
    """Test edge cases with pytest-cov."""
    
    def test_cov_with_nested_generators(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with nested generators."""
        test_file = isolated_test_env / "test_cov_nested.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator, parametrize_generator, parametrize_test

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
def test_nested_coverage(value):
    '''Test nested generators with coverage'''
    assert value in [2, 4, 6]
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
    
    def test_cov_mixed_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test coverage with mixed parametrization."""
        test_file = isolated_test_env / "test_cov_mixed.py"
        test_file.write_text("""
import pytest
from dynamic_params import parametrize_test, param_generator, DynRef

@param_generator
def generate_values():
    '''Generate values'''
    yield from [1, 2, 3, 4, 5]

@parametrize_test("base", generate_values)
@parametrize_test("multiplier", [2, 3])
def test_mixed_coverage(base, multiplier):
    '''Test mixed parametrization with coverage'''
    result = base * multiplier
    assert result > 0

@parametrize_test("x, y", [[1, 2], [3, 4]])
def test_native_coverage(x, y):
    '''Test native pytest parametrization with coverage'''
    assert x < y
""")
        
        result = run_pytest_cmd(
            test_file,
            args=["--cov=dynamic_params", "-v"],
            cwd=isolated_test_env
        )
        
        assert result["success"], f"Test failed: {result['stderr']}"
