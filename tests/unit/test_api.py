# Test public API functionality

from dynamic_params.public.api import param_generator, parametrize_fixture


class TestPublicAPI:
    """Test public API exports"""
    
    def test_parametrize_fixture_exists(self):
        """Test that parametrize_fixture is exported"""
        assert parametrize_fixture is not None
        assert callable(parametrize_fixture)
    

    def test_param_generator_exists(self):
        """Test that param_generator is exported"""
        assert param_generator is not None
        assert callable(param_generator)
    