# Dependency resolution implementation

from typing import Dict, List, Optional, Set
from .graph import DependencyGraph
from ...errors import CircularDependencyError


class DependencyResolver:
    """Class for resolving dependency relationships and determining execution order"""
    
    def __init__(self):
        """Initialize a dependency resolver"""
        self._graph = DependencyGraph()
        self._resolved_dependencies: Dict[str, List[str]] = {}
    
    def add_function(self, func_name: str, dependencies: List[str]) -> None:
        """Add a function and its dependencies
        
        Args:
            func_name: Name of the function
            dependencies: List of function names that this function depends on
        """
        for dep in dependencies:
            self._graph.add_dependency(func_name, dep)
    
    def resolve_dependencies(self, target: str) -> List[str]:
        """Resolve dependencies for a target function
        
        Args:
            target: Function name to resolve dependencies for
            
        Returns:
            List of dependency functions in execution order
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        if target not in self._graph:
            return []
        
        # Check for circular dependencies
        if self._graph.has_cycle():
            raise CircularDependencyError("Circular dependency detected in the dependency graph")
        
        # Get topological order of all nodes and filter to target dependencies
        all_order = self._graph.topological_order()
        target_index = all_order.index(target)
        
        # Get dependencies that come before the target
        resolved = []
        for node in all_order[:target_index]:
            # Check if node is a dependency of the target
            if self._is_dependency(target, node):
                resolved.append(node)
        
        return resolved
    
    def _is_dependency(self, source: str, candidate: str) -> bool:
        """Check if candidate is a dependency of source node
        
        Args:
            source: Source node
            candidate: Candidate dependency node
            
        Returns:
            True if candidate is a dependency of source, False otherwise
        """
        def dfs(node: str, target: str, visited: Set[str]) -> bool:
            if node == target:
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            
            for neighbor in self._graph.get_dependencies(node):
                if dfs(neighbor, target, visited):
                    return True
            
            return False
        
        return dfs(source, candidate, set())
    
    def get_execution_order(self) -> List[str]:
        """Get topological execution order of all functions
        
        Returns:
            List of function names in topological order
            
        Raises:
            CircularDependencyError: If a circular dependency is detected
        """
        if self._graph.has_cycle():
            raise CircularDependencyError("Circular dependency detected")
        
        return self._graph.topological_order()
    
    def get_direct_dependencies(self, func_name: str) -> List[str]:
        """Get direct dependencies of a function
        
        Args:
            func_name: Function name
            
        Returns:
            List of direct dependency names
        """
        return self._graph.get_dependencies(func_name)

    def __contains__(self, func_name: str) -> bool:
        """Check if function is in the resolver"""
        return func_name in self._graph
    
    def __repr__(self) -> str:
        """String representation"""
        return f"DependencyResolver({len(self._graph)} functions)"