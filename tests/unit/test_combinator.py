# Test ParametrizeCombinator functionality

import pytest
from dynamic_params.engine.parametrize.combinator import ParametrizeCombinator


class TestParametrizeCombinator:
    """Test ParametrizeCombinator class"""
    
    def test_combinator_init(self):
        """Test ParametrizeCombinator initialization"""
        combinator = ParametrizeCombinator()
        assert combinator is not None
    
    def test_combine_single_parametrization(self):
        """Test combine with single parametrization"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {
                "argnames": ["a"],
                "argvalues": [[1], [2], [3]]
            }
        ]
        result = combinator.combine(parametrizations)
        assert len(result) == 3
        assert [1] in result
        assert [2] in result
        assert [3] in result
    
    def test_combine_multiple_parametrizations(self):
        """Test combine with multiple parametrizations"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {
                "argnames": ["a"],
                "argvalues": [[1], [2]]
            },
            {
                "argnames": ["b"],
                "argvalues": [[3], [4]]
            }
        ]
        result = combinator.combine(parametrizations)
        assert len(result) == 4
        assert [[1], [3]] in result
        assert [[1], [4]] in result
        assert [[2], [3]] in result
        assert [[2], [4]] in result
    
    def test_combine_empty_parametrizations(self):
        """Test combine with empty parametrizations"""
        combinator = ParametrizeCombinator()
        result = combinator.combine([])
        assert result == []
    
    def test_combine_empty_argvalues(self):
        """Test combine with empty argvalues"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {
                "argnames": ["a"],
                "argvalues": []
            }
        ]
        result = combinator.combine(parametrizations)
        assert result == []
    
    def test_generate_cartesian_product_simple(self):
        """Test generate_cartesian_product with simple values"""
        combinator = ParametrizeCombinator()
        param_values_list = [
            [[1], [2]],
            [[3], [4]]
        ]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 4
        assert [[1], [3]] in result
        assert [[1], [4]] in result
        assert [[2], [3]] in result
        assert [[2], [4]] in result
    
    def test_generate_cartesian_product_single_list(self):
        """Test generate_cartesian_product with single list"""
        combinator = ParametrizeCombinator()
        param_values_list = [
            [[1], [2], [3]]
        ]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 3
        assert [1] in result
        assert [2] in result
        assert [3] in result
    
    def test_generate_cartesian_product_empty(self):
        """Test generate_cartesian_product with empty list"""
        combinator = ParametrizeCombinator()
        result = combinator.generate_cartesian_product([])
        assert result == []
    
    def test_generate_cartesian_product_three_lists(self):
        """Test generate_cartesian_product with three lists"""
        combinator = ParametrizeCombinator()
        param_values_list = [
            [[1], [2]],
            [[3], [4]],
            [[5], [6]]
        ]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 8
    
    def test_filter_combinations(self):
        """Test filter_combinations"""
        combinator = ParametrizeCombinator()
        combinations = [[1, 2], [3, 4], [5, 6]]
        
        def filter_func(comb):
            return comb[0] > 2
        
        result = combinator.filter_combinations(combinations, filter_func)
        assert len(result) == 2
        assert [3, 4] in result
        assert [5, 6] in result
    
    def test_filter_combinations_all_pass(self):
        """Test filter_combinations where all pass"""
        combinator = ParametrizeCombinator()
        combinations = [[1, 2], [3, 4]]
        
        def filter_func(comb):
            return True
        
        result = combinator.filter_combinations(combinations, filter_func)
        assert len(result) == 2
    
    def test_filter_combinations_none_pass(self):
        """Test filter_combinations where none pass"""
        combinator = ParametrizeCombinator()
        combinations = [[1, 2], [3, 4]]
        
        def filter_func(comb):
            return False
        
        result = combinator.filter_combinations(combinations, filter_func)
        assert len(result) == 0
    
    def test_combine_with_non_list_values(self):
        """Test combine with non-list values"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {
                "argnames": ["a"],
                "argvalues": [1, 2, 3]
            }
        ]
        result = combinator.combine(parametrizations)
        assert len(result) == 3
        assert 1 in result
        assert 2 in result
        assert 3 in result
