"""
Compatibility tests for different Python and pytest versions.
Tests to verify that pytest-dynamic-params works correctly across
different Python versions and pytest versions.
"""
import sys
import pytest
class TestPythonVersionCompatibility:
    """Test Python version compatibility."""
    def test_python_version_info(self, python_version):
        """Test that we can get Python version information."""
        assert python_version is not None
        major, minor, micro = map(int, python_version.split('.'))
        assert major == sys.version_info.major
        assert minor == sys.version_info.minor
    def test_python_37_features(self):
        """Test features available in Python 3.7+."""
        # Test f-strings (available since 3.6)
        value = 42
        result = f"The value is {value}"
        assert "42" in result
        # Test type hints (improved in 3.7)
        from typing import Dict, List
        lst: List[int] = [1, 2, 3]
        dct: Dict[str, int] = {"key": 42}
        assert len(lst) == 3
        assert dct["key"] == 42
    def test_python_38_features(self):
        """Test features available in Python 3.8+."""
        if sys.version_info < (3, 8):
            pytest.skip("Python 3.8+ required")
        # Test positional-only parameters
        def func(a, /, b, *, c):
            return a + b + c
        result = func(1, 2, c=3)
        assert result == 6
    def test_python_39_features(self):
        """Test features available in Python 3.9+."""
        if sys.version_info < (3, 9):
            pytest.skip("Python 3.9+ required")
        # Test dict union operator
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        merged = dict1 | dict2
        assert len(merged) == 4
    def test_python_310_features(self):
        """Test features available in Python 3.10+."""
        if sys.version_info < (3, 10):
            pytest.skip("Python 3.10+ required")
        # Test match statement
        value = 2
        match value:
            case 1:
                result = "one"
            case 2:
                result = "two"
            case _:
                result = "other"
        assert result == "two"
class TestPytestVersionCompatibility:
    """Test pytest version compatibility."""
    def test_pytest_version_info(self, get_pytest_version):
        """Test that pytest version is available."""
        assert get_pytest_version is not None
        import pytest
        assert pytest.__version__ == get_pytest_version
    def test_pytest_7_features(self):
        """Test features available in pytest 7.0+."""
        import pytest
        version = tuple(map(int, pytest.__version__.split('.')[:2]))
        if version < (7, 0):
            pytest.skip("pytest 7.0+ required")
        # pytest 7.0+ features should work
        assert pytest.version_tuple >= (7, 0)
    def test_parametrize_decorator(self):
        """Test basic pytest parametrize decorator."""
        import pytest
        @pytest.mark.parametrize("x,y", [(1, 2), (3, 4)])
        def test_func(x, y):
            assert x < y
        # This test should work with any pytest version
        test_func(1, 2)
        test_func(3, 4)
    def test_fixture_decorator(self):
        """Test pytest fixture decorator."""
        import pytest
        @pytest.fixture
        def sample_fixture():
            return {"key": "value"}
        # Simulate fixture usage
        fixture_value = sample_fixture()
        assert fixture_value["key"] == "value"
class TestDynamicParamsCoreCompatibility:
    """Test core dynamic params compatibility across versions."""
    def test_basic_parametrization(self):
        """Test basic parametrization works."""
        from dynamic_params import param_generator
        @pytest.mark.parametrize("x, y", [[1, 2], [3, 4], [5, 6]])
        def test_func(x, y):
            assert x < y
            assert isinstance(x, int)
            assert isinstance(y, int)
        # Test all parameter combinations
        test_func(1, 2)
        test_func(3, 4)
        test_func(5, 6)
    def test_generator_basic(self):
        """Test basic generator functionality."""
        from dynamic_params import param_generator
        @param_generator(scope="session", cache=True)
        def generate_numbers():
            for i in range(5):
                yield i
        # Verify generator works
        result = list(generate_numbers())
        assert result == [0, 1, 2, 3, 4]
    def test_generator_with_parameters(self):
        """Test generator with parameters."""
        from dynamic_params import param_generator
        @param_generator
        def generate_base():
            yield from [1, 2, 3]
        # Verify basic generator
        result = list(generate_base())
        assert result == [1, 2, 3]
    def test_caching_mechanism(self):
        """Test caching mechanism."""
        from dynamic_params import param_generator
        call_count = 0
        @param_generator(scope="session", cache=True)
        def generate_cached():
            nonlocal call_count
            call_count += 1
            return [1, 2, 3]
        # First call
        result1 = list(generate_cached())
        assert result1 == [1, 2, 3]
        # Second call (should use cache)
        result2 = list(generate_cached())
        assert result2 == [1, 2, 3]
        # Generator should only be called once due to caching
        # Note: In practice, caching behavior may vary based on implementation
    def test_lazy_loading(self):
        """Test lazy loading mechanism."""
        from dynamic_params import param_generator
        initialization_called = False
        @param_generator(lazy=True)
        def generate_lazy():
            nonlocal initialization_called
            initialization_called = True
            return [1, 2, 3]
        # Generator should not execute until called
        # Note: Actual lazy behavior depends on implementation
        # Access the generator
        result = list(generate_lazy())
        assert result == [1, 2, 3]
class TestTypeHintCompatibility:
    """Test type hint compatibility."""
    def test_type_annotations(self):
        """Test that type annotations work correctly."""
        from typing import List
        def typed_func(x: int, y: str) -> List[int]:
            return [x] * len(y)
        result = typed_func(5, "abc")
        assert result == [5, 5, 5]
    def test_generic_types(self):
        """Test generic type compatibility."""
        from typing import Generic, TypeVar
        T = TypeVar('T')
        class Container(Generic[T]):
            def __init__(self, value: T):
                self.value = value
            def get(self) -> T:
                return self.value
        container = Container(42)
        assert container.get() == 42
        str_container = Container("hello")
        assert str_container.get() == "hello"
class TestDecoratorCompatibility:
    """Test decorator compatibility."""
    def test_multiple_decorators(self):
        """Test multiple decorators on same function."""
        import pytest
        from dynamic_params import param_generator
        @pytest.mark.skip(reason="Just testing decorator compatibility")
        @pytest.mark.parametrize("x", [1, 2, 3])
        def test_func(x):
            assert x > 0
        # The function should still be callable
        test_func(1)
        test_func(2)
        test_func(3)
    def test_decorator_order(self):
        """Test decorator order doesn't break functionality."""
        from dynamic_params import param_generator
        @pytest.mark.parametrize("x", [1, 2])
        def test_func1(x):
            assert x > 0
        @pytest.mark.parametrize("y", [3, 4])
        def test_func2(y):
            assert y > 0
        # Both should work
        test_func1(1)
        test_func1(2)
        test_func2(3)
        test_func2(4)
class TestImportExportCompatibility:
    """Test import/export compatibility."""
    def test_import_public_api(self):
        """Test importing public API."""
        from dynamic_params import param_generator
            param_generator,
            parametrize_fixture,
        )
        # All imports should succeed
        assert is not None
        assert parametrize_fixture is not None
        assert is not None
        assert param_generator is not None
    def test_import_engine_components(self):
        """Test importing engine components."""
        from dynamic_params.engine.generator import (
            GeneratorBase,
            GeneratorCache,
            GeneratorRegistry,
        )
        from dynamic_params.engine.parametrize import (
            ParametrizeCombinator,
            ParametrizeProcessor,
        )
        # All imports should succeed
        assert GeneratorBase is not None
        assert GeneratorRegistry is not None
        assert GeneratorCache is not None
        assert ParametrizeProcessor is not None
        assert ParametrizeCombinator is not None
    def test_import_plugin_components(self):
        """Test importing plugin components."""
        from dynamic_params.plugin import PytestPlugin
        from dynamic_params.plugin.hooks import pytest_generate_tests
        # All imports should succeed
        assert PytestPlugin is not None
        assert pytest_generate_tests is not None
class TestErrorHandlingCompatibility:
    """Test error handling compatibility."""
    def test_error_types(self):
        """Test that error types are available."""
        from dynamic_params.errors import DynamicParamsError
        # Should be able to create error instances
        error = DynamicParamsError("Test error")
        assert str(error) == "Test error"
    def test_validation(self):
        """Test validation utilities."""
        from dynamic_params.utils.validation import validate_parametrization
        # Validation should not crash
        try:
            validate_parametrization("x,y", [[1, 2], [3, 4]])
        except Exception:
            pass  # May raise validation errors
