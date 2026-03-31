# Test dependency graph module comprehensively

import pytest
from dynamic_params.engine.dependency.graph import DependencyGraph
from dynamic_params.errors import CircularDependencyError


class TestDependencyGraphExtended:
    """Extended tests for DependencyGraph"""
    
    def test_init_empty_graph(self):
        """Test initialization creates empty graph"""
        graph = DependencyGraph()
        assert graph._graph == {}
    
    def test_add_dependency_first_node(self):
        """Test adding first dependency"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        assert "a" in graph._graph
        assert "b" in graph._graph
        assert "b" in graph._graph["a"]
    
    def test_add_dependency_existing_node(self):
        """Test adding dependency to existing node"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        assert graph._graph["a"] == {"b", "c"}
    
    def test_add_dependency_multiple_relationships(self):
        """Test adding multiple dependency relationships"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "d")
        
        assert "b" in graph._graph["a"]
        assert "c" in graph._graph["b"]
        assert "d" in graph._graph["c"]
    
    def test_add_dependency_duplicate(self):
        """Test adding duplicate dependency (should not duplicate)"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "b")  # Duplicate
        assert len(graph._graph["a"]) == 1
    
    def test_has_cycle_no_cycle(self):
        """Test has_cycle with no cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "d")
        
        assert graph.has_cycle() is False
    
    def test_has_cycle_simple_cycle(self):
        """Test has_cycle with simple cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "a")  # Creates cycle
        
        assert graph.has_cycle() is True
    
    def test_has_cycle_self_loop(self):
        """Test has_cycle with self-loop"""
        graph = DependencyGraph()
        graph.add_dependency("a", "a")  # Self-loop
        
        assert graph.has_cycle() is True
    
    def test_has_cycle_complex_graph_no_cycle(self):
        """Test has_cycle with complex graph without cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        graph.add_dependency("b", "d")
        graph.add_dependency("c", "d")
        graph.add_dependency("d", "e")
        
        assert graph.has_cycle() is False
    
    def test_has_cycle_complex_graph_with_cycle(self):
        """Test has_cycle with complex graph with cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "d")
        graph.add_dependency("d", "e")
        graph.add_dependency("e", "b")  # Creates cycle
        
        assert graph.has_cycle() is True
    
    def test_has_cycle_empty_graph(self):
        """Test has_cycle with empty graph"""
        graph = DependencyGraph()
        assert graph.has_cycle() is False
    
    def test_has_cycle_single_node(self):
        """Test has_cycle with single node"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        # Only "a" has dependencies, "b" and "c" are leaves
        
        assert graph.has_cycle() is False
    
    def test_topological_order_simple(self):
        """Test topological_order with simple graph"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        
        order = graph.topological_order()
        # c must come before b, b must come before a
        assert order.index("c") < order.index("b")
        assert order.index("b") < order.index("a")
    
    def test_topological_order_complex(self):
        """Test topological_order with complex graph"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        graph.add_dependency("b", "d")
        graph.add_dependency("c", "d")
        graph.add_dependency("d", "e")
        
        order = graph.topological_order()
        # e must come first, then d, then b and c, then a
        assert order.index("e") < order.index("d")
        assert order.index("d") < order.index("b")
        assert order.index("d") < order.index("c")
        assert order.index("b") < order.index("a")
        assert order.index("c") < order.index("a")
    
    def test_topological_order_with_cycle_raises_error(self):
        """Test topological_order raises error when cycle exists"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "a")
        
        with pytest.raises(CircularDependencyError):
            graph.topological_order()
    
    def test_topological_order_empty_graph(self):
        """Test topological_order with empty graph"""
        graph = DependencyGraph()
        order = graph.topological_order()
        assert order == []
    
    def test_topological_order_single_node(self):
        """Test topological_order with single node"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        order = graph.topological_order()
        assert len(order) == 2
        assert "a" in order
        assert "b" in order
    
    def test_get_dependencies_basic(self):
        """Test get_dependencies basic functionality"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        graph.add_dependency("a", "d")
        
        deps = graph.get_dependencies("a")
        assert len(deps) == 3
        assert "b" in deps
        assert "c" in deps
        assert "d" in deps
    
    def test_get_dependencies_no_dependencies(self):
        """Test get_dependencies when node has no dependencies"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        
        deps = graph.get_dependencies("b")
        assert deps == []
    
    def test_get_dependencies_nonexistent_node(self):
        """Test get_dependencies for nonexistent node"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        
        deps = graph.get_dependencies("z")
        assert deps == []
    
    def test_str_representation(self):
        """Test string representation"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        
        str_repr = str(graph)
        assert "a" in str_repr
        assert "b" in str_repr
        assert "c" in str_repr
    
    def test_add_dependency_chain(self):
        """Test adding a chain of dependencies"""
        graph = DependencyGraph()
        nodes = ["a", "b", "c", "d", "e"]
        for i in range(len(nodes) - 1):
            graph.add_dependency(nodes[i], nodes[i + 1])
        
        # Verify chain
        assert "b" in graph._graph["a"]
        assert "c" in graph._graph["b"]
        assert "d" in graph._graph["c"]
        assert "e" in graph._graph["d"]
    
    def test_topological_order_diamond_dependency(self):
        """Test topological_order with diamond dependency pattern"""
        graph = DependencyGraph()
        # Diamond: a -> b, a -> c, b -> d, c -> d
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        graph.add_dependency("b", "d")
        graph.add_dependency("c", "d")
        
        order = graph.topological_order()
        # d must come first
        assert order.index("d") == 0
        # b and c must come before a
        assert order.index("b") < order.index("a")
        assert order.index("c") < order.index("a")


class TestDependencyGraphEdgeCases:
    """Edge case tests for DependencyGraph"""
    
    def test_add_dependency_same_node_twice(self):
        """Test adding same dependency twice"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "b")
        assert len(graph._graph["a"]) == 1
    
    def test_has_cycle_multiple_cycles(self):
        """Test has_cycle with multiple cycles"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "a")  # First cycle
        graph.add_dependency("d", "e")
        graph.add_dependency("e", "f")
        graph.add_dependency("f", "d")  # Second cycle
        
        assert graph.has_cycle() is True
    
    def test_topological_order_multiple_valid_orders(self):
        """Test topological_order with multiple valid orders"""
        graph = DependencyGraph()
        graph.add_dependency("a", "c")
        graph.add_dependency("b", "c")
        
        order = graph.topological_order()
        # c has no dependencies, so it comes first
        # a and b depend on c, so they come after
        assert order.index("c") == 0
        # a and b can be in any order after c
        assert "a" in order[1:]
        assert "b" in order[1:]
    
    def test_get_dependencies_returns_list_not_set(self):
        """Test get_dependencies returns a list, not a set"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        
        deps = graph.get_dependencies("a")
        assert isinstance(deps, list)
        assert not isinstance(deps, set)
