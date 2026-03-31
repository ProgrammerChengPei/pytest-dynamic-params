# Dependency graph implementation

from typing import Dict, List, Set

from ...errors import CircularDependencyError

class DependencyGraph:
    """Class for managing dependency relationships as a graph"""
    
    def __init__(self):
        """Initialize a dependency graph"""
        self._graph: Dict[str, Set[str]] = {}
    
    def add_dependency(self, from_node: str, to_node: str) -> None:
        """Add a dependency relationship
        
        Args:
            from_node: The node that depends on another node
            to_node: The node that is being depended on
        """
        if from_node not in self._graph:
            self._graph[from_node] = set()
        self._graph[from_node].add(to_node)
        
        # Ensure to_node is in the graph
        if to_node not in self._graph:
            self._graph[to_node] = set()
    
    def has_cycle(self) -> bool:
        """Check if the graph contains a cycle
        
        Returns:
            True if a cycle is detected, False otherwise
        """
        visited = set()
        recursion_stack = set()
        
        def has_cycle_util(node: str) -> bool:
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in self._graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle_util(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True
            
            recursion_stack.remove(node)
            return False
        
        for node in self._graph:
            if node not in visited:
                if has_cycle_util(node):
                    return True
        
        return False
    
    def topological_order(self) -> List[str]:
        """Get topological order of the graph
        
        Returns:
            List of nodes in topological order
            
        Raises:
            CircularDependencyError: If a cycle is detected
        """
        if self.has_cycle():
            raise CircularDependencyError("Circular dependency detected")
        
        in_degree = {}
        reverse_graph = {}
        
        for node in self._graph:
            in_degree[node] = 0
            reverse_graph[node] = set()
        
        for node in self._graph:
            for neighbor in self._graph[node]:
                reverse_graph[neighbor].add(node)
                in_degree[node] += 1
        
        queue = []
        for node in in_degree:
            if in_degree[node] == 0:
                queue.append(node)
        
        order = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            
            for dependent in reverse_graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        
        return order
    
    def get_dependencies(self, node: str) -> List[str]:
        """Get all dependencies of a node
        
        Args:
            node: The node to get dependencies for
            
        Returns:
            List of dependency nodes
        """
        return list(self._graph.get(node, set()))
    
    def __str__(self) -> str:
        """String representation"""
        return str(self._graph)
