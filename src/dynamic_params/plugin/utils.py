# Plugin utility functions

from typing import Any, Dict

from pytest import Config

def get_plugin_config(config: Config) -> Dict[str, Any]:
    """Get plugin configuration from pytest config
    
    Args:
        config: pytest's Config object
        
    Returns:
        Dictionary of plugin configuration
    """
    plugin_config = {
        "default_cache": False,
        "default_lazy": False,
        "default_scope": "function"
    }
    
    # Load configuration from pytest.ini
    if hasattr(config, 'getini'):
        default_cache = config.getini("dynamic_params_default_cache")
        if default_cache:
            plugin_config["default_cache"] = default_cache.lower() == "true"
        
        default_lazy = config.getini("dynamic_params_default_lazy")
        if default_lazy:
            plugin_config["default_lazy"] = default_lazy.lower() == "true"
        
        default_scope = config.getini("dynamic_params_default_scope")
        if default_scope:
            plugin_config["default_scope"] = default_scope
    
    return plugin_config

def is_xdist_enabled(config: Config) -> bool:
    """Check if pytest-xdist is enabled
    
    Args:
        config: pytest's Config object
        
    Returns:
        True if xdist is enabled, False otherwise
    """
    return hasattr(config, 'workerinput')
