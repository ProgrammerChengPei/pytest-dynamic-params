# Dependency management module

from .graph import DependencyGraph
from .resolver import DependencyResolver

__all__ = [
    "DependencyGraph",
    "DependencyResolver",
]
