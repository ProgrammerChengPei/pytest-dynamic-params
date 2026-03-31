# Test DynRef functionality

import pytest
from dynamic_params.engine.dependency.dynref import DynRef

class TestDynRef:
    """Test DynRef class"""
    
    def test_dynref_resolve(self):
        """Test resolving a DynRef"""
        # Create a DynRef
        dyn_ref = DynRef("test_param")
        
        # Create context
        context = {"test_param": 42}
        
        # Resolve the DynRef
        result = dyn_ref.resolve(context)
        
        # Check result
        assert result == 42
    
    def test_dynref_resolve_not_found(self):
        """Test resolving a DynRef that doesn't exist"""
        # Create a DynRef
        dyn_ref = DynRef("non_existent_param")
        
        # Create context
        context = {"other_param": 42}
        
        # Check that resolving raises an error
        with pytest.raises(Exception):
            dyn_ref.resolve(context)
    
    def test_dynref_addition(self):
        """Test DynRef addition"""
        # Create DynRef instances
        a = DynRef("a")
        b = DynRef("b")
        
        # Create expression
        expr = a + b
        
        # Create context
        context = {"a": 10, "b": 20}
        
        # Resolve the expression
        result = expr.resolve(context)
        
        # Check result
        assert result == 30
    
    def test_dynref_subtraction(self):
        """Test DynRef subtraction"""
        # Create DynRef instances
        a = DynRef("a")
        b = DynRef("b")
        
        # Create expression
        expr = a - b
        
        # Create context
        context = {"a": 30, "b": 10}
        
        # Resolve the expression
        result = expr.resolve(context)
        
        # Check result
        assert result == 20
    
    def test_dynref_multiplication(self):
        """Test DynRef multiplication"""
        # Create DynRef instances
        a = DynRef("a")
        b = DynRef("b")
        
        # Create expression
        expr = a * b
        
        # Create context
        context = {"a": 5, "b": 6}
        
        # Resolve the expression
        result = expr.resolve(context)
        
        # Check result
        assert result == 30
    
    def test_dynref_division(self):
        """Test DynRef division"""
        # Create DynRef instances
        a = DynRef("a")
        b = DynRef("b")
        
        # Create expression
        expr = a / b
        
        # Create context
        context = {"a": 20, "b": 4}
        
        # Resolve the expression
        result = expr.resolve(context)
        
        # Check result
        assert result == 5
