# Test function parametrization decorator

from typing import Any, List, Callable

def parametrize_test(argnames: str, argvalues: Any, **kwargs: Any) -> Callable:
    """Decorator for parametrizing test functions
    
    This decorator allows you to parameterize test functions with dynamic parameters,
    including support for generators and DynRef references.
    
    Args:
        argnames: Comma-separated string of parameter names
        argvalues: List of parameter values or generator reference
        **kwargs: Additional keyword arguments
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # Add our custom attribute to the function
        if not hasattr(func, "_dynamic_parametrize"):
            func._dynamic_parametrize = []
        
        # Add parametrization configuration
        func._dynamic_parametrize.append({
            "argnames": argnames,
            "argvalues": argvalues,
            **kwargs
        })
        
        return func
    return decorator
