# Parameter generator decorator

from typing import Any, Callable, Optional

from ...engine.generator.base import GeneratorBase
from ...engine.generator.lazy import LazyGenerator
from ...engine.generator.registry import registry as generator_registry
from ...config import config as plugin_config

def param_generator(func: Optional[Callable] = None, *, 
                   scope: str = "function", 
                   cache: bool = False, 
                   lazy: bool = False) -> Callable:
    """Decorator for defining parameter generators
    
    This decorator allows you to define generator functions that can be used
    to dynamically generate test parameters.
    
    Args:
        func: The generator function
        scope: The scope of the generator (function, class, module, session)
        cache: Whether to cache the generator results
        lazy: Whether to lazy load the generator
        
    Returns:
        Decorator function or decorated function
    """
    def decorator(func: Callable) -> Callable:
        # Determine which generator class to use
        generator_class = LazyGenerator if lazy else GeneratorBase
        
        # Create generator instance
        if lazy:
            generator = generator_class(
                func,
                scope=scope,
                cache=cache
            )
        else:
            generator = generator_class(
                func,
                scope=scope,
                cache=cache
            )
        
        # Register the generator
        generator_registry.register(func.__name__, generator)
        
        # Return the generator instance
        return generator
    
    # Handle case where decorator is used without parentheses
    if func is None:
        return decorator
    return decorator(func)
