# Test config module

import pytest
from dynamic_params.config import Config, config


class TestConfig:
    """Test Config class"""
    
    def test_config_init(self):
        """Test Config initialization with defaults"""
        cfg = Config()
        assert cfg.default_cache is False
        assert cfg.default_lazy is False
        assert cfg.default_scope == "function"
        assert cfg.max_cache_size == 1000
    
    def test_config_update_existing_keys(self):
        """Test Config.update with existing keys"""
        cfg = Config()
        cfg.update(default_cache=True, default_lazy=True, default_scope="session")
        assert cfg.default_cache is True
        assert cfg.default_lazy is True
        assert cfg.default_scope == "session"
    
    def test_config_update_max_cache_size(self):
        """Test Config.update with max_cache_size"""
        cfg = Config()
        cfg.update(max_cache_size=2000)
        assert cfg.max_cache_size == 2000
    
    def test_config_update_nonexistent_key(self):
        """Test Config.update with non-existent key should not raise error"""
        cfg = Config()
        original_value = cfg.default_cache
        cfg.update(nonexistent_key="value")
        # Should not change existing values
        assert cfg.default_cache == original_value
    
    def test_config_update_multiple_updates(self):
        """Test Config.update with multiple consecutive updates"""
        cfg = Config()
        
        cfg.update(default_cache=True)
        assert cfg.default_cache is True
        
        cfg.update(default_lazy=True, default_scope="module")
        assert cfg.default_lazy is True
        assert cfg.default_scope == "module"
        
        cfg.update(max_cache_size=5000)
        assert cfg.max_cache_size == 5000
    
    def test_config_update_with_false_values(self):
        """Test Config.update with false values"""
        cfg = Config()
        cfg.default_cache = True
        cfg.default_lazy = True
        cfg.max_cache_size = 2000
        
        cfg.update(default_cache=False, default_lazy=False, max_cache_size=0)
        assert cfg.default_cache is False
        assert cfg.default_lazy is False
        assert cfg.max_cache_size == 0
    
    def test_config_update_with_none(self):
        """Test Config.update with None values"""
        cfg = Config()
        cfg.update(default_cache=None)
        assert cfg.default_cache is None


class TestGlobalConfig:
    """Test global config instance"""
    
    def test_global_config_is_singleton(self):
        """Test that global config is a singleton-like instance"""
        from dynamic_params.config import config as config1
        
        config1.default_cache = True
        
        from dynamic_params.config import config as config2
        assert config2.default_cache is True
        
        # Reset
        config1.default_cache = False
    
    def test_global_config_defaults(self):
        """Test global config default values"""
        assert config.default_cache is False
        assert config.default_lazy is False
        assert config.default_scope == "function"
        assert config.max_cache_size == 1000
    
    def test_global_config_update(self):
        """Test updating global config"""
        config.update(default_cache=True, max_cache_size=5000)
        assert config.default_cache is True
        assert config.max_cache_size == 5000
        
        # Reset
        config.update(default_cache=False, max_cache_size=1000)
