# Test DynRef and DynRefExpression functionality

import pytest
from dynamic_params.engine.dependency.dynref import DynRef, DynRefExpression


class TestDynRefOperators:
    """Test DynRef operator overloading"""
    
    def test_dynref_str(self):
        """Test DynRef string representation"""
        ref = DynRef("test")
        assert str(ref) == "DynRef('test')"
    
    def test_dynref_addition_with_value(self):
        """Test DynRef addition with regular value"""
        ref = DynRef("a")
        expr = ref + 5
        
        context = {"a": 10}
        result = expr.resolve(context)
        
        assert result == 15
    
    def test_dynref_subtraction_with_value(self):
        """Test DynRef subtraction with regular value"""
        ref = DynRef("a")
        expr = ref - 5
        
        context = {"a": 10}
        result = expr.resolve(context)
        
        assert result == 5
    
    def test_dynref_multiplication_with_value(self):
        """Test DynRef multiplication with regular value"""
        ref = DynRef("a")
        expr = ref * 5
        
        context = {"a": 10}
        result = expr.resolve(context)
        
        assert result == 50
    
    def test_dynref_division_with_value(self):
        """Test DynRef division with regular value"""
        ref = DynRef("a")
        expr = ref / 5
        
        context = {"a": 10}
        result = expr.resolve(context)
        
        assert result == 2.0
    
    def test_dynref_expression_str(self):
        """Test DynRefExpression string representation"""
        ref = DynRef("a")
        expr = ref + DynRef("b")
        
        str_repr = str(expr)
        assert "+" in str_repr


class TestDynRefExpressionOperators:
    """Test DynRefExpression with multiple operators"""
    
    def test_chained_addition(self):
        """Test chained addition"""
        a = DynRef("a")
        b = DynRef("b")
        c = DynRef("c")
        
        # Chain using explicit expressions
        expr = (a + b) + c
        context = {"a": 1, "b": 2, "c": 3}
        
        result = expr.resolve(context)
        assert result == 6
    
    def test_mixed_operations(self):
        """Test mixed operations"""
        a = DynRef("a")
        b = DynRef("b")
        
        expr = (a + b) * 2
        context = {"a": 5, "b": 3}
        
        result = expr.resolve(context)
        assert result == 16
    
    def test_division_by_zero(self):
        """Test division by zero"""
        a = DynRef("a")
        b = DynRef("b")
        
        expr = a / b
        context = {"a": 10, "b": 0}
        
        with pytest.raises(ZeroDivisionError):
            expr.resolve(context)
    
    def test_expression_with_nested_expression(self):
        """Test expression with nested expression"""
        a = DynRef("a")
        b = DynRef("b")
        c = DynRef("c")
        
        expr = (a + b) * (c - 2)
        context = {"a": 5, "b": 3, "c": 4}
        
        result = expr.resolve(context)
        assert result == 16
