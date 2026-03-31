# Generator cache implementation

from typing import Dict, Any, Optional

from ...types import CacheType

class GeneratorCache:
    """Cache for generator results"""
    
    def __init__(self):
        """Initialize a generator cache"""
        self._cache: CacheType = {
            "function": {},
            "class": {},
            "module": {},
            "session": {}
        }
    
    def get(self, scope: str, key: str) -> Optional[Any]:
        """Get a value from the cache
        
        Args:
            scope: The cache scope (function, class, module, session)
            key: The cache key
            
        Returns:
            The cached value or None if not found
        """
        if scope not in self._cache:
            return None
        return self._cache[scope].get(key)
    
    def set(self, scope: str, key: str, value: Any) -> None:
        """Set a value in the cache
        
        Args:
            scope: The cache scope (function, class, module, session)
            key: The cache key
            value: The value to cache
        """
        if scope not in self._cache:
            self._cache[scope] = {}
        self._cache[scope][key] = value
    
    def clear(self, scope: Optional[str] = None) -> None:
        """Clear the cache
        
        Args:
            scope: The scope to clear. If None, clear all scopes.
        """
        if scope:
            if scope in self._cache:
                self._cache[scope].clear()
        else:
            for scope_cache in self._cache.values():
                scope_cache.clear()
    
    def get_cache_size(self, scope: Optional[str] = None) -> int:
        """Get the size of the cache
        
        Args:
            scope: The scope to check. If None, check all scopes.
            
        Returns:
            The number of items in the cache
        """
        if scope:
            if scope in self._cache:
                return len(self._cache[scope])
            return 0
        else:
            return sum(len(scope_cache) for scope_cache in self._cache.values())
