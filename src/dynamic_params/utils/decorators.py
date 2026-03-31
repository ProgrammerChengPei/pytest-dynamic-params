# Decorator utility functions

from typing import Callable, Any, Optional

def create_decorator(decorator_func: Callable) -> Callable:
    """Create a decorator that can be used with or without parentheses
    
    Args:
        decorator_func: The decorator function to wrap
        
    Returns:
        Decorator that can be used with or without parentheses
    """
    def decorator(*args: Any, **kwargs: Any) -> Callable:
        # If the first argument is a callable and no other arguments are provided,
        # the decorator is being used without parentheses
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return decorator_func(args[0])
        # Otherwise, the decorator is being used with parentheses
        def wrapper(func: Callable) -> Callable:
            return decorator_func(func, *args, **kwargs)
        return wrapper
    return decorator
