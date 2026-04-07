import inspect
from typing import Any, Dict, Optional


def _is_pytest_fixture(obj: Any) -> bool:
    return (
        hasattr(obj, "__pytestfixturefunction__")
        or hasattr(obj, "_fixture_function_marker")
        or hasattr(obj, "_pytestfixturefunction")
    )


def process_argvalues(argvalues: Any, options: Optional[Dict[str, Any]] = None) -> Any:
    """Unified argvalues processing used by decorators.

    Behavior:
    - generator objects/functions -> evaluated to list (unless wrapped as GeneratorBase)
    - callable fixtures -> returned as-is (pytest fixtures)
    - callable normal functions -> if `cache`/`lazy` in options -> wrapped into
      GeneratorBase/LazyGenerator; otherwise called and result returned (convert
      generator results to list)

    options: dict that may contain `cache`, `lazy`, `scope` keys.
    """
    opts = options or {}
    cache = opts.get("cache", False)
    lazy = opts.get("lazy", False)
    scope = opts.get("scope", "function")

    # generator object
    if inspect.isgenerator(argvalues):
        return list(argvalues)

    # callable factory or fixture
    if callable(argvalues) and not isinstance(argvalues, (list, tuple, type)):
        # detect pytest fixture
        if _is_pytest_fixture(argvalues):
            return argvalues

        # if already a GeneratorBase instance, return as-is
        try:
            from ..engine.generator.base import GeneratorBase
        except Exception:
            GeneratorBase = None

        if GeneratorBase is not None and isinstance(argvalues, GeneratorBase):
            return argvalues

        # respect cache/lazy options: wrap as GeneratorBase/LazyGenerator
        if cache or lazy:
            if lazy:
                from ..engine.generator.lazy import LazyGenerator

                return LazyGenerator(argvalues, scope=scope, cache=cache)
            else:
                # fallback to base generator
                from ..engine.generator.base import GeneratorBase as GB

                return GB(argvalues, scope=scope, cache=cache)

        # generator function (call to get generator)
        if inspect.isgeneratorfunction(argvalues):
            return list(argvalues())

        # otherwise call the factory to obtain values
        result = argvalues()
        if inspect.isgenerator(result):
            return list(result)
        return result

    return argvalues


def is_pytest_fixture(obj: Any) -> bool:
    return _is_pytest_fixture(obj)
