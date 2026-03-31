# Parameter combinator implementation

from typing import List, Dict, Any, Callable
from itertools import product

class ParametrizeCombinator:
    """Class for combining parameters from multiple parametrizations"""
    
    def combine(self, parametrizations: List[Dict[str, Any]]) -> List[List[Any]]:
        """Combine multiple parametrizations
        
        Args:
            parametrizations: List of parametrization configurations
            
        Returns:
            List of parameter combinations
        """
        if not parametrizations:
            return []
        
        # Extract parameter values from each parametrization
        param_values_list = []
        for parametrization in parametrizations:
            argvalues = parametrization.get("argvalues", [])
            param_values_list.append(argvalues)
        
        # Generate Cartesian product of all parameter values
        combinations = self.generate_cartesian_product(param_values_list)
        
        return combinations
    
    def generate_cartesian_product(self, param_values_list: List[List[Any]]) -> List[List[Any]]:
        """Generate Cartesian product of parameter values
        
        Args:
            param_values_list: List of parameter values lists
            
        Returns:
            List of parameter combinations
        """
        if not param_values_list:
            return []
        
        # Use itertools.product to generate Cartesian product
        product_result = product(*param_values_list)
        
        # Convert tuples to lists, but unwrap single-element tuples
        combinations = []
        for combination in product_result:
            if len(combination) == 1:
                # Single parameter, use the value directly (not wrapped in list)
                combinations.append(combination[0])
            else:
                # Multiple parameters, convert to list
                combinations.append(list(combination))
        
        return combinations
    
    def filter_combinations(self, combinations: List[List[Any]], 
                          filter_func: Callable[[List[Any]], bool]) -> List[List[Any]]:
        """Filter parameter combinations
        
        Args:
            combinations: List of parameter combinations
            filter_func: Function to filter combinations
            
        Returns:
            Filtered list of parameter combinations
        """
        return [comb for comb in combinations if filter_func(comb)]
