"""
Fixture integration functional tests.

Tests integration between dynamic parameters and pytest fixtures.
"""

import pytest
from dynamic_params import parametrize_test, parametrize_fixture, param_generator, DynRef


class TestFixtureParametrization:
    """Test fixture parametrization."""
    
    def test_user_fixture(self):
        """Test user fixture with parametrization."""
        @param_generator
        def generate_user_ids():
            """Generate user IDs."""
            for i in range(1, 4):
                yield i
        
        @parametrize_fixture("user_id", generate_user_ids)
        def user(user_id):
            return {"id": user_id, "name": f"User {user_id}"}
        
        for i in range(1, 4):
            user_data = {"id": i, "name": f"User {i}"}
            assert "id" in user_data
            assert "name" in user_data
            assert user_data["id"] in [1, 2, 3]
    
    def test_config_fixture(self):
        """Test config fixture with parametrization."""
        @param_generator
        def generate_config_values():
            """Generate configuration values."""
            yield {"timeout": 10}
            yield {"timeout": 20}
            yield {"timeout": 30}
        
        @parametrize_fixture("config", generate_config_values)
        def app_config(config):
            return {"app": "test", **config}
        
        for timeout in [10, 20, 30]:
            cfg = {"app": "test", "timeout": timeout}
            assert cfg["app"] == "test"
            assert cfg["timeout"] in [10, 20, 30]


class TestFixtureWithDependencies:
    """Test fixtures with parameter dependencies."""
    
    def test_fixture_dependencies(self):
        """Test fixture with dependencies."""
        @param_generator
        def generate_base_url():
            """Generate base URLs."""
            yield "http://localhost"
            yield "http://testserver"
        
        @param_generator
        def generate_endpoint(base_url):
            """Generate endpoints based on base URL."""
            yield f"{base_url}/api/users"
            yield f"{base_url}/api/posts"
        
        @parametrize_fixture("base_url", generate_base_url)
        def url_context(base_url):
            return {"base": base_url}
        
        @parametrize_fixture("endpoint", generate_endpoint)
        def full_url(endpoint):
            return endpoint
        
        for base in ["http://localhost", "http://testserver"]:
            url_ctx = {"base": base}
            assert url_ctx["base"] in ["http://localhost", "http://testserver"]
            assert "api" in f"{base}/api/users"


class TestMixedFixtureAndParametrization:
    """Test mixing fixtures with parametrization."""
    
    def test_mixed_static_dynamic(self):
        """Test mixing static fixture with dynamic parametrization."""
        @pytest.fixture
        def static_fixture():
            return "static_value"
        
        @param_generator
        def generate_dynamic_values():
            """Generate dynamic values."""
            yield "dynamic1"
            yield "dynamic2"
        
        @parametrize_test("dynamic", generate_dynamic_values)
        def test_mix(static_fixture, dynamic):
            assert static_fixture == "static_value"
            assert dynamic in ["dynamic1", "dynamic2"]
        
        test_mix("static_value", "dynamic1")
        test_mix("static_value", "dynamic2")
    
    def test_all_types_together(self):
        """Test all types together."""
        @pytest.fixture
        def static_fixture():
            return "static_value"
        
        @pytest.fixture(params=["fixture_param1", "fixture_param2"])
        def parametrized_fixture(request):
            return request.param
        
        @param_generator
        def generate_more_values():
            """Generate more values."""
            yield 100
            yield 200
        
        @parametrize_test("dynamic_val", generate_more_values)
        def test_all(static_fixture, parametrized_fixture, dynamic_val):
            assert static_fixture == "static_value"
            assert parametrized_fixture in ["fixture_param1", "fixture_param2"]
            assert dynamic_val in [100, 200]
        
        for pf in ["fixture_param1", "fixture_param2"]:
            for dv in [100, 200]:
                test_all("static_value", pf, dv)


class TestFixtureScopes:
    """Test fixture scopes with dynamic parametrization."""
    
    def test_session_scope(self):
        """Test session scope combination."""
        @param_generator
        def generate_session_data():
            """Generate session data."""
            return {"session_key": "session_value"}
        
        @pytest.fixture(scope="session")
        def session_fixture():
            return {"scope": "session"}
        
        @parametrize_test("data", generate_session_data)
        def test_session(session_fixture, data):
            assert session_fixture["scope"] == "session"
            assert data["session_key"] == "session_value"
        
        test_session({"scope": "session"}, {"session_key": "session_value"})
    
    def test_module_scope(self):
        """Test module scope combination."""
        @param_generator
        def generate_module_data():
            """Generate module data."""
            return {"module_key": "module_value"}
        
        @pytest.fixture(scope="module")
        def module_fixture():
            return {"scope": "module"}
        
        @parametrize_test("data", generate_module_data)
        def test_module(module_fixture, data):
            assert module_fixture["scope"] == "module"
            assert data["module_key"] == "module_value"
        
        test_module({"scope": "module"}, {"module_key": "module_value"})


class TestFixtureWithDynRef:
    """Test fixtures using DynRef."""
    
    def test_fixture_dynref(self):
        """Test fixture with DynRef computation."""
        @param_generator
        def generate_base():
            """Generate base value."""
            yield 10
        
        @param_generator
        def generate_multiplier():
            """Generate multiplier."""
            yield 5
        
        @parametrize_fixture("base", generate_base)
        def base_value(base):
            return base
        
        @parametrize_fixture("multiplier", generate_multiplier)
        def multiplier_value(multiplier):
            return multiplier
        
        @parametrize_fixture("result", DynRef("base_value") * DynRef("multiplier_value"))
        def computed_result(result):
            return result
        
        base_val = 10
        mult_val = 5
        result = base_val * mult_val
        
        assert base_val == 10
        assert mult_val == 5
        assert result == 50


class TestIndirectFixture:
    """Test indirect fixture parametrization."""
    
    def test_indirect_fixture(self):
        """Test indirect fixture parametrization."""
        @param_generator
        def generate_input_data():
            """Generate input data."""
            yield {"input": 1}
            yield {"input": 2}
            yield {"input": 3}
        
        @parametrize_fixture("raw_data", generate_input_data)
        def processed_data(raw_data):
            return {"processed": raw_data["input"] * 2}
        
        for inp in [1, 2, 3]:
            raw = {"input": inp}
            processed = {"processed": raw["input"] * 2}
            assert processed["processed"] in [2, 4, 6]
    
    def test_user_profile_fixture(self):
        """Test user profile fixture."""
        @param_generator
        def generate_user_data():
            """Generate user data."""
            yield {"username": "alice", "age": 25}
            yield {"username": "bob", "age": 30}
        
        @parametrize_fixture("user_data", generate_user_data)
        def user_profile(user_data):
            return {
                "display_name": user_data["username"].upper(),
                "age_group": "adult" if user_data["age"] >= 18 else "minor"
            }
        
        for username, age in [("alice", 25), ("bob", 30)]:
            user_data = {"username": username, "age": age}
            profile = {
                "display_name": user_data["username"].upper(),
                "age_group": "adult" if user_data["age"] >= 18 else "minor"
            }
            assert profile["display_name"] in ["ALICE", "BOB"]
            assert profile["age_group"] == "adult"
