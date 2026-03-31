# Generator parametrization decorator

from typing import Any, List, Callable

import pytest

def parametrize_generator(argnames: str, argvalues: List[Any], **kwargs: Any) -> Callable:
    """Decorator for parametrizing generators
    
    This decorator allows you to parameterize generator functions with dynamic parameters,
    including support for other generators and DynRef references.
    
    Args:
        argnames: Comma-separated string of parameter names
        argvalues: List of parameter values
        **kwargs: Additional keyword arguments
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Add our custom marker to the function
        pytest.mark.dynamic_parametrize(
            argnames=argnames,
            argvalues=argvalues,
            **kwargs
        )(func)
        return func
    return decorator
