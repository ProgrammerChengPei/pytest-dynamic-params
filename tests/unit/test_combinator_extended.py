# Test combinator module comprehensively - CORRECTED VERSION

import pytest
from dynamic_params.engine.parametrize.combinator import ParametrizeCombinator


class TestParametrizeCombinatorExtended:
    """Extended tests for ParametrizeCombinator"""
    
    def test_combine_empty_list(self):
        """Test combine with empty list"""
        combinator = ParametrizeCombinator()
        result = combinator.combine([])
        assert result == []
    
    def test_combine_single_parametrization(self):
        """Test combine with single parametrization"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": [[1], [2], [3]]}
        ]
        result = combinator.combine(parametrizations)
        # 单个 parametrization 会被 flatten，所以结果是 [[1], [2], [3]]
        assert len(result) == 3
        assert [1] in result
        assert [2] in result
        assert [3] in result
    
    def test_combine_multiple_parametrizations(self):
        """Test combine with multiple parametrizations"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": [[1], [2]]},
            {"argnames": "y", "argvalues": [["a"], ["b"]]}
        ]
        result = combinator.combine(parametrizations)
        # 多个 parametrizations 不会 flatten
        assert len(result) == 4
        assert [[1], ["a"]] in result
        assert [[1], ["b"]] in result
        assert [[2], ["a"]] in result
        assert [[2], ["b"]] in result
    
    def test_combine_with_non_list_argvalues(self):
        """Test combine with non-list argvalues (should be wrapped)"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": [1, 2, 3]}  # Not wrapped in lists
        ]
        result = combinator.combine(parametrizations)
        # Non-list values are now used directly
        assert len(result) == 3
        assert 1 in result
        assert 2 in result
        assert 3 in result
    
    def test_generate_cartesian_product_empty(self):
        """Test generate_cartesian_product with empty input"""
        combinator = ParametrizeCombinator()
        result = combinator.generate_cartesian_product([])
        assert result == []
    
    def test_generate_cartesian_product_single_list(self):
        """Test generate_cartesian_product with single list"""
        combinator = ParametrizeCombinator()
        param_values_list = [[[1], [2], [3]]]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 3
        assert [1] in result
        assert [2] in result
        assert [3] in result
    
    def test_generate_cartesian_product_multiple_lists(self):
        """Test generate_cartesian_product with multiple lists"""
        combinator = ParametrizeCombinator()
        param_values_list = [
            [[1], [2]],
            [["a"], ["b"]],
            [[True], [False]]
        ]
        result = combinator.generate_cartesian_product(param_values_list)
        # 2 * 2 * 2 = 8 combinations
        assert len(result) == 8
        assert [[1], ["a"], [True]] in result
        assert [[1], ["a"], [False]] in result
        assert [[2], ["b"], [False]] in result
    
    def test_generate_cartesian_product_with_complex_values(self):
        """Test generate_cartesian_product with complex values"""
        combinator = ParametrizeCombinator()
        param_values_list = [
            [[{"key": "value1"}], [{"key": "value2"}]],
            [[[1, 2, 3]], [[4, 5, 6]]]
        ]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 4
        assert [[{"key": "value1"}], [[1, 2, 3]]] in result
        assert [[{"key": "value2"}], [[4, 5, 6]]] in result
    
    def test_filter_combinations_basic(self):
        """Test filter_combinations with basic filter function"""
        combinator = ParametrizeCombinator()
        combinations = [[1, "a"], [1, "b"], [2, "a"], [2, "b"]]
        
        # Filter to keep only combinations where first element is 1
        filtered = combinator.filter_combinations(
            combinations,
            lambda comb: comb[0] == 1
        )
        
        assert len(filtered) == 2
        assert [1, "a"] in filtered
        assert [1, "b"] in filtered
        assert [2, "a"] not in filtered
        assert [2, "b"] not in filtered
    
    def test_filter_combinations_complex_filter(self):
        """Test filter_combinations with complex filter function"""
        combinator = ParametrizeCombinator()
        combinations = [[1, 2], [2, 4], [3, 6], [4, 8]]
        
        # Filter to keep only combinations where sum > 5
        filtered = combinator.filter_combinations(
            combinations,
            lambda comb: sum(comb) > 5
        )
        
        # 2+4=6, 3+6=9, 4+8=12 are all > 5
        assert len(filtered) == 3
        assert [2, 4] in filtered
        assert [3, 6] in filtered
        assert [4, 8] in filtered
    
    def test_filter_combinations_empty_input(self):
        """Test filter_combinations with empty input"""
        combinator = ParametrizeCombinator()
        combinations = []
        filtered = combinator.filter_combinations(
            combinations,
            lambda comb: comb[0] == 1
        )
        assert filtered == []
    
    def test_filter_combinations_all_filtered(self):
        """Test filter_combinations where all are filtered out"""
        combinator = ParametrizeCombinator()
        combinations = [[1, 2], [3, 4], [5, 6]]
        filtered = combinator.filter_combinations(
            combinations,
            lambda comb: comb[0] > 10
        )
        assert filtered == []
    
    def test_combine_with_mixed_argvalue_types(self):
        """Test combine with mixed argvalue types"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": [[1], [2]]},
            {"argnames": "y", "argvalues": [[3.14], [2.71]]},
            {"argnames": "z", "argvalues": [["a"], ["b"]]}
        ]
        result = combinator.combine(parametrizations)
        assert len(result) == 8  # 2 * 2 * 2
        assert [[1], [3.14], ["a"]] in result
        assert [[2], [2.71], ["b"]] in result


class TestParametrizeCombinatorEdgeCases:
    """Edge case tests for ParametrizeCombinator"""
    
    def test_combine_with_none_values(self):
        """Test combine with None values"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": [[None], [1]]}
        ]
        result = combinator.combine(parametrizations)
        assert len(result) == 2
        assert [None] in result
        assert [1] in result
    
    def test_combine_with_empty_argvalues(self):
        """Test combine with empty argvalues"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": []}
        ]
        result = combinator.combine(parametrizations)
        assert result == []
    
    def test_generate_cartesian_product_with_single_element_lists(self):
        """Test generate_cartesian_product with single element lists"""
        combinator = ParametrizeCombinator()
        param_values_list = [[[1]], [[2]], [[3]]]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 1
        assert result[0] == [[1], [2], [3]]
    
    def test_filter_combinations_preserves_order(self):
        """Test filter_combinations preserves original order"""
        combinator = ParametrizeCombinator()
        combinations = [[1], [2], [3], [4], [5]]
        filtered = combinator.filter_combinations(
            combinations,
            lambda comb: comb[0] % 2 == 1
        )
        assert filtered == [[1], [3], [5]]
    
    def test_combine_single_parametrization_empty_argvalues(self):
        """Test combine with single parametrization having empty argvalues"""
        combinator = ParametrizeCombinator()
        parametrizations = [
            {"argnames": "x", "argvalues": []}
        ]
        result = combinator.combine(parametrizations)
        assert result == []
    
    def test_generate_cartesian_product_with_nested_lists(self):
        """Test generate_cartesian_product with nested lists"""
        combinator = ParametrizeCombinator()
        param_values_list = [
            [[[1, 2]], [[3, 4]]],
            [[[5, 6]], [[7, 8]]]
        ]
        result = combinator.generate_cartesian_product(param_values_list)
        assert len(result) == 4
        assert [[[1, 2]], [[5, 6]]] in result
        assert [[[3, 4]], [[7, 8]]] in result
