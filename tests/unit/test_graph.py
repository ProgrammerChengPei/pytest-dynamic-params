# Test dependency graph functionality

import pytest
from dynamic_params.engine.dependency.graph import DependencyGraph
from dynamic_params.errors import CircularDependencyError


class TestDependencyGraph:
    """Test DependencyGraph class"""

    def test_graph_init(self):
        """Test DependencyGraph initialization"""
        graph = DependencyGraph()
        assert graph._graph == {}

    def test_add_dependency(self):
        """Test adding dependency"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        assert "a" in graph._graph
        assert "b" in graph._graph["a"]
        assert "b" in graph._graph

    def test_add_multiple_dependencies(self):
        """Test adding multiple dependencies"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        assert "a" in graph._graph
        assert "b" in graph._graph["a"]
        assert "c" in graph._graph["a"]

    def test_has_cycle_no_cycle(self):
        """Test has_cycle with no cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        assert graph.has_cycle() is False

    def test_has_cycle_with_cycle(self):
        """Test has_cycle with cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "a")
        assert graph.has_cycle() is True

    def test_has_cycle_self_dependency(self):
        """Test has_cycle with self dependency"""
        graph = DependencyGraph()
        graph.add_dependency("a", "a")
        assert graph.has_cycle() is True

    def test_topological_order_simple(self):
        """Test topological order with simple graph"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        order = graph.topological_order()
        assert "b" in order
        assert "a" in order
        b_index = order.index("b")
        a_index = order.index("a")
        assert b_index < a_index

    def test_topological_order_complex(self):
        """Test topological order with complex graph"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        graph.add_dependency("b", "d")
        graph.add_dependency("c", "d")
        order = graph.topological_order()
        assert "d" in order
        assert "c" in order
        assert "b" in order
        assert "a" in order
        d_index = order.index("d")
        b_index = order.index("b")
        c_index = order.index("c")
        a_index = order.index("a")
        assert d_index < b_index
        assert d_index < c_index
        assert b_index < a_index
        assert c_index < a_index

    def test_topological_order_with_cycle(self):
        """Test topological order with cycle"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "a")
        with pytest.raises(CircularDependencyError):
            graph.topological_order()

    def test_get_dependencies(self):
        """Test get_dependencies"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        graph.add_dependency("a", "c")
        deps = graph.get_dependencies("a")
        assert "b" in deps
        assert "c" in deps

    def test_get_dependencies_no_deps(self):
        """Test get_dependencies with no dependencies"""
        graph = DependencyGraph()
        deps = graph.get_dependencies("a")
        assert deps == []

    def test_str(self):
        """Test string representation"""
        graph = DependencyGraph()
        graph.add_dependency("a", "b")
        str_repr = str(graph)
        assert "a" in str_repr
        assert "b" in str_repr
