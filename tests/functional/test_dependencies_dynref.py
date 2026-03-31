"""
Advanced functional tests for dependency management and DynRef.

Tests parameter dependencies, DynRef expressions, and complex dependency chains.
"""

import pytest
from dynamic_params import parametrize_test, param_generator, DynRef


class TestDynRefBasic:
    """Test basic DynRef functionality."""
    
    def test_dynref_addition(self):
        """Test DynRef addition operation."""
        @parametrize_test("a, b, expected", [
            [1, 2, DynRef("a") + DynRef("b")],
            [3, 4, DynRef("a") + DynRef("b")],
            [5, 6, DynRef("a") + DynRef("b")],
        ])
        def test_add(a, b, expected):
            assert a + b == expected
        
        test_add(1, 2, 3)
        test_add(3, 4, 7)
        test_add(5, 6, 11)
    
    def test_dynref_multiplication(self):
        """Test DynRef multiplication operation."""
        @parametrize_test("x, y, product", [
            [2, 3, DynRef("x") * DynRef("y")],
            [4, 5, DynRef("x") * DynRef("y")],
            [6, 7, DynRef("x") * DynRef("y")],
        ])
        def test_mul(x, y, product):
            assert x * y == product
        
        test_mul(2, 3, 6)
        test_mul(4, 5, 20)
        test_mul(6, 7, 42)
    
    def test_dynref_subtraction(self):
        """Test DynRef subtraction operation."""
        @parametrize_test("a, b, result", [
            [10, 3, DynRef("a") - DynRef("b")],
            [20, 5, DynRef("a") - DynRef("b")],
        ])
        def test_sub(a, b, result):
            assert a - b == result
        
        test_sub(10, 3, 7)
        test_sub(20, 5, 15)


class TestDynRefComplexExpressions:
    """Test complex DynRef expressions."""
    
    def test_multiple_dynref_addition(self):
        """Test adding multiple DynRefs."""
        @parametrize_test("a, b, c, sum", [
            [1, 2, 3, DynRef("a") + DynRef("b") + DynRef("c")],
            [4, 5, 6, DynRef("a") + DynRef("b") + DynRef("c")],
        ])
        def test_sum(a, b, c, sum_val):
            assert a + b + c == sum_val
        
        test_sum(1, 2, 3, 6)
        test_sum(4, 5, 6, 15)
    
    def test_complex_expression(self):
        """Test complex DynRef expressions with multiple operations."""
        @parametrize_test("x, y, z, result", [
            [2, 3, 4, (DynRef("x") + DynRef("y")) * DynRef("z")],
            [5, 6, 7, (DynRef("x") + DynRef("y")) * DynRef("z")],
        ])
        def test_complex(x, y, z, result):
            assert (x + y) * z == result
        
        test_complex(2, 3, 4, 20)
        test_complex(5, 6, 7, 77)


class TestDynRefWithGenerators:
    """Test DynRef used with generators."""
    
    def test_dynref_with_generator(self):
        """Test DynRef with generator values."""
        @param_generator
        def generate_base_values():
            """Generate base values."""
            for i in range(1, 4):
                yield i
        
        @parametrize_test("base, multiplier, result", [
            [generate_base_values, 2, DynRef("base") * DynRef("multiplier")],
            [generate_base_values, 3, DynRef("base") * DynRef("multiplier")],
        ])
        def test_calc(base, multiplier, result):
            assert base * multiplier == result
        
        for base in range(1, 4):
            for multiplier in [2, 3]:
                test_calc(base, multiplier, base * multiplier)


class TestDependencyChains:
    """Test dependency chains and ordering."""
    
    def test_dependency_chain(self):
        """Test chain of dependencies."""
        @param_generator
        def generate_start():
            """Generate starting value."""
            yield 1
            yield 2
            yield 3
        
        @param_generator
        def generate_middle(start):
            """Generate middle value based on start."""
            yield start * 2
            yield start * 3
        
        @param_generator
        def generate_end(middle):
            """Generate end value based on middle."""
            yield middle + 10
            yield middle + 20
        
        @parametrize_test("start", generate_start)
        @parametrize_test("middle", generate_middle)
        @parametrize_test("end", generate_end)
        def test_chain(start, middle, end):
            assert middle > start
            assert end > middle
            assert end == middle + 10 or end == middle + 20
        
        for start in [1, 2, 3]:
            for middle in [start * 2, start * 3]:
                for end in [middle + 10, middle + 20]:
                    test_chain(start, middle, end)


class TestDynRefDivision:
    """Test DynRef division operations."""
    
    def test_dynref_division(self):
        """Test DynRef division operation."""
        @parametrize_test("numerator, denominator, quotient", [
            [10, 2, DynRef("numerator") / DynRef("denominator")],
            [15, 3, DynRef("numerator") / DynRef("denominator")],
            [20, 4, DynRef("numerator") / DynRef("denominator")],
        ])
        def test_div(numerator, denominator, quotient):
            assert numerator / denominator == quotient
        
        test_div(10, 2, 5.0)
        test_div(15, 3, 5.0)
        test_div(20, 4, 5.0)
    
    def test_dynref_modulo(self):
        """Test DynRef modulo operation."""
        @parametrize_test("numerator, denominator", [
            [10, 3],
            [15, 4],
            [20, 6],
        ])
        def test_mod(numerator, denominator):
            remainder = numerator % denominator
            assert remainder == numerator % denominator
        
        test_mod(10, 3)
        test_mod(15, 4)
        test_mod(20, 6)
