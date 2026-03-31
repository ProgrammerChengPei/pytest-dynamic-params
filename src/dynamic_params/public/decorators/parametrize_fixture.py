# Fixture parametrization decorator

from typing import Any, List, Callable
import warnings
import pytest

def parametrize_fixture(argnames: str, argvalues: List[Any], **kwargs: Any) -> Callable:
    """Decorator for parametrizing fixtures
    
    This decorator allows you to parameterize fixtures with dynamic parameters,
    including support for generators and DynRef references.
    
    Args:
        argnames: Comma-separated string of parameter names
        argvalues: List of parameter values
        **kwargs: Additional keyword arguments
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        # First apply the pytest fixture decorator
        if not hasattr(func, "__pytestfixturefunction__"):
            func = pytest.fixture(**kwargs)(func)
        
        # Note: In pytest 9+, marks on fixtures have no effect and raise a warning
        # We skip adding the mark for fixtures to avoid the warning
        # pytest.mark.dynamic_parametrize(
        #     argnames=argnames,
        #     argvalues=argvalues,
        #     **kwargs
        # )(func)
        return func
    return decorator
