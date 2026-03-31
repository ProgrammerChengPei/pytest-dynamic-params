# Test DependencyResolver functionality

import pytest
from dynamic_params.engine.dependency.resolver import DependencyResolver
from dynamic_params.engine.dependency.dynref import DynRef
from dynamic_params.errors import DependencyError, CircularDependencyError


class TestDependencyResolver:
    """Test DependencyResolver class"""
    
    def test_resolver_init(self):
        """Test DependencyResolver initialization"""
        resolver = DependencyResolver()
        assert resolver.graph is not None
    
    def test_resolve_simple(self):
        """Test resolve with simple dependencies"""
        resolver = DependencyResolver()
        dependencies = {
            "a": 1,
            "b": 2,
            "c": 3
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 1
        assert result["b"] == 2
        assert result["c"] == 3
    
    def test_resolve_with_dynref(self):
        """Test resolve with DynRef"""
        resolver = DependencyResolver()
        dependencies = {
            "a": 1,
            "b": DynRef("a")
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 1
        assert result["b"] == 1
    
    def test_resolve_with_context(self):
        """Test resolve with context"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("existing")
        }
        context = {"existing": 42}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 42
    
    def test_resolve_with_expression(self):
        """Test resolve with DynRef expression"""
        resolver = DependencyResolver()
        dependencies = {
                "a": 10,
            "b": 20,
            "sum": DynRef("a") + DynRef("b")
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 10
        assert result["b"] == 20
        assert result["sum"] == 30
    
    def test_resolve_with_nested_dynref(self):
        """Test resolve with nested DynRef"""
        resolver = DependencyResolver()
        dependencies = {
            "a": 5,
            "b": DynRef("a"),
            "c": DynRef("b")
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 5
        assert result["b"] == 5
        assert result["c"] == 5
    
    def test_resolve_with_list(self):
        """Test resolve with list containing DynRef"""
        resolver = DependencyResolver()
        dependencies = {
            "a": 1,
            "b": [DynRef("a"), 2, 3]
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 1
        assert result["b"] == [1, 2, 3]
    
    def test_resolve_with_dict(self):
        """Test resolve with dict containing DynRef"""
        resolver = DependencyResolver()
        dependencies = {
            "a": 1,
            "b": {"x": DynRef("a"), "y": 2}
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 1
        assert result["b"] == {"x": 1, "y": 2}
    
    def test_resolve_with_tuple(self):
        """Test resolve with tuple containing DynRef"""
        resolver = DependencyResolver()
        dependencies = {
            "a": 1,
            "b": (DynRef("a"), 2, 3)
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 1
        assert result["b"] == (1, 2, 3)
    
    def test_resolve_with_circular_dependency(self):
        """Test resolve with circular dependency"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("b"),
            "b": DynRef("a")
        }
        context = {}
        with pytest.raises(DependencyError):
            resolver.resolve(dependencies, context)
    
    def test_find_dynrefs_simple(self):
        """Test _find_dynrefs with simple values"""
        resolver = DependencyResolver()
        refs = resolver._find_dynrefs(42)
        assert refs == []
    
    def test_find_dynrefs_with_dynref(self):
        """Test _find_dynrefs with DynRef"""
        resolver = DependencyResolver()
        refs = resolver._find_dynrefs(DynRef("a"))
        assert refs == ["a"]
    
    def test_find_dynrefs_with_list(self):
        """Test _find_dynrefs with list"""
        resolver = DependencyResolver()
        refs = resolver._find_dynrefs([1, DynRef("a"), DynRef("b")])
        assert "a" in refs
        assert "b" in refs
    
    def test_find_dynrefs_with_dict(self):
        """Test _find_dynrefs with dict"""
        resolver = DependencyResolver()
        refs = resolver._find_dynrefs({"x": DynRef("a"), "y": DynRef("b")})
        assert "a" in refs
        assert "b" in refs
    
    def test_resolve_value_simple(self):
        """Test _resolve_value with simple value"""
        resolver = DependencyResolver()
        result = resolver._resolve_value(42, {})
        assert result == 42
    
    def test_resolve_value_with_dynref(self):
        """Test _resolve_value with DynRef"""
        resolver = DependencyResolver()
        result = resolver._resolve_value(DynRef("a"), {"a": 10})
        assert result == 10
    
    def test_resolve_value_with_list(self):
        """Test _resolve_value with list"""
        resolver = DependencyResolver()
        result = resolver._resolve_value([1, DynRef("a"), 3], {"a": 2})
        assert result == [1, 2, 3]
    
    def test_resolve_value_with_dict(self):
        """Test _resolve_value with dict"""
        resolver = DependencyResolver()
        result = resolver._resolve_value({"x": DynRef("a"), "y": 2}, {"a": 10})
        assert result == {"x": 10, "y": 2}
