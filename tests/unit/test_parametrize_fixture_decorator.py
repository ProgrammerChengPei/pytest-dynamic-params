# Test parametrize_fixture decorator functionality
import pytest
from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture
from dynamic_params.public.decorators.param_generator import param_generator
class TestParametrizeFixtureBasic:
    """Test basic parametrize_fixture functionality"""
    def test_fixture_parametrization_basic(self):
        """Test parametrizing a fixture with basic values"""
        @parametrize_fixture("value", [1, 2, 3])
        def my_fixture(value):
            return value * 2
        assert hasattr(my_fixture, "_dynamic_parametrize")
        param_config = my_fixture._dynamic_parametrize
        assert param_config["args"] == "value"
        assert param_config["argvalues"] == [1, 2, 3]
        assert param_config.get("scope") == "function"  # Default scope
    def test_fixture_with_scope(self):
        """Test fixture with explicit scope"""
        @parametrize_fixture("data", ["a", "b"], scope="session")
        def session_fixture(data):
            return data.upper()
        param_config = session_fixture._dynamic_parametrize
        assert param_config["scope"] == "session"
    def test_fixture_with_params_kwarg(self):
        """Test fixture using params parameter"""
        @parametrize_fixture(params=[10, 20, 30])
        def params_fixture(request):
            return request.param
        param_config = params_fixture._dynamic_parametrize
        assert param_config["args"] == ""
        assert param_config["argvalues"] == [10, 20, 30]
class TestParametrizeFixtureWithGenerators:
    """Test fixture parametrization with generators"""
    def test_fixture_with_generator_reference(self):
        """Test referencing a registered generator"""
        @param_generator
        def number_generator():
            return [100, 200, 300]
        @parametrize_fixture("num", "number_generator")
        def generated_fixture(num):
            return num + 50
        param_config = generated_fixture._dynamic_parametrize
        assert param_config["argvalues"] == "number_generator"
    def test_fixture_with_generator_function(self):
        """Test using generator function directly"""
        def local_generator():
            return [5, 10, 15]
        @parametrize_fixture("value", local_generator)
        def direct_generator_fixture(value):
            return value * 3
        param_config = direct_generator_fixture._dynamic_parametrize
        assert param_config["argvalues"] == local_generator
    def test_fixture_with_dynref_syntax(self):
        """Test using syntax for generator references"""
        @param_generator
        def data_generator():
            return [{"x": 1}, {"x": 2}]
        @parametrize_fixture("data", "data_generator")
        def dynref_fixture(data):
            return data["x"] * 10
        param_config = dynref_fixture._dynamic_parametrize
        assert param_config["argvalues"] == "data_generator"
class TestParametrizeFixtureEdgeCases:
    """Test edge cases and special scenarios"""
    def test_fixture_without_parameters(self):
        """Test fixture with empty parametrization"""
        @parametrize_fixture("", [])
        def empty_fixture():
            return "constant"
        param_config = empty_fixture._dynamic_parametrize
        assert param_config["args"] == ""
        assert param_config["argvalues"] == []
    def test_fixture_with_single_parameter(self):
        """Test fixture with single parameter value"""
        @parametrize_fixture("x", [42])
        def single_param_fixture(x):
            return x
        param_config = single_param_fixture._dynamic_parametrize
        assert param_config["argvalues"] == [42]
    def test_fixture_accepts_pytest_fixture_args(self):
        """Test that fixture can accept standard pytest fixture arguments"""
        @parametrize_fixture("base", [1, 2], autouse=True, name="custom_fixture")
        def complex_fixture(base):
            return base * 10
        # Should preserve pytest fixture attributes
        assert hasattr(complex_fixture, "_pytestfixturefunction")
        fixture_func = complex_fixture._pytestfixturefunction
        assert fixture_func.autouse is True
        assert fixture_func.name == "custom_fixture"
class TestParametrizeFixtureErrorHandling:
    """Test error handling for parametrize_fixture"""
    def test_invalid_generator_reference(self):
        """Test referencing non-existent generator"""
        with pytest.raises(ValueError):
            @parametrize_fixture("data", "nonexistent_generator")
            def bad_fixture(data):
                return data
    def test_mismatched_parameter_count(self):
        """Test when parameter count doesn't match function signature"""
        with pytest.raises(TypeError):
            @parametrize_fixture("a,b", [[1, 2]])
            def mismatched_fixture(a):  # Expects 1 param but gets 2
                return a
    def test_invalid_scope_value(self):
        """Test with invalid scope value"""
        with pytest.raises(ValueError):
            @parametrize_fixture("x", [1], scope="invalid_scope")
            def invalid_scope_fixture(x):
                return x
class TestParametrizeFixtureIntegration:
    """Test integration with pytest fixture system"""
    def test_fixture_function_metadata_preserved(self):
        """Test that original function metadata is preserved"""
        def original_fixture(value):
            """Original fixture docstring"""
            return value
        decorated_fixture = parametrize_fixture("value", [1, 2])(original_fixture)
        assert decorated_fixture.__name__ == "original_fixture"
        assert decorated_fixture.__doc__ == "Original fixture docstring"
    def test_multiple_decorator_compatibility(self):
        """Test compatibility with other pytest decorators"""
        import pytest as pt
        @pt.mark.usefixtures("other_fixture")
        @parametrize_fixture("x", [10])
        @pt.fixture(scope="session")
        def multi_decorator_fixture(x):
            return x
        # Should have both parametrize and fixture attributes
        assert hasattr(multi_decorator_fixture, "_dynamic_parametrize")
        assert hasattr(multi_decorator_fixture, "_pytestfixturefunction")