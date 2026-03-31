# Configuration management for pytest-dynamic-params

class Config:
    """Global configuration for the plugin"""
    
    def __init__(self):
        """Initialize configuration with default values"""
        self.default_cache = False
        self.default_lazy = False
        self.default_scope = "function"
        self.max_cache_size = 1000
    
    def update(self, **kwargs):
        """Update configuration with user-provided values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Global configuration instance
config = Config()
