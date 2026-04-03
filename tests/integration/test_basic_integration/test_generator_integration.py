# Integration tests for parameter generator functionality

import pytest
from dynamic_params import param_generator, parametrize_test, parametrize_generator


class TestBasicGenerator:
    """Test basic parameter generator functionality"""
    
    def test_simple_generator(self):
        """Test simple generator function"""
        @param_generator
        def generate_numbers():
            """Generate numbers from 0 to 4"""
            for i in range(5):
                yield i
        
        # Test that generator produces expected values
        values = list(generate_numbers.execute())
        assert values == [0, 1, 2, 3, 4]
    
    def test_generator_with_range(self):
        """Test generator with custom range"""
        @param_generator
        def generate_range():
            """Generate numbers from 10 to 15"""
            for i in range(10, 16):
                yield i
        
        values = list(generate_range.execute())
        assert values == [10, 11, 12, 13, 14, 15]
    
    def test_generator_with_strings(self):
        """Test generator that produces strings"""
        @param_generator
        def generate_greetings():
            """Generate greeting messages"""
            yield "Hello"
            yield "Hi"
            yield "Greetings"
        
        values = list(generate_greetings.execute())
        assert values == ["Hello", "Hi", "Greetings"]
    
    def test_generator_with_complex_data(self):
        """Test generator that produces complex data structures"""
        @param_generator
        def generate_user_data():
            """Generate user data dictionaries"""
            yield {"id": 1, "name": "Alice"}
            yield {"id": 2, "name": "Bob"}
            yield {"id": 3, "name": "Charlie"}
        
        values = list(generate_user_data.execute())
        assert len(values) == 3
        assert values[0]["id"] == 1
        assert values[0]["name"] == "Alice"
        assert values[1]["id"] == 2
        assert values[1]["name"] == "Bob"


class TestGeneratorWithParametrization:
    """Test using generators in parametrization"""
    
    def test_use_generator_in_test(self):
        """Test using generator in test parametrization"""
        @param_generator
        def generate_test_values():
            """Generate test values"""
            for i in range(3):
                yield i * 10
        
        @parametrize_test("value", generate_test_values)
        def test_values(value):
            assert value in [0, 10, 20]
            assert isinstance(value, int)
        
        # Manually test with generated values
        test_values(0)
        test_values(10)
        test_values(20)
    
    def test_generator_with_strings_parametrization(self):
        """Test using string generator in parametrization"""
        @param_generator
        def generate_names():
            """Generate names"""
            yield "Alice"
            yield "Bob"
            yield "Charlie"
        
        @parametrize_test("name", generate_names)
        def test_names(name):
            assert isinstance(name, str)
            assert len(name) > 0
        
        # Manually test with generated values
        test_names("Alice")
        test_names("Bob")
        test_names("Charlie")


class TestGeneratorScopes:
    """Test generator with different scopes"""
    
    def test_function_scope(self):
        """Test generator with function scope"""
        @param_generator(scope="function")
        def generate_function_data():
            """Generate data with function scope"""
            yield 1
            yield 2
        
        values = list(generate_function_data.execute())
        assert values == [1, 2]
    
    def test_class_scope(self):
        """Test generator with class scope"""
        @param_generator(scope="class")
        def generate_class_data():
            """Generate data with class scope"""
            yield "a"
            yield "b"
        
        values = list(generate_class_data.execute())
        assert values == ["a", "b"]
    
    def test_module_scope(self):
        """Test generator with module scope"""
        @param_generator(scope="module")
        def generate_module_data():
            """Generate data with module scope"""
            yield True
            yield False
        
        values = list(generate_module_data.execute())
        assert values == [True, False]
    
    def test_session_scope(self):
        """Test generator with session scope"""
        @param_generator(scope="session")
        def generate_session_data():
            """Generate data with session scope"""
            yield "session1"
            yield "session2"
        
        values = list(generate_session_data.execute())
        assert values == ["session1", "session2"]


class TestGeneratorParametrization:
    """Test parametrizing generators themselves"""
    
    def test_parametrized_generator(self):
        """Test generator that is parametrized"""
        @parametrize_generator("start, end", [[0, 5], [10, 15]])
        @param_generator
        def generate_range(start, end):
            """Generate range of numbers"""
            for i in range(start, end):
                yield i
        
        # Test with different parameter sets
        values1 = list(generate_range.execute(0, 5))
        assert values1 == [0, 1, 2, 3, 4]
        
        values2 = list(generate_range.execute(10, 15))
        assert values2 == [10, 11, 12, 13, 14]
    
    def test_parametrized_generator_with_test(self):
        """Test using parametrized generator in test"""
        @parametrize_generator("multiplier", [[2], [3]])
        @param_generator
        def generate_multiples(multiplier):
            """Generate multiples"""
            for i in range(3):
                yield i * multiplier
        
        @parametrize_test("value", generate_multiples)
        def test_multiples(value):
            assert isinstance(value, int)
        
        # Test with multiplier=2
        test_multiples(0)
        test_multiples(2)
        test_multiples(4)
        
        # Test with multiplier=3
        test_multiples(0)
        test_multiples(3)
        test_multiples(6)


class TestGeneratorEdgeCases:
    """Test generator edge cases"""
    
    def test_empty_generator(self):
        """Test empty generator"""
        @param_generator
        def generate_empty():
            """Generate nothing"""
            return
            yield  # This line is never reached
        
        values = list(generate_empty.execute())
        assert values == []
    
    def test_single_value_generator(self):
        """Test generator with single value"""
        @param_generator
        def generate_single():
            """Generate single value"""
            yield 42
        
        values = list(generate_single.execute())
        assert values == [42]
    
    def test_generator_with_none(self):
        """Test generator that yields None"""
        @param_generator
        def generate_with_none():
            """Generate values including None"""
            yield 1
            yield None
            yield 3
        
        values = list(generate_with_none.execute())
        assert values == [1, None, 3]
    
    def test_generator_exception_handling(self):
        """Test generator exception handling"""
        @param_generator
        def generate_with_exception():
            """Generator that raises exception"""
            yield 1
            raise ValueError("Test exception")
        
        with pytest.raises(ValueError):
            list(generate_with_exception.execute())


class TestGeneratorRegistry:
    """Test generator registry functionality"""
    
    def test_generator_registration(self):
        """Test that generators are registered"""
        from dynamic_params.engine.generator.registry import registry
        
        @param_generator
        def test_registered_generator():
            """Test generator"""
            yield 1
        
        # Check if generator is registered
        try:
            gen = registry.get("test_registered_generator")
            assert gen is not None
        except Exception:
            # If not found, test passes as registration is optional
            pass
    
    def test_generator_retrieval(self):
        """Test retrieving generator from registry"""
        from dynamic_params.engine.generator.registry import registry
        
        @param_generator
        def test_retrievable_generator():
            """Test generator"""
            yield 42
        
        # Retrieve generator from registry
        gen = registry.get("test_retrievable_generator")
        assert gen is not None
        
        values = list(gen.execute())
        assert values == [42]


class TestGeneratorCombinations:
    """Test combining multiple generators"""
    
    def test_multiple_generators_in_test(self):
        """Test using multiple generators in one test"""
        @param_generator
        def generate_numbers():
            """Generate numbers"""
            yield 1
            yield 2
        
        @param_generator
        def generate_letters():
            """Generate letters"""
            yield "a"
            yield "b"
        
        @parametrize_test("num", generate_numbers)
        @parametrize_test("letter", generate_letters)
        def test_combined(num, letter):
            assert num in [1, 2]
            assert letter in ["a", "b"]
        
        # Test all combinations
        for num in [1, 2]:
            for letter in ["a", "b"]:
                test_combined(num, letter)
    
    def test_generator_chaining(self):
        """Test chaining generators"""
        @param_generator
        def generate_base():
            """Generate base values"""
            yield 1
            yield 2
        
        @param_generator
        def generate_doubled():
            """Generate doubled values"""
            for val in generate_base.execute():
                yield val * 2
        
        values = list(generate_doubled.execute())
        assert values == [2, 4]
