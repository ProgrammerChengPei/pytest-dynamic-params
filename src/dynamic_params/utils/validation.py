# Validation utility functions

from typing import Any, List

from ..errors import ParametrizeError

def validate_parametrize_args(argnames: str, argvalues: List[Any]) -> None:
    """Validate parametrize arguments
    
    Args:
        argnames: Comma-separated string of parameter names
        argvalues: List of parameter values
        
    Raises:
        ParametrizeError: If validation fails
    """
    # Check that argnames is a string
    if not isinstance(argnames, str):
        raise ParametrizeError("argnames must be a string")
    
    # Check that argvalues is a list
    if not isinstance(argvalues, list):
        raise ParametrizeError("argvalues must be a list")
    
    # Check that argnames is not empty
    if not argnames.strip():
        raise ParametrizeError("argnames cannot be empty")
    
    # Check that argvalues is not empty
    if not argvalues:
        raise ParametrizeError("argvalues cannot be empty")
