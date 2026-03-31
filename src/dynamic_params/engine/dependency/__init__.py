# Dependency management module

from .dynref import DynRef
from .graph import DependencyGraph
from .resolver import DependencyResolver

__all__ = [
    "DynRef",
    "DependencyGraph",
    "DependencyResolver",
]
