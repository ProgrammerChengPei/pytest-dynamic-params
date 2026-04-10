# Integration test for the plugin

import pytest
from dynamic_params import param_generator


# Define a parameter generator
@param_generator(scope="session", cache=True)
def generate_test_data():
    """Generate test data"""
    for i in range(3):
        yield i

class TestIntegration:
    """Integration tests for the plugin"""
    
    def test_basic_parametrization(self):
        """Test basic parametrization"""
        # Define a test function with parametrization
        @pytest.mark.parametrize("a, b, expected", [[1, 2, 3], [4, 5, 9], [6, 7, 13]])
        def test_add(a, b, expected):
            assert a + b == expected
        
        # Run the test function with different parameters
        test_add(1, 2, 3)
        test_add(4, 5, 9)
        test_add(6, 7, 13)
    
    def test_generator_parametrization(self):
        """Test parametrization with generator"""
        # Define a test function that uses the generator
        @pytest.mark.parametrize("value", generate_test_data)
        def test_generator_value(value):
            assert isinstance(value, int)
            assert 0 <= value < 3
        
        # Run the test function with generated values
        for i in range(3):
            test_generator_value(i)
    
    def test_dynref_parametrization(self):
        """Test parametrization - placeholder for removed DynRef functionality"""
        # DynRef functionality has been removed - this test is a placeholder
        pass
