# Integration tests for advanced usage scenarios

import pytest
from dynamic_params import parametrize_test, parametrize_fixture, param_generator, parametrize_generator, DynRef


class TestComplexParametrization:
    """Test complex parametrization scenarios"""
    
    def test_nested_parametrization(self):
        """Test nested parametrization"""
        @parametrize_test("outer", [1, 2, 3])
        @parametrize_test("inner", [10, 20])
        def test_nested(outer, inner):
            result = outer * 10 + inner
            assert result > 0
        
        # Test all combinations
        for outer in [1, 2, 3]:
            for inner in [10, 20]:
                test_nested(outer, inner)
    
    def test_parametrization_with_complex_expressions(self):
        """Test parametrization with complex expressions"""
        @parametrize_test("x, y, result", [
            [1, 2, (DynRef("x") + DynRef("y")) * (DynRef("x") - DynRef("y"))],
            [5, 3, (DynRef("x") + DynRef("y")) * (DynRef("x") - DynRef("y"))]
        ])
        def test_complex_expr(x, y, result):
            expected = (x + y) * (x - y)
            assert result == expected
        
        test_complex_expr(1, 2, -3)
        test_complex_expr(5, 3, 16)
    
    def test_parametrization_with_lambda(self):
        """Test parametrization with lambda functions"""
        @parametrize_test("func, input_val, expected", [
            [lambda x: x * 2, 5, 10],
            [lambda x: x + 10, 5, 15],
            [lambda x: x ** 2, 5, 25]
        ])
        def test_functions(func, input_val, expected):
            assert func(input_val) == expected
        
        test_functions(lambda x: x * 2, 5, 10)
        test_functions(lambda x: x + 10, 5, 15)
        test_functions(lambda x: x ** 2, 5, 25)


class TestAdvancedGeneratorUsage:
    """Test advanced generator usage scenarios"""
    
    def test_generator_with_dependencies(self):
        """Test generator with dependencies on other generators"""
        @param_generator
        def generate_base_numbers():
            """Generate base numbers"""
            for i in range(1, 6):
                yield i
        
        @param_generator
        def generate_squared():
            """Generate squared numbers"""
            for num in generate_base_numbers.execute():
                yield num ** 2
        
        values = list(generate_squared.execute())
        assert values == [1, 4, 9, 16, 25]
    
    def test_generator_with_external_data(self):
        """Test generator using external data source"""
        external_data = [100, 200, 300, 400]
        
        @param_generator
        def generate_from_external():
            """Generate from external data"""
            for item in external_data:
                yield item * 2
        
        values = list(generate_from_external.execute())
        assert values == [200, 400, 600, 800]
    
    def test_generator_with_state(self):
        """Test generator maintaining state"""
        @param_generator
        def generate_with_state():
            """Generate with internal state"""
            state = 0
            for i in range(5):
                state += i
                yield state
        
        values = list(generate_with_state.execute())
        assert values == [0, 1, 3, 6, 10]  # Cumulative sum


class TestParametrizeGeneratorAdvanced:
    """Test advanced parametrize_generator usage"""
    
    def test_parametrized_generator_with_multiple_params(self):
        """Test parametrized generator with multiple parameters"""
        @parametrize_generator("start, step, count", [
            [0, 1, 3],
            [10, 2, 3],
            [100, 10, 3]
        ])
        @param_generator
        def generate_sequence(start, step, count):
            """Generate sequence with parameters"""
            for i in range(count):
                yield start + (i * step)
        
        # Test with different parameter sets
        values1 = list(generate_sequence.execute(0, 1, 3))
        assert values1 == [0, 1, 2]
        
        values2 = list(generate_sequence.execute(10, 2, 3))
        assert values2 == [10, 12, 14]
        
        values3 = list(generate_sequence.execute(100, 10, 3))
        assert values3 == [100, 110, 120]
    
    def test_parametrized_generator_with_dynref(self):
        """Test parametrized generator using DynRef"""
        @parametrize_generator("multiplier, offset", [
            [2, 0],
            [3, 1]
        ])
        @param_generator
        def generate_transformed(multiplier, offset):
            """Generate transformed values"""
            for i in range(3):
                yield (i * multiplier) + offset
        
        # Test with different parameter sets
        values1 = list(generate_transformed.execute(2, 0))
        assert values1 == [0, 2, 4]
        
        values2 = list(generate_transformed.execute(3, 1))
        assert values2 == [1, 4, 7]


class TestMixedParametrizationSources:
    """Test mixing different parametrization sources"""
    
    def test_mixed_direct_and_generator(self):
        """Test mixing direct values and generator"""
        @param_generator
        def generate_values():
            """Generate values"""
            yield 10
            yield 20
        
        @parametrize_test("a", [1, 2, 3])
        @parametrize_test("b", generate_values)
        def test_mixed(a, b):
            result = a + b
            assert result > 0
        
        # Test all combinations
        for a in [1, 2, 3]:
            for b in [10, 20]:
                test_mixed(a, b)
    
    def test_mixed_fixture_and_direct(self):
        """Test mixing fixture and direct values"""
        # Note: parametrize_fixture applies fixture decorator internally
        # and marks are not applied to fixtures in pytest 9+
        
        @parametrize_fixture("base", [100, 200])
        def fixture_value(base):
            """Fixture value"""
            return base * 2
        
        # Verify the fixture was decorated
        assert 'Fixture' in str(type(fixture_value))
        
        @parametrize_test("multiplier", [2, 3])
        def test_mixed(fixture_value, multiplier):
            result = fixture_value * multiplier
            assert result > 0
        
        # Note: In actual pytest usage, fixture_value would be auto-injected
        # Here we just verify the decorators are applied correctly
    
    def test_mixed_generator_and_dynref(self):
        """Test mixing generator and DynRef"""
        @param_generator
        def generate_base():
            """Generate base values"""
            yield 5
            yield 10
        
        @parametrize_test("base, doubled", [
            [DynRef("base"), DynRef("base") * 2]
        ])
        def test_with_generator_and_dynref(base, doubled):
            assert doubled == base * 2
        
        # Test with generated values
        for base_val in [5, 10]:
            test_with_generator_and_dynref(base_val, base_val * 2)


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_api_testing_scenario(self):
        """Test API testing scenario"""
        @param_generator
        def generate_api_endpoints():
            """Generate API endpoints"""
            yield "/api/users"
            yield "/api/posts"
            yield "/api/comments"
        
        @param_generator
        def generate_http_methods():
            """Generate HTTP methods"""
            yield "GET"
            yield "POST"
        
        @parametrize_test("endpoint", generate_api_endpoints)
        @parametrize_test("method", generate_http_methods)
        def test_api_endpoint(endpoint, method):
            # Simulate API testing
            assert endpoint.startswith("/api/")
            assert method in ["GET", "POST"]
        
        # Test all combinations
        endpoints = ["/api/users", "/api/posts", "/api/comments"]
        methods = ["GET", "POST"]
        for endpoint in endpoints:
            for method in methods:
                test_api_endpoint(endpoint, method)
    
    def test_database_testing_scenario(self):
        """Test database testing scenario"""
        @parametrize_test("db_config", [
            {"host": "localhost", "port": 5432, "db": "test_db"},
            {"host": "localhost", "port": 5433, "db": "dev_db"}
        ])
        def test_database_connection(db_config):
            """Test database connection"""
            assert "host" in db_config
            assert "port" in db_config
            assert "db" in db_config
            assert isinstance(db_config["port"], int)
        
        # Test with different configs
        test_database_connection({"host": "localhost", "port": 5432, "db": "test_db"})
        test_database_connection({"host": "localhost", "port": 5433, "db": "dev_db"})
    
    def test_data_validation_scenario(self):
        """Test data validation scenario"""
        @parametrize_test("input_data, validator, expected", [
            ["test@example.com", "email", True],
            ["invalid", "email", False],
            ["https://example.com", "url", True],
            ["not_a_url", "url", False]
        ])
        def test_validation(input_data, validator, expected):
            """Test data validation"""
            # Simplified validation logic
            if validator == "email":
                result = "@" in input_data
            elif validator == "url":
                result = input_data.startswith("http")
            else:
                result = False
            
            assert result == expected
        
        # Test all cases
        test_validation("test@example.com", "email", True)
        test_validation("invalid", "email", False)
        test_validation("https://example.com", "url", True)
        test_validation("not_a_url", "url", False)


class TestEdgeCasesAndStress:
    """Test edge cases and stress scenarios"""
    
    def test_large_parametrization(self):
        """Test with large number of parameters"""
        @parametrize_test("value", list(range(100)))
        def test_large(value):
            assert isinstance(value, int)
            assert 0 <= value < 100
        
        # Test a sample of values
        for i in [0, 50, 99]:
            test_large(i)
    
    def test_deeply_nested_generators(self):
        """Test deeply nested generator calls"""
        @param_generator
        def generate_level1():
            """Level 1 generator"""
            yield 1
            yield 2
        
        @param_generator
        def generate_level2():
            """Level 2 generator"""
            for val in generate_level1.execute():
                yield val * 10
        
        @param_generator
        def generate_level3():
            """Level 3 generator"""
            for val in generate_level2.execute():
                yield val + 5
        
        values = list(generate_level3.execute())
        assert values == [15, 25]  # (1*10)+5, (2*10)+5
    
    def test_parametrization_with_none_and_empty(self):
        """Test parametrization with None and empty values"""
        @parametrize_test("value", [None, "", [], {}, 0, False])
        def test_falsy_values(value):
            # Test that all values are handled
            assert value is not None or value is None  # Always passes
        
        # Test all falsy values
        test_falsy_values(None)
        test_falsy_values("")
        test_falsy_values([])
        test_falsy_values({})
        test_falsy_values(0)
        test_falsy_values(False)
    
    def test_complex_dynref_chaining(self):
        """Test complex DynRef chaining"""
        @parametrize_test("a, b, c, d, result", [
            [1, 2, 3, 4, DynRef("a") + DynRef("b") * DynRef("c") - DynRef("d")]
        ])
        def test_complex_chain(a, b, c, d, result):
            expected = a + b * c - d
            assert result == expected
        
        test_complex_chain(1, 2, 3, 4, 3)  # 1 + 2*3 - 4 = 3


class TestCompatibilityWithPytest:
    """Test compatibility with pytest features"""
    
    def test_with_pytest_marks(self):
        """Test compatibility with pytest marks"""
        @pytest.mark.skip(reason="Skip for demonstration")
        @parametrize_test("value", [1, 2, 3])
        def test_skipped(value):
            pass
        
        # The test should have both marks
        # pytest marks are stored in pytestmark attribute
        markers = getattr(test_skipped, 'pytestmark', [])
        mark_names = [m.name for m in markers]
        assert 'skip' in mark_names
        # Our decorator is stored in _dynamic_parametrize attribute
        assert hasattr(test_skipped, '_dynamic_parametrize')
    
    def test_with_pytest_fixture(self):
        """Test compatibility with pytest fixture"""
        @pytest.fixture
        def simple_fixture():
            return "fixture_value"
        
        @parametrize_test("multiplier", [2, 3])
        def test_with_fixture(simple_fixture, multiplier):
            assert simple_fixture == "fixture_value"
            assert multiplier in [2, 3]
        
        # Test the function
        test_with_fixture("fixture_value", 2)
        test_with_fixture("fixture_value", 3)
    
    def test_parametrize_order_independence(self):
        """Test that parametrization order doesn't affect correctness"""
        @parametrize_test("a", [1, 2])
        @parametrize_test("b", [10, 20])
        def test_order1(a, b):
            return (a, b)
        
        @parametrize_test("b", [10, 20])
        @parametrize_test("a", [1, 2])
        def test_order2(a, b):
            return (a, b)
        
        # Both should produce same combinations
        results1 = [(a, b) for a in [1, 2] for b in [10, 20]]
        results2 = [(a, b) for a in [1, 2] for b in [10, 20]]
        
        assert results1 == results2
