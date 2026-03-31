# Dependency resolver implementation

from typing import Dict, List, Any

from .graph import DependencyGraph
from .dynref import DynRef, DynRefExpression
from ...errors import DependencyError

class DependencyResolver:
    """Class for resolving dependencies between parameters"""
    
    def __init__(self):
        """Initialize a dependency resolver"""
        self.graph = DependencyGraph()
    
    def resolve(self, dependencies: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all dependencies
        
        Args:
            dependencies: Dictionary of parameter names to their values (which may contain DynRefs)
            context: Dictionary of existing parameter values
            
        Returns:
            Dictionary of resolved parameter values
        """
        # Build dependency graph
        self._build_dependency_graph(dependencies, context)
        
        # Get topological order
        try:
            order = self.graph.topological_order()
        except Exception as e:
            raise DependencyError(f"Failed to resolve dependencies: {str(e)}")
        
        # Resolve dependencies in topological order
        resolved = context.copy()
        for param_name in order:
            if param_name in dependencies:
                value = dependencies[param_name]
                resolved_value = self._resolve_value(value, resolved)
                resolved[param_name] = resolved_value
        
        return resolved
    
    def _build_dependency_graph(self, dependencies: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Build the dependency graph
        
        Args:
            dependencies: Dictionary of parameter names to their values
            context: Dictionary of existing parameter values
        """
        # Clear existing graph
        self.graph = DependencyGraph()
        
        # Add all parameters to the graph first
        for param_name in dependencies:
            if param_name not in self.graph._graph:
                self.graph._graph[param_name] = set()
        
        # Add dependencies for each parameter
        for param_name, value in dependencies.items():
            # Find all DynRefs in the value
            refs = self._find_dynrefs(value)
            for ref_name in refs:
                # Add dependency
                self.graph.add_dependency(param_name, ref_name)
                # Ensure the referenced parameter is in the graph
                if ref_name not in self.graph._graph:
                    self.graph._graph[ref_name] = set()
    
    def _find_dynrefs(self, value: Any) -> List[str]:
        """Find all DynRefs in a value
        
        Args:
            value: The value to search for DynRefs
            
        Returns:
            List of parameter names referenced by DynRefs
        """
        refs = []
        
        def _find_dynrefs_recursive(val):
            if isinstance(val, DynRef):
                refs.append(val.name)
            elif isinstance(val, DynRefExpression):
                _find_dynrefs_recursive(val.left)
                _find_dynrefs_recursive(val.right)
            elif isinstance(val, (list, tuple)):
                for item in val:
                    _find_dynrefs_recursive(item)
            elif isinstance(val, dict):
                for item in val.values():
                    _find_dynrefs_recursive(item)
        
        _find_dynrefs_recursive(value)
        return refs
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Resolve a value that may contain DynRefs
        
        Args:
            value: The value to resolve
            context: Dictionary of parameter values
            
        Returns:
            The resolved value
        """
        if isinstance(value, (DynRef, DynRefExpression)):
            return value.resolve(context)
        elif isinstance(value, list):
            return [self._resolve_value(item, context) for item in value]
        elif isinstance(value, tuple):
            return tuple(self._resolve_value(item, context) for item in value)
        elif isinstance(value, dict):
            return {k: self._resolve_value(v, context) for k, v in value.items()}
        else:
            return value
