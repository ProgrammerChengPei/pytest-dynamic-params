# Test low coverage modules
import pytest
import importlib
class TestPublicAPIModule:
    """Test public api module imports"""
    def test_import_public_api_directly(self):
        """Test importing public.api module directly"""
        module = importlib.import_module("dynamic_params.public.api")
        # Access the imports to ensure they are executed
        assert module. is not None
        assert module.parametrize_fixture is not None
        assert module. is not None
        assert module.param_generator is not None
        assert module. is not None
        # Access __all__
        assert len(module.__all__) == 5
class TestVersionModule:
    """Test __version__ module"""
    def test_version_import(self):
        """Test importing __version__ module"""
        from dynamic_params import param_generator
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0
    def test_version_module_direct(self):
        """Test accessing __version__ module directly"""
        module = importlib.import_module("dynamic_params.__version__")
        assert hasattr(module, "__version__")
        assert isinstance(module.__version__, str)
class TestErrorsModule:
    """Test errors module coverage"""
    def test_import_all_errors(self):
        """Test importing all error classes"""
        from dynamic_params.errors import (
            DynamicParamsError,
            DependencyError,
            CircularDependencyError,
            GeneratorError,
            GeneratorNotFoundError,
            ParametrizeErrorError,
            ConfigError,
            ConfigurationError,
        )
        # Verify all classes are accessible
        assert DynamicParamsError is not None
        assert DependencyError is not None
        assert CircularDependencyError is not None
        assert GeneratorError is not None
        assert GeneratorNotFoundError is not None
        assert ParametrizeError is not None
        assertError is not None
        assert ConfigError is not None
        assert ConfigurationError is not None
    def test_error_inheritance(self):
        """Test error class inheritance hierarchy"""
        from dynamic_params.errors import (
            DynamicParamsError,
            DependencyError,
            CircularDependencyError,
            GeneratorError,
            GeneratorNotFoundError,
            ParametrizeErrorError,
            ConfigError,
            ConfigurationError,
        )
        # Check inheritance
        assert issubclass(DependencyError, DynamicParamsError)
        assert issubclass(CircularDependencyError, DependencyError)
        assert issubclass(GeneratorError, DynamicParamsError)
        assert issubclass(GeneratorNotFoundError, GeneratorError)
        assert issubclass(ParametrizeError, DynamicParamsError)
        assert issubclass(Error, DynamicParamsError)
        assert issubclass(ConfigError, DynamicParamsError)
        assert issubclass(ConfigurationError, ConfigError)
    def test_error_instantiation(self):
        """Test instantiating error classes"""
        from dynamic_params.errors import (
            DynamicParamsError,
            DependencyError,
            CircularDependencyError,
            GeneratorError,
            GeneratorNotFoundError,
            ParametrizeErrorError,
            ConfigError,
            ConfigurationError,
        )
        # Test each error can be instantiated
        err1 = DynamicParamsError("test message")
        assert str(err1) == "test message"
        err2 = DependencyError("dependency error")
        assert str(err2) == "dependency error"
        err3 = CircularDependencyError("circular dep")
        assert str(err3) == "circular dep"
        err4 = GeneratorError("generator error")
        assert str(err4) == "generator error"
        err5 = GeneratorNotFoundError("not found")
        assert str(err5) == "not found"
        err6 = ParametrizeError("param error")
        assert str(err6) == "param error"
        err7 =Error("dynref error")
        assert str(err7) == "dynref error"
        err8 = ConfigError("config error")
        assert str(err8) == "config error"
        err9 = ConfigurationError("config error alias")
        assert str(err9) == "config error alias"
