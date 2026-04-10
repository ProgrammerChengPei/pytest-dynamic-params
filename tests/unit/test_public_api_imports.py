# Test public API imports and module structure
import pytest
import importlib
class TestPublicAPIImports:
    """Test imports from the main public API"""
    def test_main_module_imports(self):
        """Test importing the main public API module"""
        from dynamic_params.public import api
        # Check that expected exports are available
        assert hasattr(api, '')
        assert hasattr(api, 'parametrize_fixture')
        assert hasattr(api, '')
        assert hasattr(api, 'param_generator')
        assert hasattr(api, '')
    def test_direct_api_imports(self):
        """Test direct imports from public API"""
        from dynamic_params.public.api import (,
            parametrize_fixture,
            param_generator
        )
        # All imports should succeed
        assert is not None
        assert parametrize_fixture is not None
        assert is not None
        assert param_generator is not None
        assert is not None
    def test_public_api_all_attribute(self):
        """Test __all__ attribute in public API"""
        from dynamic_params.public import api
        assert hasattr(api, '__all__')
        assert len(api.__all__) == 5
        assert '' in api.__all__
        assert 'parametrize_fixture' in api.__all__
        assert '' in api.__all__
        assert 'param_generator' in api.__all__
        assert '' in api.__all__
    def test_star_import_completeness(self):
        """Test that star import brings in all expected symbols"""
        from dynamic_params.public.api import *
        # Check that all expected names are available
        expected_symbols = [
            '',
            'parametrize_fixture', 
            '',
            'param_generator',
            ''
        ]
        for symbol in expected_symbols:
            assert symbol in locals()
            assert locals()[symbol] is not None
class TestPublicDecoratorImports:
    """Test imports from public decorator modules"""
    def test__import(self):
        """Test importing decorator"""
        from dynamic_params.public.decorators. import
        assert callable()
    def test_parametrize_fixture_import(self):
        """Test importing parametrize_fixture decorator"""
        from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture
        assert callable(parametrize_fixture)
    def test__import(self):
        """Test importing decorator"""
        from dynamic_params.public.decorators. import
        assert callable()
    def test_param_generator_import(self):
        """Test importing param_generator decorator"""
        from dynamic_params.public.decorators.param_generator import param_generator
        assert callable(param_generator)
    def test_dynref_import_path(self):
        """Test importing from correct module"""
        from dynamic_params.public.ref.dynref import
        assert is not None
class TestModuleStructure:
    """Test overall module structure and organization"""
    def test_public_module_organization(self):
        """Test that public module has correct structure"""
        # Check that all expected submodules exist
        modules_to_check = [
            'dynamic_params.public',
            'dynamic_params.public.api',
            'dynamic_params.public.decorators',
            'dynamic_params.public.decorators.',
            'dynamic_params.public.decorators.parametrize_fixture',
            'dynamic_params.public.decorators.',
            'dynamic_params.public.decorators.param_generator',
            'dynamic_params.public.ref',
            'dynamic_params.public.ref.dynref'
        ]
        for module_path in modules_to_check:
            try:
                module = importlib.import_module(module_path)
                assert module is not None
            except ImportError:
                pytest.fail(f"Module {module_path} should be importable")
    def test_engine_module_structure(self):
        """Test engine module structure"""
        # Check core engine modules exist
        engine_modules = [
            'dynamic_params.engine',
            'dynamic_params.engine.generator',
            'dynamic_params.engine.generator.registry',
            'dynamic_params.engine.generator.cache',
            'dynamic_params.engine.errors',
            'dynamic_params.engine.dependency'
        ]
        for module_path in engine_modules:
            try:
                module = importlib.import_module(module_path)
                assert module is not None
            except ImportError:
                pytest.fail(f"Engine module {module_path} should be importable")
    def test_error_module_imports(self):
        """Test importing error classes"""
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
        # All error classes should be importable
        error_classes = [
            DynamicParamsError,
            DependencyError,
            CircularDependencyError,
            GeneratorError,
            GeneratorNotFoundError,
            ParametrizeErrorError,
            ConfigError,
            ConfigurationError
        ]
        for error_class in error_classes:
            assert error_class is not None
class TestTypeAnnotations:
    """Test type annotations and function signatures"""
    def test_decorator_signatures(self):
        """Test that decorators have proper signatures"""
        from dynamic_params.public.decorators. import
        from dynamic_params.public.decorators.parametrize_fixture import parametrize_fixture
        from dynamic_params.public.decorators. import
        from dynamic_params.public.decorators.param_generator import param_generator
        # All decorators should be callable
        assert callable()
        assert callable(parametrize_fixture)
        assert callable()
        assert callable(param_generator)
    def test_dynref_type_annotations(self):
        """Test type annotations"""
        from dynamic_params.public.ref.dynref import
        # should have proper constructor
        ref =("test_generator")
        assert isinstance(ref)
        assert hasattr(ref, 'generator_name')
        assert ref.generator_name == "test_generator"
class TestVersionManagement:
    """Test version management and module metadata"""
    def test_version_import(self):
        """Test that version information is available"""
        from dynamic_params import param_generator
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        # Version should follow semantic versioning pattern
        version_parts = __version__.split('.')
        assert len(version_parts) >= 2  # At least major.minor
        assert all(part.isdigit() or '+' in part or '-' in part for part in version_parts[:2])
    def test_module_metadata(self):
        """Test module-level metadata"""
        import dynamic_params
        assert hasattr(dynamic_params, '__version__')
        assert hasattr(dynamic_params, '__author__') or hasattr(dynamic_params, '__authors__')
        assert hasattr(dynamic_params, '__description__') or hasattr(dynamic_params, 'description')
    def test_public_api_stability(self):
        """Test that public API remains stable"""
        # Import all public symbols to ensure no breaking changes
        from dynamic_params.public.api import *
        # These should always be available in public API
        required_symbols = [
            '',
            'parametrize_fixture',
            '', 
            'param_generator',
            ''
        ]
        for symbol in required_symbols:
            assert symbol in globals()
            assert callable(globals().get(symbol)) or globals().get(symbol) is not None