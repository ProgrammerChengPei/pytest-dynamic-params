# pytest-dynamic-params plugin

from .__version__ import __version__
from .public.api import param_generator, parametrize_fixture

__all__ = [
    "__version__",
    "parametrize_fixture",
    "param_generator",
]
