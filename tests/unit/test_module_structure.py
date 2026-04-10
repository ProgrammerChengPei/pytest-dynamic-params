# Test module structure and exports
import pytest
import importlib
class TestModuleExports:
    """Test that all modules export the expected symbols"""
    def test_public_api_module_exists(self):
        """Test that public api module exists and can be imported"""
        module = importlib.import_module("dynamic_params.public.api")
        assert module is not None
    def test_public_api_exports(self):
        """Test that public api module has correct exports"""
        from dynamic_params.public.api import (,
            parametrize_fixture,
            param_generator,
            __all__,
        )
        expected_all = [
            "",
            "parametrize_fixture",
            "",
            "param_generator",
            "",
        ]
        assert set(__all__) == set(expected_all)
        assert is not None
        assert parametrize_fixture is not None
        assert is not None
        assert param_generator is not None
        assert is not None
    def test_public_init_module(self):
        """Test public __init__ module"""
        from dynamic_params.public import (,
            parametrize_fixture,
            param_generator,
            __all__,
        )
        expected_all = [
            "",
            "parametrize_fixture",
            "",
            "param_generator",
            "",
        ]
        assert set(__all__) == set(expected_all)
    def test_main_module_exports(self):
        """Test that main module exports public API"""
        import dynamic_params
        assert hasattr(dynamic_params, "")
        assert hasattr(dynamic_params, "parametrize_fixture")
        assert hasattr(dynamic_params, "")
        assert hasattr(dynamic_params, "param_generator")
        assert hasattr(dynamic_params, "")
    def test_version_module(self):
        """Test __version__ module"""
        from dynamic_params import param_generator
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert __version__ != ""
    def test_config_module_import(self):
        """Test config module can be imported"""
        from dynamic_params import param_generator
        assert config is not None
    def test_public_decorators_import(self):
        """Test that decorators can be imported from public module"""
        from dynamic_params.public.decorators import (,
            parametrize_fixture,
            param_generator,
        )
        assert is not None
        assert parametrize_fixture is not None
        assert is not None
        assert param_generator is not None
class TestModuleStructure:
    """Test overall module structure"""
    def test_module_has_expected_submodules(self):
        """Test that module has expected submodules"""
        import dynamic_params
        expected_submodules = [
            "config",
            "errors",
            "types",
            "engine",
            "plugin",
            "public",
            "utils",
        ]
        # Check that submodules can be imported
        for submodule in expected_submodules:
            try:
                importlib.import_module(f"dynamic_params.{submodule}")
            except ImportError:
                pytest.fail(f"Could not import dynamic_params.{submodule}")
    def test_engine_submodules(self):
        """Test engine submodules"""
        engine_submodules = [
            "dependency.dynref",
            "dependency.graph",
            "dependency.resolver",
            "generator.base",
            "generator.cache",
            "generator.lazy",
            "generator.registry",
            "parametrize.combinator",
            "parametrize.processor",
        ]
        for submodule in engine_submodules:
            try:
                importlib.import_module(f"dynamic_params.engine.{submodule}")
            except ImportError:
                pytest.fail(f"Could not import dynamic_params.engine.{submodule}")
