"""
Basic parametrization functional tests.

Tests basic parameter generation and parametrization scenarios.
"""

import pytest
from dynamic_params import parametrize_test, param_generator


class TestBasicParametrization:
    """Test basic parametrization functionality."""
    
    def test_simple_addition(self):
        """Test simple addition with static parameters."""
        @parametrize_test("a, b, expected", [
            [1, 2, 3],
            [2, 3, 5],
            [3, 4, 7],
        ])
        def test_add(a, b, expected):
            assert a + b == expected
        
        test_add(1, 2, 3)
        test_add(2, 3, 5)
        test_add(3, 4, 7)
    
    def test_truthiness(self):
        """Test truthiness of values."""
        @parametrize_test("value, expected", [
            [1, True],
            [0, False],
            [2, True],
            [-1, True],
        ])
        def test_bool_check(value, expected):
            assert bool(value) == expected
        
        test_bool_check(1, True)
        test_bool_check(0, False)
        test_bool_check(2, True)
        test_bool_check(-1, True)
    
    def test_string_length(self):
        """Test string length calculation."""
        @parametrize_test("text, expected", [
            ["hello", 5],
            ["world", 5],
            ["", 0],
            ["python", 6],
        ])
        def test_len(text, expected):
            assert len(text) == expected
        
        test_len("hello", 5)
        test_len("world", 5)
        test_len("", 0)
        test_len("python", 6)


class TestGeneratorBasicUsage:
    """Test basic generator usage."""
    
    def test_generated_numbers(self):
        """Test that numbers are generated correctly."""
        @param_generator
        def generate_numbers():
            """Generate a sequence of numbers."""
            for i in range(1, 6):
                yield i
        
        @parametrize_test("number", generate_numbers)
        def test_num(number):
            assert isinstance(number, int)
            assert 1 <= number <= 5
        
        for i in range(1, 6):
            test_num(i)
    
    def test_even_numbers(self):
        """Test that even numbers are generated."""
        @param_generator
        def generate_even_numbers():
            """Generate even numbers."""
            for i in range(2, 11, 2):
                yield i
        
        @parametrize_test("even_num", generate_even_numbers)
        def test_even(even_num):
            assert even_num % 2 == 0
            assert 2 <= even_num <= 10
        
        for i in [2, 4, 6, 8, 10]:
            test_even(i)
    
    def test_data_generation(self):
        """Test dictionary data generation."""
        @param_generator
        def generate_test_data():
            """Generate test data dictionaries."""
            for i in range(3):
                yield {"id": i, "name": f"Item {i}"}
        
        @parametrize_test("data", generate_test_data)
        def test_data(data):
            assert "id" in data
            assert "name" in data
            assert isinstance(data["id"], int)
            assert isinstance(data["name"], str)
        
        for i in range(3):
            test_data({"id": i, "name": f"Item {i}"})


class TestMixedStaticAndDynamic:
    """Test mixing static and dynamic parameters."""
    
    def test_mixed_params(self):
        """Test mixing static base with dynamic multipliers."""
        @param_generator
        def generate_multipliers():
            """Generate multiplier values."""
            yield 2
            yield 3
            yield 4
        
        @parametrize_test("base", [1, 5, 10])
        @parametrize_test("multiplier", generate_multipliers)
        def test_multiply(base, multiplier):
            result = base * multiplier
            assert result % base == 0
        
        for base in [1, 5, 10]:
            for multiplier in [2, 3, 4]:
                test_multiply(base, multiplier)
    
    def test_multiple_decorators(self):
        """Test multiple parametrize_test decorators."""
        @param_generator
        def generate_multipliers():
            """Generate multiplier values."""
            yield 2
            yield 3
            yield 4
        
        @parametrize_test("x, y", [[1, 2], [3, 4]])
        @parametrize_test("z", generate_multipliers)
        def test_all(x, y, z):
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert isinstance(z, int)
            assert z in [2, 3, 4]
        
        for x, y in [[1, 2], [3, 4]]:
            for z in [2, 3, 4]:
                test_all(x, y, z)


class TestParameterTypes:
    """Test different parameter types."""
    
    def test_string_parameters(self):
        """Test string parameter generation."""
        @param_generator
        def generate_strings():
            """Generate string values."""
            yield "apple"
            yield "banana"
            yield "cherry"
        
        @parametrize_test("fruit", generate_strings)
        def test_fruit(fruit):
            assert isinstance(fruit, str)
            assert len(fruit) > 0
        
        for fruit in ["apple", "banana", "cherry"]:
            test_fruit(fruit)
    
    def test_list_parameters(self):
        """Test list parameter generation."""
        @param_generator
        def generate_lists():
            """Generate list values."""
            yield [1, 2, 3]
            yield [4, 5, 6]
            yield [7, 8, 9]
        
        @parametrize_test("numbers", generate_lists)
        def test_nums(numbers):
            assert isinstance(numbers, list)
            assert len(numbers) == 3
            assert all(isinstance(n, int) for n in numbers)
        
        for lst in [[1, 2, 3], [4, 5, 6], [7, 8, 9]]:
            test_nums(lst)
    
    def test_tuple_parameters(self):
        """Test tuple parameter generation."""
        @param_generator
        def generate_tuples():
            """Generate tuple values."""
            yield (1, "a")
            yield (2, "b")
            yield (3, "c")
        
        @parametrize_test("pair", generate_tuples)
        def test_pair(pair):
            assert isinstance(pair, tuple)
            assert len(pair) == 2
            assert isinstance(pair[0], int)
            assert isinstance(pair[1], str)
        
        for pair in [(1, "a"), (2, "b"), (3, "c")]:
            test_pair(pair)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_values(self):
        """Test empty value generation."""
        @param_generator
        def generate_empty():
            """Generate empty sequence."""
            yield []
            yield {}
            yield ""
        
        @parametrize_test("empty", generate_empty)
        def test_empty_check(empty):
            assert not empty or len(empty) == 0
        
        test_empty_check([])
        test_empty_check({})
        test_empty_check("")
    
    def test_large_numbers(self):
        """Test large number generation."""
        @param_generator
        def generate_large_numbers():
            """Generate large numbers."""
            yield 10**6
            yield 10**9
            yield 10**12
        
        @parametrize_test("big_num", generate_large_numbers)
        def test_large(big_num):
            assert isinstance(big_num, int)
            assert big_num >= 10**6
        
        for num in [10**6, 10**9, 10**12]:
            test_large(num)
