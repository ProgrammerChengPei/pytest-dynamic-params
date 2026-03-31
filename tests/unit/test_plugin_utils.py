# Test plugin utils functionality

import pytest
from dynamic_params.plugin.utils import get_plugin_config, is_xdist_enabled


class MockConfig:
    """Mock Config class for testing"""
    
    def __init__(self, config_dict=None):
        self.config_dict = config_dict or {}
    
    def getini(self, key):
        return self.config_dict.get(key)


class TestGetPluginConfig:
    """Test get_plugin_config function"""
    
    def test_get_plugin_config_default(self):
        """Test get_plugin_config with default values"""
        config = MockConfig()
        result = get_plugin_config(config)
        
        assert result["default_cache"] is False
        assert result["default_lazy"] is False
        assert result["default_scope"] == "function"
    
    def test_get_plugin_config_with_values(self):
        """Test get_plugin_config with custom values"""
        config = MockConfig({
            "dynamic_params_default_cache": "true",
            "dynamic_params_default_lazy": "true",
            "dynamic_params_default_scope": "session"
        })
        result = get_plugin_config(config)
        
        assert result["default_cache"] is True
        assert result["default_lazy"] is True
        assert result["default_scope"] == "session"
    
    def test_get_plugin_config_partial_values(self):
        """Test get_plugin_config with partial values"""
        config = MockConfig({
            "dynamic_params_default_cache": "true"
        })
        result = get_plugin_config(config)
        
        assert result["default_cache"] is True
        assert result["default_lazy"] is False
        assert result["default_scope"] == "function"


class TestIsXdistEnabled:
    """Test is_xdist_enabled function"""
    
    def test_is_xdist_enabled_false(self):
        """Test is_xdist_enabled with no xdist"""
        config = MockConfig()
        result = is_xdist_enabled(config)
        
        assert result is False
    
    def test_is_xdist_enabled_true(self):
        """Test is_xdist_enabled with xdist"""
        config = MockConfig()
        config.workerinput = {}
        result = is_xdist_enabled(config)
        
        assert result is True
