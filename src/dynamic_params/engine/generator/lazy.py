# Lazy generator implementation

from typing import Any, List

from .base import GeneratorBase

class LazyGenerator(GeneratorBase):
    """Lazy-loading generator"""
    
    def __init__(self, func, scope="function", cache=False):
        """Initialize a lazy generator
        
        Args:
            func: The generator function
            scope: The scope of the generator (function, class, module, session)
            cache: Whether to cache the generator results
        """
        super().__init__(func, scope=scope, cache=cache, lazy=True)
        self._cached_result = None
        self._executed = False
    
    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """Execute the generator function lazily
        
        Args:
            *args: Positional arguments for the generator function
            **kwargs: Keyword arguments for the generator function
            
        Returns:
            List of generated parameter values
        """
        # If already executed, return cached result
        if self._executed:
            return self._cached_result
        
        # Execute the generator function
        result = super().execute(*args, **kwargs)
        
        # Cache the result for future calls
        self._cached_result = result
        self._executed = True
        
        return result
    
    def reset(self):
        """Reset the lazy generator to its initial state"""
        self._cached_result = None
        self._executed = False
