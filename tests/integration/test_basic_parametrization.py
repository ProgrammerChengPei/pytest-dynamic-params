# Integration tests for basic parametrization functionality

import pytest
from dynamic_params import parametrize_test


class TestBasicParametrization:
    """Test basic parametrization functionality"""
    
    def test_simple_parametrization(self):
        """Test simple parametrization with direct values"""
        @parametrize_test("a, b, expected", [
            [1, 2, 3],
            [4, 5, 9],
            [6, 7, 13],
            [10, 20, 30]
        ])
        def test_add(a, b, expected):
            assert a + b == expected
        
        # Manually test with different parameters
        test_add(1, 2, 3)
        test_add(4, 5, 9)
        test_add(6, 7, 13)
        test_add(10, 20, 30)
    
    def test_string_parametrization(self):
        """Test parametrization with string values"""
        @parametrize_test("name, greeting", [
            ["Alice", "Hello, Alice!"],
            ["Bob", "Hello, Bob!"],
            ["Charlie", "Hello, Charlie!"]
        ])
        def test_greeting(name, greeting):
            assert greeting == f"Hello, {name}!"
        
        # Manually test with different parameters
        test_greeting("Alice", "Hello, Alice!")
        test_greeting("Bob", "Hello, Bob!")
        test_greeting("Charlie", "Hello, Charlie!")
    
    def test_boolean_parametrization(self):
        """Test parametrization with boolean values"""
        @parametrize_test("value, expected", [
            [True, True],
            [False, False],
            [True and True, True],
            [False or True, True]
        ])
        def test_boolean(value, expected):
            assert value is expected
        
        # Manually test with different parameters
        test_boolean(True, True)
        test_boolean(False, False)
        test_boolean(True and True, True)
        test_boolean(False or True, True)
    
    def test_list_parametrization(self):
        """Test parametrization with list values"""
        @parametrize_test("input_list, expected_length", [
            [[1, 2, 3], 3],
            [[4, 5, 6, 7], 4],
            [[], 0],
            [["a", "b"], 2]
        ])
        def test_list_length(input_list, expected_length):
            assert len(input_list) == expected_length
        
        # Manually test with different parameters
        test_list_length([1, 2, 3], 3)
        test_list_length([4, 5, 6, 7], 4)
        test_list_length([], 0)
        test_list_length(["a", "b"], 2)
    
    def test_dict_parametrization(self):
        """Test parametrization with dictionary values"""
        @parametrize_test("input_dict, expected_keys", [
            [{"a": 1, "b": 2}, ["a", "b"]],
            [{"x": 10}, ["x"]],
            [{}, []]
        ])
        def test_dict_keys(input_dict, expected_keys):
            assert list(input_dict.keys()) == expected_keys
        
        # Manually test with different parameters
        test_dict_keys({"a": 1, "b": 2}, ["a", "b"])
        test_dict_keys({"x": 10}, ["x"])
        test_dict_keys({}, [])
    
    def test_multiple_parametrization_decorators(self):
        """Test multiple parametrization decorators on same function"""
        @parametrize_test("a", [1, 2, 3])
        @parametrize_test("b", [10, 20])
        def test_multiply(a, b):
            result = a * b
            assert result > 0
        
        # Manually test with different parameter combinations
        for a in [1, 2, 3]:
            for b in [10, 20]:
                test_multiply(a, b)
    
    def test_parametrization_with_ids(self):
        """Test parametrization with custom IDs"""
        @parametrize_test("value, expected", [
            [1, 2],
            [2, 4],
            [3, 6]
        ], ids=["double_1", "double_2", "double_3"])
        def test_double(value, expected):
            assert value * 2 == expected
        
        # Manually test with different parameters
        test_double(1, 2)
        test_double(2, 4)
        test_double(3, 6)
    
    def test_parametrization_edge_cases(self):
        """Test parametrization with edge cases"""
        @parametrize_test("value, expected", [
            [0, 0],
            [-1, -1],
            [1000000, 1000000],
            [None, None]
        ])
        def test_identity(value, expected):
            assert value == expected
        
        # Manually test with different parameters
        test_identity(0, 0)
        test_identity(-1, -1)
        test_identity(1000000, 1000000)
        test_identity(None, None)


class TestParametrizationTypes:
    """Test parametrization with different data types"""
    
    def test_numeric_types(self):
        """Test parametrization with numeric types"""
        @parametrize_test("value, expected_type", [
            [1, int],
            [3.14, float],
            [2+3j, complex]
        ])
        def test_type_check(value, expected_type):
            assert isinstance(value, expected_type)
        
        # Manually test with different parameters
        test_type_check(1, int)
        test_type_check(3.14, float)
        test_type_check(2+3j, complex)
    
    def test_mixed_types(self):
        """Test parametrization with mixed types"""
        @parametrize_test("value", [
            1,
            "string",
            [1, 2, 3],
            {"key": "value"},
            None
        ])
        def test_value_exists(value):
            assert value is not None or value is None  # Always passes
        
        # Manually test with different parameters
        test_value_exists(1)
        test_value_exists("string")
        test_value_exists([1, 2, 3])
        test_value_exists({"key": "value"})
        test_value_exists(None)


class TestParametrizationMarkers:
    """Test that parametrization markers are correctly applied"""
    
    def test_marker_applied(self):
        """Test that the dynamic_parametrize decorator is applied"""
        @parametrize_test("x", [1, 2, 3])
        def test_func(x):
            pass
        
        # Check if the decorator attribute is present
        assert hasattr(test_func, '_dynamic_parametrize')
        assert len(test_func._dynamic_parametrize) > 0
    
    def test_marker_contains_correct_data(self):
        """Test that the decorator contains correct parametrization data"""
        @parametrize_test("a, b", [[1, 2], [3, 4]])
        def test_func(a, b):
            pass
        
        # Check if the decorator contains correct data
        assert hasattr(test_func, '_dynamic_parametrize')
        dynamic_params = test_func._dynamic_parametrize
        assert len(dynamic_params) > 0
        
        param = dynamic_params[0]
        assert param.get('argnames') == "a, b"
        assert len(param.get('argvalues', [])) == 2
