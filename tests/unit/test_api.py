# Test public API functionality

from dynamic_params.public.api import (
    parametrize_test,
    parametrize_fixture,
    parametrize_generator,
    param_generator,
    DynRef,
)


class TestPublicAPI:
    """Test public API exports"""
    
    def test_parametrize_test_exists(self):
        """Test that parametrize_test is exported"""
        assert parametrize_test is not None
        assert callable(parametrize_test)
    
    def test_parametrize_fixture_exists(self):
        """Test that parametrize_fixture is exported"""
        assert parametrize_fixture is not None
        assert callable(parametrize_fixture)
    
    def test_parametrize_generator_exists(self):
        """Test that parametrize_generator is exported"""
        assert parametrize_generator is not None
        assert callable(parametrize_generator)
    
    def test_param_generator_exists(self):
        """Test that param_generator is exported"""
        assert param_generator is not None
        assert callable(param_generator)
    
    def test_dynref_exists(self):
        """Test that DynRef is exported"""
        assert DynRef is not None
        assert callable(DynRef)
    
    def test_dynref_creation(self):
        """Test creating DynRef instance"""
        ref = DynRef("test_param")
        assert ref.name == "test_param"
