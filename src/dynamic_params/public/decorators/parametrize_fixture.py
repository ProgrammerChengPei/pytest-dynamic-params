# Fixture parametrization decorator

import inspect
import warnings
from typing import Any, Callable, List

import pytest

from ..argvalues import process_argvalues


def parametrize_fixture(argnames: str, argvalues: List[Any], **kwargs: Any) -> Callable:
    """Decorator for parametrizing fixtures

    This decorator creates a parametrized fixture with the name specified in argnames,
    and the decorated function receives this fixture as a parameter.

    Args:
        argnames: Comma-separated string of parameter names (these become fixture names)
        argvalues: List of parameter values, generator object, or callable that returns a list
        **kwargs: Additional keyword arguments

    Returns:
        Decorator function

    Example:
        @parametrize_fixture("value", [1, 2, 3])
        def my_fixture(value):
            return value * 2

        def test_example(my_fixture):
            assert my_fixture in [2, 4, 6]

        # Optional performance settings:
        @parametrize_fixture("value", get_values, cache=True, scope="session")
        def my_cached_fixture(value):
            return value

        @parametrize_fixture("value", get_values, lazy=True)
        def my_lazy_fixture(value):
            return value
    """

    def decorator(func: Callable) -> Callable:
        # Process argvalues - use shared processor; this also supports optional
        # cache/lazy when provided in kwargs (backwards compatible if not set)
        processed_argvalues = process_argvalues(argvalues, kwargs)

        # Warn when @pytest.fixture is combined with @parametrize_fixture,
        # because the two decorators have overlapping semantics and may be
        # ambiguous.
        is_fixture = (
            hasattr(func, "__pytestfixturefunction__")
            or hasattr(func, "_fixture_function_marker")
            or hasattr(func, "_pytestfixturefunction")
        )
        if is_fixture:
            warnings.warn(
                "Combining @pytest.fixture with @parametrize_fixture is not supported "
                "and may produce undefined behavior.",
                UserWarning,
            )

        # Store parametrization info on the function for processor to use
        if not hasattr(func, "_dynamic_fixture_parametrize"):
            func._dynamic_fixture_parametrize = []

        func._dynamic_fixture_parametrize.append({
            "argnames": argnames,
            "argvalues": processed_argvalues,
            **kwargs
        })

        # Parse argnames to get the fixture names
        fixture_names = [name.strip() for name in argnames.split(",")]

        # Create parametrized fixtures for each argname
        # Each fixture will be parametrized with the corresponding values
        for i, fixture_name in enumerate(fixture_names):
            # Create a simple fixture that yields the parametrized value
            # The fixture will be parametrized via pytest_generate_tests hook
            fixture_func = _create_parametrized_fixture(fixture_name, processed_argvalues, **kwargs)

            # Register the fixture in the module's global namespace
            # This makes it available to other fixtures and tests
            module = inspect.getmodule(func)
            if module and not hasattr(module, fixture_name):
                setattr(module, fixture_name, fixture_func)

        # Apply pytest.fixture decorator to the function if it is not already
        # a fixture. Filter cache/lazy keys before passing kwargs to pytest.
        fixture_kwargs = {
            k: v for k, v in kwargs.items() if k not in ("cache", "lazy")
        }
        if not is_fixture:
            func = pytest.fixture(**fixture_kwargs)(func)

        return func

    return decorator


def _create_parametrized_fixture(name: str, values: List[Any], **kwargs: Any):
    """Create a parametrized fixture

    Args:
        name: Fixture name
        values: List of parameter values
        **kwargs: Additional keyword arguments for pytest.fixture

    Returns:
        A pytest fixture function
    """
    # Create a fixture that receives request.param and returns it
    def parametrized_fixture(request):
        return request.param

    parametrized_fixture.__name__ = name

    # If values is a GeneratorBase-like instance, pass it directly to pytest.fixture
    # so pytest can iterate it lazily. Do not execute it eagerly here.
    try:
        from ...engine.generator.base import GeneratorBase
    except Exception:
        GeneratorBase = None

    if GeneratorBase is not None and isinstance(values, GeneratorBase):
        params = values
    else:
        params = values

    fixture_kwargs = {
        k: v for k, v in kwargs.items() if k not in ("cache", "lazy")
    }
    return pytest.fixture(params=params, name=name, **fixture_kwargs)(parametrized_fixture)


# processing delegated to public.argvalues.process_argvalues
