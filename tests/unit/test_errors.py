# Test errors functionality
import pytest
from dynamic_params.errors import (
    DynamicParamsError,
    DependencyError,
    CircularDependencyError,
    GeneratorError,
    GeneratorNotFoundError,
    ParametrizeErrorError,
    ConfigError,
    ConfigurationError
)
class TestErrors:
    """Test error classes"""
    def test_dynamic_params_error(self):
        """Test DynamicParamsError"""
        with pytest.raises(DynamicParamsError):
            raise DynamicParamsError("Test error")
    def test_dependency_error(self):
        """Test DependencyError"""
        with pytest.raises(DependencyError):
            raise DependencyError("Dependency error")
    def test_dependency_error_is_dynamic_params_error(self):
        """Test DependencyError is DynamicParamsError"""
        error = DependencyError("Test")
        assert isinstance(error, DynamicParamsError)
    def test_circular_dependency_error(self):
        """Test CircularDependencyError"""
        with pytest.raises(CircularDependencyError):
            raise CircularDependencyError("Circular dependency")
    def test_circular_dependency_error_is_dependency_error(self):
        """Test CircularDependencyError is DependencyError"""
        error = CircularDependencyError("Test")
        assert isinstance(error, DependencyError)
        assert isinstance(error, DynamicParamsError)
    def test_generator_error(self):
        """Test GeneratorError"""
        with pytest.raises(GeneratorError):
            raise GeneratorError("Generator error")
    def test_generator_error_is_dynamic_params_error(self):
        """Test GeneratorError is DynamicParamsError"""
        error = GeneratorError("Test")
        assert isinstance(error, DynamicParamsError)
    def test_generator_not_found_error(self):
        """Test GeneratorNotFoundError"""
        with pytest.raises(GeneratorNotFoundError):
            raise GeneratorNotFoundError("Generator not found")
    def test_generator_not_found_error_is_generator_error(self):
        """Test GeneratorNotFoundError is GeneratorError"""
        error = GeneratorNotFoundError("Test")
        assert isinstance(error, GeneratorError)
        assert isinstance(error, DynamicParamsError)
    def test_parametrize_error(self):
        """Test ParametrizeError"""
        with pytest.raises(ParametrizeError):
            raise ParametrizeError("Parametrize error")
    def test_parametrize_error_is_dynamic_params_error(self):
        """Test ParametrizeError is DynamicParamsError"""
        error = ParametrizeError("Test")
        assert isinstance(error, DynamicParamsError)
    def test_dynref_error(self):
        """TestError"""
        with pytest.raises(Error):
            raiseError(" error")
    def test_dynref_error_is_dynamic_params_error(self):
        """TestError is DynamicParamsError"""
        error =Error("Test")
        assert isinstance(error, DynamicParamsError)
    def test_config_error(self):
        """Test ConfigError"""
        with pytest.raises(ConfigError):
            raise ConfigError("Config error")
    def test_config_error_is_dynamic_params_error(self):
        """Test ConfigError is DynamicParamsError"""
        error = ConfigError("Test")
        assert isinstance(error, DynamicParamsError)
    def test_configuration_error(self):
        """Test ConfigurationError"""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Configuration error")
    def test_configuration_error_is_config_error(self):
        """Test ConfigurationError is ConfigError"""
        error = ConfigurationError("Test")
        assert isinstance(error, ConfigError)
        assert isinstance(error, DynamicParamsError)
    def test_error_message(self):
        """Test error message"""
        error = DynamicParamsError("Test error message")
        assert str(error) == "Test error message"
    def test_error_inheritance_chain(self):
        """Test error inheritance chain"""
        error = CircularDependencyError("Test")
        assert isinstance(error, DependencyError)
        assert isinstance(error, DynamicParamsError)
        assert isinstance(error, Exception)
