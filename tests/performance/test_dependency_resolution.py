"""
Performance tests for dependency resolution.

Tests dependency resolution performance including:
- Dependency graph construction
- Cycle detection
- Topological sorting
- DynRef resolution
- Complex dependency chains
"""

import pytest
import time
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from dynamic_params import parametrize_test, DynRef
from dynamic_params.engine.dependency import DependencyResolver, DependencyGraph


class TestDependencyGraphConstruction:
    """Test dependency graph construction performance."""
    
    def test_graph_construction_small(self, timer, benchmark_config):
        """Test small dependency graph construction."""
        resolver = DependencyResolver()
        
        dependencies = {
            "a": [1],
            "b": [DynRef("a")],
            "c": [DynRef("a"), DynRef("b")],
        }
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        assert timer.elapsed < 10, f"Small graph construction took {timer.elapsed:.2f}ms"
        assert "a" in resolved
        assert "b" in resolved
        assert "c" in resolved
    
    def test_graph_construction_large(self, timer, benchmark_config):
        """Test large dependency graph construction."""
        resolver = DependencyResolver()
        
        # Create a large dependency graph
        num_nodes = benchmark_config["sample_size"]
        dependencies = {}
        
        for i in range(num_nodes):
            if i == 0:
                dependencies[f"node_{i}"] = [i]
            else:
                # Each node depends on up to 5 previous nodes
                dep_values = [DynRef(f"node_{j}") for j in range(max(0, i - 5), i)]
                dependencies[f"node_{i}"] = dep_values
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        assert len(resolved) == num_nodes
        assert timer.elapsed < 500, f"Large graph construction took {timer.elapsed:.2f}ms"
    
    def test_graph_construction_complex(self, timer):
        """Test complex dependency graph construction."""
        resolver = DependencyResolver()
        
        # Create a complex dependency pattern
        dependencies = {}
        layers = 10
        nodes_per_layer = 20
        
        for layer in range(layers):
            for node in range(nodes_per_layer):
                node_name = f"layer{layer}_node{node}"
                if layer == 0:
                    dependencies[node_name] = [layer * nodes_per_layer + node]
                else:
                    # Depend on nodes from previous layer
                    deps = []
                    for prev_node in range(nodes_per_layer):
                        deps.append(DynRef(f"layer{layer-1}_node{prev_node}"))
                    dependencies[node_name] = deps
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        total_nodes = layers * nodes_per_layer
        assert len(resolved) == total_nodes
        assert timer.elapsed < 1000, f"Complex graph took {timer.elapsed:.2f}ms"


class TestCycleDetection:
    """Test cycle detection performance."""
    
    def test_cycle_detection_no_cycle(self, timer, benchmark_config):
        """Test cycle detection in acyclic graph."""
        graph = DependencyGraph()
        
        # Build a large acyclic graph
        num_nodes = benchmark_config["sample_size"]
        for i in range(num_nodes):
            if i > 0:
                graph.add_dependency(f"node_{i}", f"node_{i-1}")
        
        with timer:
            has_cycle = graph.has_cycle()
        
        assert not has_cycle
        assert timer.elapsed < 200, f"Cycle detection took {timer.elapsed:.2f}ms"
    
    def test_cycle_detection_with_cycle(self, timer):
        """Test cycle detection in cyclic graph."""
        graph = DependencyGraph()
        
        # Build a graph with a cycle
        graph.add_dependency("a", "b")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "d")
        graph.add_dependency("d", "a")  # Creates cycle
        
        with timer:
            has_cycle = graph.has_cycle()
        
        assert has_cycle
        assert timer.elapsed < 50, f"Cycle detection took {timer.elapsed:.2f}ms"
    
    def test_cycle_detection_large_graph(self, timer, benchmark_config):
        """Test cycle detection in large graph."""
        graph = DependencyGraph()
        
        num_nodes = benchmark_config["sample_size"]
        for i in range(num_nodes):
            if i > 0:
                # Add multiple dependencies
                for j in range(max(0, i - 10), i):
                    graph.add_dependency(f"node_{i}", f"node_{j}")
        
        with timer:
            has_cycle = graph.has_cycle()
        
        assert not has_cycle  # This graph is acyclic
        assert timer.elapsed < 500, f"Large graph cycle detection took {timer.elapsed:.2f}ms"


class TestTopologicalSort:
    """Test topological sorting performance."""
    
    def test_topological_sort_small(self, timer):
        """Test topological sort on small graph."""
        graph = DependencyGraph()
        
        graph.add_dependency("a", "c")
        graph.add_dependency("b", "c")
        graph.add_dependency("c", "d")
        graph.add_dependency("c", "e")
        
        with timer:
            order = graph.topological_order()
        
        assert len(order) == 5
        assert timer.elapsed < 10, f"Small topo sort took {timer.elapsed:.2f}ms"
    
    def test_topological_sort_large(self, timer, benchmark_config):
        """Test topological sort on large graph."""
        graph = DependencyGraph()
        
        num_nodes = benchmark_config["sample_size"]
        for i in range(num_nodes):
            if i > 0:
                for j in range(max(0, i - 5), i):
                    graph.add_dependency(f"node_{i}", f"node_{j}")
        
        with timer:
            order = graph.topological_order()
        
        assert len(order) == num_nodes
        assert timer.elapsed < 500, f"Large topo sort took {timer.elapsed:.2f}ms"


class TestDynRefResolution:
    """Test DynRef resolution performance."""
    
    def test_dynref_simple_resolution(self, timer, benchmark_config):
        """Test simple DynRef resolution."""
        context = {"a": 10, "b": 20}
        
        resolution_times = []
        for _ in range(benchmark_config["benchmark_iterations"]):
            ref = DynRef("a")
            with timer:
                value = ref.resolve(context)
            resolution_times.append(timer.elapsed)
            assert value == 10
        
        avg_time = sum(resolution_times) / len(resolution_times)
        assert avg_time < 2, f"Simple DynRef resolution took {avg_time:.2f}ms"
    
    def test_dynref_expression_resolution(self, timer, benchmark_config):
        """Test DynRef expression resolution."""
        context = {"a": 10, "b": 20, "c": 5}
        
        resolution_times = []
        for _ in range(benchmark_config["benchmark_iterations"]):
            expr = DynRef("a") + DynRef("b") * DynRef("c")
            with timer:
                value = expr.resolve(context)
            resolution_times.append(timer.elapsed)
            assert value == 10 + 20 * 5
        
        avg_time = sum(resolution_times) / len(resolution_times)
        assert avg_time < 5, f"Expression resolution took {avg_time:.2f}ms"
    
    def test_dynref_complex_expression(self, timer):
        """Test complex DynRef expression resolution."""
        context = {
            "x": 100,
            "y": 50,
            "z": 25,
            "w": 10,
        }
        
        # Build complex expression
        expr = (
            DynRef("x") * 2 +
            DynRef("y") - DynRef("z") / DynRef("w")
        )
        
        with timer:
            value = expr.resolve(context)
        
        expected = 100 * 2 + 50 - 25 / 10
        assert abs(value - expected) < 0.01
        assert timer.elapsed < 10, f"Complex expression took {timer.elapsed:.2f}ms"


class TestDependencyResolverPerformance:
    """Test overall dependency resolver performance."""
    
    def test_resolve_dependencies_simple(self, timer):
        """Test resolving simple dependencies."""
        resolver = DependencyResolver()
        
        # Use scalar values, not lists
        dependencies = {
            "a": 1,
            "b": DynRef("a") + 1,
            "c": DynRef("b") + DynRef("a"),
        }
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        assert resolved["a"] == 1
        assert resolved["b"] == 2
        assert resolved["c"] == 3
        assert timer.elapsed < 20, f"Simple resolution took {timer.elapsed:.2f}ms"
    
    def test_resolve_dependencies_chain(self, timer, benchmark_config):
        """Test resolving dependency chain."""
        resolver = DependencyResolver()
        
        chain_length = 50
        dependencies = {}
        
        for i in range(chain_length):
            if i == 0:
                dependencies[f"node_{i}"] = 1
            else:
                dependencies[f"node_{i}"] = DynRef(f"node_{i-1}") + 1
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        assert resolved[f"node_{chain_length-1}"] == chain_length
        assert timer.elapsed < 200, f"Chain resolution took {timer.elapsed:.2f}ms"
    
    def test_resolve_dependencies_dag(self, timer):
        """Test resolving DAG dependencies."""
        resolver = DependencyResolver()
        
        # Create a diamond-shaped dependency graph
        dependencies = {
            "top": 1,
            "left": DynRef("top") + 1,
            "right": DynRef("top") * 2,
            "bottom": DynRef("left") + DynRef("right"),
        }
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        assert resolved["top"] == 1
        assert resolved["left"] == 2
        assert resolved["right"] == 2
        assert resolved["bottom"] == 4
        assert timer.elapsed < 30, f"DAG resolution took {timer.elapsed:.2f}ms"


class TestDependencyStress:
    """Stress tests for dependency resolution."""
    
    def test_many_dependencies(self, timer, benchmark_config):
        """Test resolving many dependencies."""
        resolver = DependencyResolver()
        
        num_deps = benchmark_config["sample_size"]
        dependencies = {}
        
        for i in range(num_deps):
            if i == 0:
                dependencies[f"dep_{i}"] = i
            else:
                # Create a sum expression using DynRefs
                deps = [DynRef(f"dep_{j}") for j in range(max(0, i - 3), i)]
                if deps:
                    # Build expression: dep_0 + dep_1 + ... + dep_{i-1}
                    expr = deps[0]
                    for dep in deps[1:]:
                        expr = expr + dep
                    dependencies[f"dep_{i}"] = expr
                else:
                    dependencies[f"dep_{i}"] = i
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        assert len(resolved) == num_deps
        assert timer.elapsed < 1000, f"Many deps took {timer.elapsed:.2f}ms"
    
    def test_deep_dependency_chain(self, timer):
        """Test deep dependency chain resolution."""
        resolver = DependencyResolver()
        
        depth = 100
        dependencies = {}
        
        for i in range(depth):
            if i == 0:
                dependencies[f"level_{i}"] = 1
            else:
                dependencies[f"level_{i}"] = DynRef(f"level_{i-1}") * 2
        
        context = {}
        
        with timer:
            resolved = resolver.resolve(dependencies, context)
        
        expected = 2 ** (depth - 1)
        assert resolved[f"level_{depth-1}"] == expected
        assert timer.elapsed < 500, f"Deep chain took {timer.elapsed:.2f}ms"
