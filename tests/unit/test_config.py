# Test config functionality

import pytest
from dynamic_params.config import Config, config

class TestConfig:
    """Test Config class"""
    
    def test_config_init(self):
        """Test Config initialization"""
        config_instance = Config()
        assert config_instance.default_cache is False
        assert config_instance.default_lazy is False
        assert config_instance.default_scope == "function"
        assert config_instance.max_cache_size == 1000
    
    def test_config_update(self):
        """Test Config update"""
        config_instance = Config()
        config_instance.update(default_cache=True, default_lazy=True)
        assert config_instance.default_cache is True
        assert config_instance.default_lazy is True
    
    def test_config_update_invalid_key(self):
        """Test Config update with invalid key"""
        config_instance = Config()
        config_instance.update(invalid_key=True)
        assert not hasattr(config_instance, 'invalid_key')
    
    def test_global_config_instance(self):
        """Test global config instance"""
        assert isinstance(config, Config)
