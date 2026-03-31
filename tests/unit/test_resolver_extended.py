# Test dependency resolver module comprehensively

import pytest
from dynamic_params.engine.dependency.resolver import DependencyResolver
from dynamic_params.engine.dependency.dynref import DynRef
from dynamic_params.errors import DependencyError


class TestDependencyResolverExtended:
    """Extended tests for DependencyResolver"""
    
    def test_init(self):
        """Test initialization"""
        resolver = DependencyResolver()
        assert hasattr(resolver, "graph")
        assert resolver.graph is not None
    
    def test_resolve_empty_dependencies(self):
        """Test resolve with empty dependencies"""
        resolver = DependencyResolver()
        result = resolver.resolve({}, {})
        assert result == {}
    
    def test_resolve_no_dynrefs(self):
        """Test resolve with no DynRefs"""
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
    
    def test_resolve_simple_dynref(self):
        """Test resolve with simple DynRef"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("b"),
            "b": 42
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["b"] == 42
        assert result["a"] == 42
    
    def test_resolve_with_context(self):
        """Test resolve with existing context"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("existing")
        }
        context = {"existing": 100}
        result = resolver.resolve(dependencies, context)
        assert result["existing"] == 100
        assert result["a"] == 100
    
    def test_resolve_chain_dependency(self):
        """Test resolve with chain dependency"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("b"),
            "b": DynRef("c"),
            "c": 10
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["c"] == 10
        assert result["b"] == 10
        assert result["a"] == 10
    
    def test_resolve_dynref_expression(self):
        """Test resolve with DynRef expression"""
        resolver = DependencyResolver()
        dependencies = {
            "result": DynRef("a") + DynRef("b"),
            "a": 10,
            "b": 20
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] == 10
        assert result["b"] == 20
        assert result["result"] == 30
    
    def test_resolve_complex_expression(self):
        """Test resolve with complex expression"""
        resolver = DependencyResolver()
        dependencies = {
            "result": (DynRef("a") + DynRef("b")) * DynRef("c"),
            "a": 2,
            "b": 3,
            "c": 4
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["result"] == 20  # (2 + 3) * 4
    
    def test_resolve_with_list(self):
        """Test resolve with list containing DynRefs"""
        resolver = DependencyResolver()
        dependencies = {
            "items": [DynRef("a"), DynRef("b"), 3],
            "a": 1,
            "b": 2
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["items"] == [1, 2, 3]
    
    def test_resolve_with_tuple(self):
        """Test resolve with tuple containing DynRefs"""
        resolver = DependencyResolver()
        dependencies = {
            "pair": (DynRef("a"), DynRef("b")),
            "a": 10,
            "b": 20
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["pair"] == (10, 20)
    
    def test_resolve_with_dict(self):
        """Test resolve with dict containing DynRefs"""
        resolver = DependencyResolver()
        dependencies = {
            "data": {"x": DynRef("a"), "y": DynRef("b")},
            "a": 100,
            "b": 200
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["data"]["x"] == 100
        assert result["data"]["y"] == 200
    
    def test_resolve_nested_structures(self):
        """Test resolve with nested structures"""
        resolver = DependencyResolver()
        dependencies = {
            "nested": {
                "list": [DynRef("a"), {"key": DynRef("b")}],
                "tuple": (DynRef("c"), DynRef("d"))
            },
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["nested"]["list"] == [1, {"key": 2}]
        assert result["nested"]["tuple"] == (3, 4)
    
    def test_resolve_preserves_context(self):
        """Test resolve preserves existing context"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("b")
        }
        context = {"existing": 999, "b": 42}
        result = resolver.resolve(dependencies, context)
        assert result["existing"] == 999
        assert result["b"] == 42
        assert result["a"] == 42
    
    def test_resolve_circular_dependency_raises_error(self):
        """Test resolve raises error on circular dependency"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("b"),
            "b": DynRef("a")
        }
        context = {}
        
        with pytest.raises(DependencyError):
            resolver.resolve(dependencies, context)
    
    def test_resolve_missing_reference(self):
        """Test resolve with missing reference"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("nonexistent")
        }
        context = {}
        
        # Should raise an error when trying to resolve nonexistent reference
        with pytest.raises(Exception):
            resolver.resolve(dependencies, context)
    
    def test_resolve_multiple_dependencies_same_param(self):
        """Test resolve with multiple dependencies on same parameter"""
        resolver = DependencyResolver()
        dependencies = {
            "result": DynRef("base") * 2,
            "doubled": DynRef("base") * 4,
            "base": 10
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["base"] == 10
        assert result["result"] == 20
        assert result["doubled"] == 40
    
    def test_resolve_with_none_values(self):
        """Test resolve with None values"""
        resolver = DependencyResolver()
        dependencies = {
            "a": None,
            "b": DynRef("a")
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["a"] is None
        assert result["b"] is None
    
    def test_resolve_with_string_values(self):
        """Test resolve with string values"""
        resolver = DependencyResolver()
        dependencies = {
            "greeting": DynRef("name") + "!",
            "name": "World"
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["greeting"] == "World!"
    
    def test_find_dynrefs_in_list(self):
        """Test _find_dynrefs in list"""
        resolver = DependencyResolver()
        value = [DynRef("a"), 1, DynRef("b")]
        refs = resolver._find_dynrefs(value)
        assert "a" in refs
        assert "b" in refs
        assert len(refs) == 2
    
    def test_find_dynrefs_in_dict(self):
        """Test _find_dynrefs in dict"""
        resolver = DependencyResolver()
        value = {"x": DynRef("a"), "y": DynRef("b")}
        refs = resolver._find_dynrefs(value)
        assert "a" in refs
        assert "b" in refs
        assert len(refs) == 2
    
    def test_find_dynrefs_nested(self):
        """Test _find_dynrefs in nested structure"""
        resolver = DependencyResolver()
        value = {
            "list": [DynRef("a"), {"key": DynRef("b")}],
            "tuple": (DynRef("c"),)
        }
        refs = resolver._find_dynrefs(value)
        assert "a" in refs
        assert "b" in refs
        assert "c" in refs
        assert len(refs) == 3
    
    def test_find_dynrefs_no_dynrefs(self):
        """Test _find_dynrefs with no DynRefs"""
        resolver = DependencyResolver()
        value = [1, 2, 3, {"key": "value"}]
        refs = resolver._find_dynrefs(value)
        assert refs == []
    
    def test_resolve_value_plain_value(self):
        """Test _resolve_value with plain value"""
        resolver = DependencyResolver()
        value = 42
        context = {}
        result = resolver._resolve_value(value, context)
        assert result == 42
    
    def test_resolve_value_dynref(self):
        """Test _resolve_value with DynRef"""
        resolver = DependencyResolver()
        value = DynRef("a")
        context = {"a": 100}
        result = resolver._resolve_value(value, context)
        assert result == 100
    
    def test_resolve_value_expression(self):
        """Test _resolve_value with DynRefExpression"""
        resolver = DependencyResolver()
        value = DynRef("a") + DynRef("b")
        context = {"a": 10, "b": 20}
        result = resolver._resolve_value(value, context)
        assert result == 30


class TestDependencyResolverEdgeCases:
    """Edge case tests for DependencyResolver"""
    
    def test_resolve_empty_dependencies_with_context(self):
        """Test resolve empty dependencies with non-empty context"""
        resolver = DependencyResolver()
        result = resolver.resolve({}, {"existing": 123})
        assert result["existing"] == 123
    
    def test_resolve_self_referencing_dynref(self):
        """Test resolve self-referencing DynRef (should cause cycle)"""
        resolver = DependencyResolver()
        dependencies = {
            "a": DynRef("a")
        }
        context = {}
        
        with pytest.raises(DependencyError):
            resolver.resolve(dependencies, context)
    
    def test_resolve_deep_nesting(self):
        """Test resolve with deeply nested structure"""
        resolver = DependencyResolver()
        dependencies = {
            "level1": {
                "level2": {
                    "level3": {
                        "value": DynRef("x")
                    }
                }
            },
            "x": 42
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["level1"]["level2"]["level3"]["value"] == 42
    
    def test_resolve_mixed_types_in_list(self):
        """Test resolve with mixed types in list"""
        resolver = DependencyResolver()
        dependencies = {
            "mixed": [
                DynRef("a"),
                "string",
                123,
                {"key": DynRef("b")},
                (DynRef("c"),)
            ],
            "a": 1,
            "b": 2,
            "c": 3
        }
        context = {}
        result = resolver.resolve(dependencies, context)
        assert result["mixed"][0] == 1
        assert result["mixed"][1] == "string"
        assert result["mixed"][2] == 123
        assert result["mixed"][3] == {"key": 2}
        assert result["mixed"][4] == (3,)
