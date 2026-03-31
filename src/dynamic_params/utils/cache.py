# Cache utility functions

import hashlib
from typing import Any, List, Dict

def generate_cache_key(func_name: str, args: List[Any], kwargs: Dict[str, Any]) -> str:
    """Generate a cache key based on function name and arguments
    
    Args:
        func_name: Name of the function
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Cache key as a string
    """
    # Create a string representation of the function and arguments
    args_repr = repr(args)
    kwargs_repr = repr(sorted(kwargs.items()))
    
    # Create a hash of the combined string
    combined = f"{func_name}:{args_repr}:{kwargs_repr}"
    return hashlib.md5(combined.encode()).hexdigest()
