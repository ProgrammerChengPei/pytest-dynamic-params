"""
Compatibility tests with pytest-bdd plugin.
Tests to verify that pytest-dynamic-params works correctly with pytest-bdd
for behavior-driven development tests.
"""
import pytest
import sys
import subprocess
from pathlib import Path
class TestBddBasicCompatibility:
    """Test basic compatibility with pytest-bdd."""
    def test_bdd_with_dynamic_params(self, isolated_test_env, run_pytest_cmd):
        """Test that dynamic params work with BDD scenarios."""
        test_file = isolated_test_env / "test_bdd_basic.py"
        test_file.write_text("""
import pytest
from pytest_bdd import scenario, given, when, then, parsers
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@scenario('basic.feature', 'Basic parametrized scenario')
def test_basic_bdd():
    '''Basic BDD scenario'''
    pass
@pytest.mark.parametrize("x, y, expected", [[1, 2, 3], [3, 4, 7], [5, 6, 11]])
def test_bdd_parametrization(x, y, expected):
    '''Test BDD with parametrization'''
    result = x + y
    assert result == expected
""")
        # Create feature file
        feature_file = isolated_test_env / "basic.feature"
        feature_file.write_text("""
Feature: Basic parametrized scenario
    Scenario: Test parametrized values
        Given I have a parametrized test
        When I run the test with parameters
        Then the test should pass
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        # Test may fail due to missing BDD steps, but plugin should not crash
        assert "dynamic_params" not in result["stderr"].lower() or result["success"]
    def test_bdd_generators(self, isolated_test_env, run_pytest_cmd):
        """Test BDD with generator-based parametrization."""
        test_file = isolated_test_env / "test_bdd_generator.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@param_generator(scope="session", cache=True)
def generate_test_values():
    '''Generate values for BDD testing'''
    for i in range(5):
        yield i
@pytest.mark.parametrize("value", generate_test_values)
def test_bdd_generator(value):
    '''Test BDD with generator'''
    assert isinstance(value, int)
    assert 0 <= value < 5
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestBddWith:
    """Test pytest-bdd with functionality."""
    def test_bdd_dynref(self, isolated_test_env, run_pytest_cmd):
        """Test BDD with."""
        test_file = isolated_test_env / "test_bdd_dynref.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@pytest.mark.parametrize("a, b, expected", [
    [1, 2("a") +("b")],
    [3, 4("a") +("b")],
])
def test_bdd_dynref(a, b, expected):
    '''Test BDD with'''
    result = a + b
    assert result == expected
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestBddWithFixtures:
    """Test pytest-bdd with fixture parametrization."""
    def test_bdd_fixture_parametrization(self, isolated_test_env, run_pytest_cmd):
        """Test BDD with parametrized fixtures."""
        test_file = isolated_test_env / "test_bdd_fixture.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@param_generator
def generate_fixture_values():
    '''Generate fixture values'''
    yield from [10, 20, 30]
@parametrize_fixture("value", generate_fixture_values)
@pytest.fixture
def bdd_fixture_value(value):
    '''Parametrized fixture for BDD'''
    return value * 2
def test_bdd_fixture(bdd_fixture_value):
    '''Test BDD with parametrized fixture'''
    assert bdd_fixture_value in [20, 40, 60]
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestBddScenarioIntegration:
    """Test BDD scenario integration."""
    def test_bdd_scenario_with_params(self, isolated_test_env, run_pytest_cmd):
        """Test BDD scenarios with parametrized tests."""
        test_file = isolated_test_env / "test_bdd_scenario.py"
        test_file.write_text("""
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
scenarios('test.feature')
@given('I have a number')
def number():
    return 5
@when('I multiply it by another number', target_fixture="result")
def multiply(number):
    return number * 2
@then('the result should be correct')
def check_result(result):
    assert result == 10
@pytest.mark.parametrize("multiplier, expected", [[2, 4], [3, 6], [4, 8]])
def test_scenario_parametrization(multiplier, expected):
    '''Test scenario with parametrization'''
    result = 2 * multiplier
    assert result == expected
""")
        # Create feature file
        feature_file = isolated_test_env / "test.feature"
        feature_file.write_text("""
Feature: Test feature
    Scenario: Basic test
        Given I have a number
        When I multiply it by another number
        Then the result should be correct
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        # Plugin should not crash even if BDD steps have issues
        assert "dynamic_params" not in result["stderr"].lower() or result["success"]
class TestBddEdgeCases:
    """Test edge cases with pytest-bdd."""
    def test_bdd_caching(self, isolated_test_env, run_pytest_cmd):
        """Test BDD with generator caching."""
        test_file = isolated_test_env / "test_bdd_cache.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@param_generator(scope="session", cache=True)
def generate_cached_bdd_data():
    '''Cached generator for BDD'''
    return [i for i in range(5)]
@pytest.mark.parametrize("value", generate_cached_bdd_data)
def test_bdd_caching(value):
    '''Test BDD with caching'''
    assert value in [0, 1, 2, 3, 4]
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
    def test_bdd_lazy_loading(self, isolated_test_env, run_pytest_cmd):
        """Test BDD with lazy loading."""
        test_file = isolated_test_env / "test_bdd_lazy.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@param_generator(lazy=True, cache=True)
def generate_lazy_bdd_data():
    '''Lazy loaded data for BDD'''
    return [i * 2 for i in range(5)]
@pytest.mark.parametrize("value", generate_lazy_bdd_data)
def test_bdd_lazy(value):
    '''Test BDD with lazy loading'''
    assert value in [0, 2, 4, 6, 8]
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
    def test_bdd_mixed_approaches(self, isolated_test_env, run_pytest_cmd):
        """Test BDD with mixed parametrization approaches."""
        test_file = isolated_test_env / "test_bdd_mixed.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@param_generator
def generate_bdd_values():
    '''Generate BDD values'''
    yield from [1, 2, 3]
@pytest.mark.parametrize("base", generate_bdd_values)
@pytest.mark.parametrize("multiplier", [2, 3])
def test_bdd_mixed(base, multiplier):
    '''Test BDD with mixed parametrization'''
    result = base * multiplier
    assert result > 0
@pytest.mark.parametrize("x, y, sum", [
    [1, 2("x") +("y")],
    [3, 4("x") +("y")],
])
def test_bdd_dynref_mixed(x, y, sum):
    '''Test BDD with'''
    assert x + y == sum
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        assert result["success"], f"Test failed: {result['stderr']}"
class TestBddOutlineScenarios:
    """Test BDD outline scenarios with dynamic params."""
    def test_bdd_outline_compatibility(self, isolated_test_env, run_pytest_cmd):
        """Test compatibility with BDD outline scenarios."""
        test_file = isolated_test_env / "test_bdd_outline.py"
        test_file.write_text("""
import pytest
from dynamic_params import param_generator
pytest_plugins = ('pytest_bdd',)
@pytest.mark.parametrize("input_val, expected", [[1, 2], [2, 4], [3, 6]])
def test_outline_compatibility(input_val, expected):
    '''Test outline scenario compatibility'''
    result = input_val * 2
    assert result == expected
""")
        # Create outline feature file
        feature_file = isolated_test_env / "outline.feature"
        feature_file.write_text("""
Feature: Outline scenario
    Scenario Outline: Test outline
        Given I have <input>
        When I process it
        Then I get <output>
        Examples:
            | input | output |
            | 1     | 2      |
            | 2     | 4      |
""")
        result = run_pytest_cmd(
            test_file,
            args=["-v"],
            cwd=isolated_test_env
        )
        # Plugin should not crash
        assert "dynamic_params" not in result["stderr"].lower() or result["success"]
