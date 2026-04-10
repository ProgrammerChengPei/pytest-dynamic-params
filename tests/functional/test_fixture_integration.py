"""
Fixture integration functional tests.

Tests integration between dynamic parameters and pytest fixtures.
"""

import pytest
from dynamic_params import param_generator


class TestFixtureIntegration:
    """Test fixture integration with param_generator."""
    
    def test_param_generator_with_pytest_fixtures(self):
        """Test param_generator integration with standard pytest fixtures."""
        @pytest.fixture
        def user_context():
            return {"app": "test"}
        
        @param_generator
        def generate_user_ids():
            """Generate user IDs."""
            for i in range(1, 4):
                yield i
        
        @pytest.mark.parametrize("user_id", generate_user_ids())
        def test_user_context(user_context, user_id):
            assert user_context["app"] == "test"
            assert user_id in [1, 2, 3]
        
        # Test the function calls
        test_user_context({"app": "test"}, 1)
        test_user_context({"app": "test"}, 2)
        test_user_context({"app": "test"}, 3)
    
    def test_param_generator_with_parametrized_fixtures(self):
        """Test param_generator with pytest's parametrized fixtures."""
        @pytest.fixture(params=[10, 20, 30])
        def config_timeout(request):
            return {"timeout": request.param}
        
        @param_generator
        def generate_app_names():
            """Generate app names."""
            yield "backend"
            yield "frontend"
        
        @pytest.mark.parametrize("app_name", generate_app_names())
        def test_config_integration(config_timeout, app_name):
            assert config_timeout["timeout"] in [10, 20, 30]
            assert app_name in ["backend", "frontend"]
        
        # Test the function calls
        for test_config in [{"timeout": 10}, {"timeout": 20}, {"timeout": 30}]:
            for app in ["backend", "frontend"]:
                test_config_integration(test_config, app)


class TestParamGeneratorDependencies:
    """Test param_generator with dependencies."""
    
    def test_generator_with_function_dependencies(self):
        """Test generator that depends on other generators."""
        @param_generator
        def generate_base_urls():
            """Generate base URLs."""
            yield "http://localhost"
            yield "http://testserver"
        
        @param_generator
        def generate_endpoints():
            """Generate endpoints."""
            return ["/api/users", "/api/posts"]
        
        # Test independent param_generators working together
        @pytest.mark.parametrize("base_url", generate_base_urls())
        @pytest.mark.parametrize("endpoint", generate_endpoints())
        def test_url_combination(base_url, endpoint):
            assert base_url in ["http://localhost", "http://testserver"]
            assert endpoint in ["/api/users", "/api/posts"]
            assert "/api/" in endpoint
        
        # Test all combinations
        for base in ["http://localhost", "http://testserver"]:
            for endpoint in ["/api/users", "/api/posts"]:
                test_url_combination(base, endpoint)
    
    def test_generator_chain_implicit_scope(self):
        """Test chain of generators with automatic scope inference."""
        @param_generator(scope="session")
        def generate_session_config():
            """Generate session-level configuration."""
            return ["config_v1", "config_v2"]
        
        @param_generator  # No explicit scope, should be inferred
        def generate_processing_config(choices):
            """Generate processing configuration based on session config."""
            return [f"process_{choice}" for choice in choices]
        
        # Test that generators work together
        @pytest.mark.parametrize("session_conf", generate_session_config())
        @pytest.mark.parametrize("process_conf", generate_processing_config(["config_v1", "config_v2"]))
        def test_config_chain(session_conf, process_conf):
            assert session_conf in ["config_v1", "config_v2"]
            assert process_conf in ["process_config_v1", "process_config_v2"]


class TestFixtureScopeIntegration:
    """Test fixture scope integration with param_generator."""
    
    def test_session_scope_with_generator(self):
        """Test session scope fixture with param_generator."""
        @pytest.fixture(scope="session")
        def session_data():
            return {"session_key": "session_value"}
        
        @param_generator
        def generate_test_cases():
            """Generate test case data."""
            return ["case1", "case2", "case3"]
        
        @pytest.mark.parametrize("test_case", generate_test_cases())
        def test_session_scope_integration(session_data, test_case):
            assert session_data["session_key"] == "session_value"
            assert test_case in ["case1", "case2", "case3"]
    
    def test_module_scope_with_generator(self):
        """Test module scope fixture with param_generator."""
        @pytest.fixture(scope="module")
        def module_config():
            return {"module": "test_module"}
        
        @param_generator
        def generate_module_data():
            """Generate module-specific data."""
            yield "data_v1"
            yield "data_v2"
        
        @pytest.mark.parametrize("mod_data", generate_module_data())
        def test_module_scope_integration(module_config, mod_data):
            assert module_config["module"] == "test_module"
            assert mod_data in ["data_v1", "data_v2"]