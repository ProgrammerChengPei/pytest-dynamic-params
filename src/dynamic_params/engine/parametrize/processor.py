# Parametrization processor implementation

from typing import Any, Dict, List

from pytest import Metafunc

from ...errors import ParametrizeError
from ..dependency.dynref import DynRef, DynRefExpression
from ..dependency.resolver import DependencyResolver
from .combinator import ParametrizeCombinator


class ParametrizeProcessor:
    """Class for processing parameterization"""

    def __init__(self):
        """Initialize a parametrize processor"""
        self.resolver = DependencyResolver()
        self.combinator = ParametrizeCombinator()

    def _is_fixture(self, value: Any) -> bool:
        """Check if a value is a pytest fixture function"""
        return (
            hasattr(value, "__pytestfixturefunction__")
            or hasattr(value, "_fixture_function_marker")
            or hasattr(value, "_pytestfixturefunction")
        )

    def process(self, metafunc: Metafunc) -> None:
        """Process parameterization for a test function

        Args:
            metafunc: pytest's Metafunc object
        """
        # Get parametrization configuration from metafunc
        parametrizations = self._get_parametrizations(metafunc)

        if not parametrizations:
            return

        # Handle fixture-based parametrizations: inject via fixturenames
        remaining = []
        for parametrization in parametrizations:
            argvalues = parametrization.get("argvalues")
            argnames_str = parametrization.get("argnames", "")
            argnames = [n.strip() for n in argnames_str.split(",")]

            if callable(argvalues) and self._is_fixture(argvalues):
                # Try to get the fixture's params or call it directly if no request needed
                import inspect

                sig = inspect.signature(
                    argvalues.__wrapped__
                    if hasattr(argvalues, "__wrapped__")
                    else argvalues
                )
                params = list(sig.parameters.keys())
                fixture_name = getattr(argvalues, "__name__", None)

                # Get the underlying function
                underlying = getattr(argvalues, "__wrapped__", None) or argvalues

                # Check if fixture was created by parametrize_fixture decorator
                # Check both the fixture function itself and the underlying function
                fixture_parametrize_config = getattr(
                    argvalues, "_dynamic_fixture_parametrize", None
                ) or getattr(underlying, "_dynamic_fixture_parametrize", None)

                # Check if fixture has params= defined (parametrized fixture)
                fixture_marker = (
                    getattr(argvalues, "__pytestfixturefunction__", None)
                    or getattr(argvalues, "_fixture_function_marker", None)
                    or getattr(argvalues, "_pytestfixturefunction", None)
                )
                fixture_params = getattr(fixture_marker, "params", None)

                if fixture_parametrize_config is not None or fixture_params is not None:
                    # Fixture was created by parametrize_fixture or has params=
                    # If the requested argname matches the fixture name, inject it.
                    # Otherwise use the fixture as a source of values.
                    should_inject_fixture = fixture_name in argnames
                    if should_inject_fixture:
                        if fixture_name and fixture_name not in metafunc.fixturenames:
                            metafunc.fixturenames.append(fixture_name)
                    else:
                        if fixture_params is not None:
                            remaining.append(
                                {
                                    "argnames": argnames_str,
                                    "argvalues": list(fixture_params),
                                }
                            )
                        else:
                            try:
                                result = underlying()
                                if not isinstance(result, list):
                                    result = [result]
                                remaining.append(
                                    {
                                        "argnames": argnames_str,
                                        "argvalues": result,
                                    }
                                )
                            except Exception:
                                if fixture_name and fixture_name not in metafunc.fixturenames:
                                    metafunc.fixturenames.append(fixture_name)
                elif not params or params == ["request"]:
                    # Fixture takes no args - call directly to get values
                    if not params:
                        try:
                            result = underlying()
                            if not isinstance(result, list):
                                result = [result]
                            remaining.append(
                                {
                                    "argnames": argnames_str,
                                    "argvalues": result,
                                }
                            )
                        except Exception:
                            if (
                                fixture_name
                                and fixture_name not in metafunc.fixturenames
                            ):
                                metafunc.fixturenames.append(fixture_name)
                    else:
                        # Only takes request - needs pytest injection
                        if fixture_name and fixture_name not in metafunc.fixturenames:
                            metafunc.fixturenames.append(fixture_name)
                else:
                    # Has other params, try calling directly
                    try:
                        result = underlying()
                        if not isinstance(result, list):
                            result = [result]
                        remaining.append(
                            {
                                "argnames": argnames_str,
                                "argvalues": result,
                            }
                        )
                    except Exception:
                        if fixture_name and fixture_name not in metafunc.fixturenames:
                            metafunc.fixturenames.append(fixture_name)
            else:
                remaining.append(parametrization)

        if not remaining:
            return

        # Generate parameter combinations for non-fixture parametrizations
        try:
            param_combinations = self.generate_param_combinations(remaining, metafunc)
        except Exception as e:
            raise ParametrizeError(
                f"Failed to generate parameter combinations: {str(e)}"
            )

        # Apply parameterization to metafunc
        if len(remaining) == 1:
            # Single parametrization - apply directly
            self._apply_parametrization(metafunc, param_combinations, remaining)
        else:
            # Multiple stacked @parametrize_test - apply each independently
            # so pytest generates the cartesian product via its own mechanism
            for parametrization in remaining:
                single_combinations = self.generate_param_combinations(
                    [parametrization], metafunc
                )
                self._apply_parametrization(
                    metafunc, single_combinations, [parametrization]
                )

    def _get_parametrizations(self, metafunc: Metafunc) -> List[Dict[str, Any]]:
        """Get parametrization configurations from metafunc

        Args:
            metafunc: pytest's Metafunc object

        Returns:
            List of parametrization configurations
        """
        # Check if the function has our custom parametrization attribute
        parametrizations = []

        # Get the function object
        func = metafunc.function

        # Check if the function has our custom attribute
        if hasattr(func, "_dynamic_parametrize"):
            try:
                parametrizations.extend(func._dynamic_parametrize)
            except (TypeError, AttributeError):
                # Handle mock objects or non-iterable attributes
                pass
        else:
            # Fallback to getting markers from the function definition
            # This is for backward compatibility with tests
            try:
                if hasattr(metafunc, "definition") and hasattr(
                    metafunc.definition, "iter_markers"
                ):
                    markers = metafunc.definition.iter_markers()
                    # Check if markers is iterable and try to iterate
                    try:
                        for marker in markers:
                            if (
                                hasattr(marker, "name")
                                and marker.name == "dynamic_parametrize"
                            ):
                                if hasattr(marker, "kwargs"):
                                    parametrizations.append(marker.kwargs)
                    except TypeError:
                        # Handle mock objects or non-iterable markers
                        pass
            except (TypeError, AttributeError):
                # If any error occurs, just return an empty list
                pass

        return parametrizations

    def resolve_parameters(
        self, parametrization: Dict[str, Any], context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Resolve parameters for a parametrization

        Args:
            parametrization: Parametrization configuration
            context: Context for resolving dependencies

        Returns:
            Resolved parameters
        """
        if context is None:
            context = {}

        # Extract parameters from parametrization
        argnames = parametrization.get("argnames", "").split(",")
        argvalues = parametrization.get("argvalues", [])

        # Resolve each parameter value
        resolved_params = {}
        for i, argname in enumerate(argnames):
            argname = argname.strip()
            if i < len(argvalues):
                value = argvalues[i]
                # Resolve the value
                resolved_value = self._resolve_value(value, context)
                resolved_params[argname] = resolved_value

        # Resolve dependencies
        resolved = self.resolver.resolve(resolved_params, context)
        return resolved

    def generate_param_combinations(
        self, parametrizations: List[Dict[str, Any]], metafunc=None
    ) -> List[List[Any]]:
        """Generate parameter combinations from multiple parametrizations

        Args:
            parametrizations: List of parametrization configurations
            metafunc: pytest's Metafunc object (optional)

        Returns:
            List of parameter combinations
        """
        # Process each parametrization
        processed_parametrizations = []
        for parametrization in parametrizations:
            # Extract argnames
            argnames = parametrization.get("argnames", "").split(",")
            argnames = [name.strip() for name in argnames]

            # Get argvalues
            argvalues = parametrization.get("argvalues", [])

            # Resolve each argvalue
            resolved_argvalues = []
            if isinstance(argvalues, list):
                # If argvalues is a list, process each item
                for argvalue in argvalues:
                    if isinstance(argvalue, (list, tuple)):
                        # list or tuple = one row of multiple parameter values
                        resolved_argvalue = [
                            self._resolve_value(item, {}, metafunc) for item in argvalue
                        ]
                        resolved_argvalues.append(resolved_argvalue)
                    else:
                        # scalar value = one test case for a single parameter
                        resolved_value = self._resolve_value(argvalue, {}, metafunc)
                        resolved_argvalues.append([resolved_value])
            else:
                # If argvalues is not a list, resolve it and use it directly
                # This supports direct function/generator references
                # Check if argvalues is a fixture function
                if self._is_fixture(argvalues):
                    # Fixture function - let pytest inject it
                    fixture_name = getattr(argvalues, "__name__", None)
                    if fixture_name and fixture_name not in metafunc.fixturenames:
                        metafunc.fixturenames.append(fixture_name)
                    # Use fixture name as parameter value (pytest will replace it)
                    # For now, use a placeholder - pytest will inject the actual fixture value
                    resolved_argvalues.append([argvalues])
                else:
                    resolved_value = self._resolve_value(argvalues, {}, metafunc)
                    # If resolved_value is a list (e.g., from a generator), expand it into separate test cases
                    if isinstance(resolved_value, list):
                        # Each item in the list becomes a separate test case
                        # For single parameter, use the item directly
                        # For multiple parameters, wrap in tuple
                        for item in resolved_value:
                            if len(argnames) == 1:
                                # Single parameter, use item directly
                                resolved_argvalues.append(item)
                            else:
                                # Multiple parameters, wrap in list/tuple
                                resolved_argvalues.append(
                                    item if isinstance(item, (list, tuple)) else [item]
                                )
                    else:
                        resolved_argvalues.append([resolved_value])

            processed_parametrizations.append(
                {"argnames": argnames, "argvalues": resolved_argvalues}
            )

        # Combine parametrizations
        return self.combinator.combine(processed_parametrizations)

    def _resolve_value(self, value: Any, context: Dict[str, Any], metafunc=None) -> Any:
        """Resolve a value that may contain generators or DynRefs

        Args:
            value: The value to resolve
            context: Context for resolving dependencies
            metafunc: pytest's Metafunc object (optional, for method resolution)

        Returns:
            Resolved value
        """
        # If value is a callable (function/generator), call it
        if callable(value):
            import inspect

            # Check if it's a GeneratorBase instance (already wrapped)
            from ..generator.base import GeneratorBase

            if isinstance(value, GeneratorBase):
                # Call the generator to get preloaded/cached data
                result = value()
                return result
            # Check if it's a generator function (uses yield)
            elif inspect.isgeneratorfunction(value):
                # Execute the generator and collect all values
                result = list(value())
                return result
            # Check if it's an unbound method (method defined in class)
            elif inspect.isfunction(value) and hasattr(value, "__self__"):
                # It's a bound method, can call directly
                result = value()
                # Ensure result is a list
                if not isinstance(result, list):
                    return [result]
                return result
            elif inspect.ismethod(value):
                # It's a bound method, can call directly
                result = value()
                # Ensure result is a list
                if not isinstance(result, list):
                    return [result]
                return result
            else:
                # Check if it's a pytest fixture function - do not call it directly
                if (
                    hasattr(value, "__pytestfixturefunction__")
                    or hasattr(value, "_fixture_function_marker")
                    or hasattr(value, "_pytestfixturefunction")
                ):
                    # Return the fixture function as-is; pytest will inject it via its own mechanism
                    return value
                # It's a regular function
                # Try to call without arguments first
                try:
                    result = value()
                    # Ensure result is a list
                    if not isinstance(result, list):
                        return [result]
                    return result
                except TypeError as e:
                    if "missing 1 required positional argument" in str(
                        e
                    ) and "self" in str(e):
                        # It's an unbound method, skip it (should be handled differently)
                        # For now, return the value as-is to avoid breaking tests
                        return value
                    raise
        # If value is a DynRef or DynRefExpression, resolve it
        elif isinstance(value, (DynRef, DynRefExpression)):
            return value.resolve(context)
        # If value is a list, resolve each item
        elif isinstance(value, list):
            return [self._resolve_value(item, context) for item in value]
        # If value is a tuple, resolve each item
        elif isinstance(value, tuple):
            return tuple(self._resolve_value(item, context) for item in value)
        # If value is a dict, resolve each value
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, context) for k, v in value.items()}
        # Otherwise, return the value as-is
        else:
            return value

    def _apply_parametrization(
        self,
        metafunc: Metafunc,
        param_combinations: List[List[Any]],
        parametrizations: List[Dict[str, Any]] = None,
    ) -> None:
        """Apply parameterization to metafunc

        Args:
            metafunc: pytest's Metafunc object
            param_combinations: List of parameter combinations
            parametrizations: List of parametrization configurations (optional)
        """
        # Get argnames from the first parametrization
        if not parametrizations:
            # Fallback to getting parametrizations from metafunc
            # This is for backward compatibility with tests
            try:
                parametrizations = self._get_parametrizations(metafunc)
                if not parametrizations:
                    return
            except (TypeError, AttributeError):
                # If any error occurs, just return
                return

        argnames = parametrizations[0].get("argnames", "").split(",")
        argnames = [name.strip() for name in argnames]

        # Apply parametrization
        # For single argname, unwrap single-element lists: [[1],[2],[3]] -> [1,2,3]
        if len(argnames) == 1:
            unwrapped = []
            for combo in param_combinations:
                if isinstance(combo, (list, tuple)) and len(combo) == 1:
                    unwrapped.append(combo[0])
                else:
                    unwrapped.append(combo)
            param_combinations = unwrapped

        metafunc.parametrize(argnames=",".join(argnames), argvalues=param_combinations)
