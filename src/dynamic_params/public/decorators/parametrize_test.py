# Test function parametrization decorator

from typing import Any, Callable

from ..argvalues import process_argvalues


def parametrize_test(argnames: str, argvalues: Any, **kwargs: Any) -> Callable:
    """Decorator for parametrizing test functions

    This decorator allows you to parameterize test functions with dynamic parameters,
    including support for generators, functions, and DynRef references.

    Args:
        argnames: Comma-separated string of parameter names
        argvalues: List of parameter values, generator reference, or callable function
        **kwargs: Additional keyword arguments:
            - cache: Whether to cache the generator results (default: False)
            - lazy: Whether to lazy load the generator (default: False)
            - scope: The scope of caching (function, class, module, session)

    Returns:
        Decorator function

    Examples:
        # Basic usage with list
        @parametrize_test("value", [1, 2, 3])
        def test_basic(value):
            assert value > 0

        # With function (auto-wrapped as GeneratorBase)
        @parametrize_test("value", get_data, cache=True, scope="session")
        def test_with_cache(value):
            assert value is not None

        # With lazy loading
        @parametrize_test("value", get_expensive_data, lazy=True)
        def test_lazy(value):
            assert value > 0
    """
    def decorator(func: Callable) -> Callable:
        # Add our custom attribute to the function
        if not hasattr(func, "_dynamic_parametrize"):
            func._dynamic_parametrize = []

        # Process argvalues - use shared processor
        processed_argvalues = process_argvalues(argvalues, kwargs)

        config = {
            "argnames": argnames,
            "argvalues": processed_argvalues,
        }
        # Store original kwargs for reference (excluding cache/lazy/scope which are consumed)
        config.update({k: v for k, v in kwargs.items() if k not in ("cache", "lazy", "scope")})

        func._dynamic_parametrize.append(config)

        return func
    return decorator


# processing delegated to public.argvalues.process_argvalues
