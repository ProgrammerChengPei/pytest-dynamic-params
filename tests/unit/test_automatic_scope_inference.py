# Test automatic scope inference for param_generator decorator

import pytest
from dynamic_params.public.decorators.param_generator import param_generator


class TestAutomaticScopeInference:
    """Test automatic scope inference based on generator dependencies."""
    
    def test_basic_generator_without_explicit_scope(self):
        """Test generator without explicit scope (should use default)."""
        @param_generator
        def basic_generator():
            """Generator without explicit scope."""
            return [1, 2, 3]
        
        # Should work without scope parameter (scope will be inferred at runtime)
        results = basic_generator()
        assert results == [1, 2, 3]
    
    def test_generator_function_scope_inference(self):
        """Test scope inference for generators with function-level dependencies."""
        @param_generator(scope="function")
        def function_scoped_dependency():
            """Function-scoped dependency generator."""
            return ["func_data"]
        
        # Main generator without explicit scope
        @param_generator  # No explicit scope, should be inferred
        def main_generator(function_scoped_dependency):
            """Main generator depends on function-scoped dependency."""
            return [f"main_{function_scoped_dependency[0]}"]
        
        # Scope should be inferred as function (minimum of dependencies)
        results = main_generator()
        assert results == ["main_func_data"]
    
    def test_generator_session_scope_inference(self):
        """Test scope inference with session-level dependencies."""
        @param_generator(scope="session")
        def session_scoped_data():
            """Session-scoped data generator."""
            return ["session_data"]
        
        @param_generator(scope="module")
        def module_scoped_processor():
            """Module-scoped processor generator."""
            return ["module_processor"]
        
        # Main generator without explicit scope
        @param_generator  # No explicit scope
        def combined_generator(session_scoped_data, module_scoped_processor):
            """Depends on session and module scoped generators."""
            # Should infer function scope (minimum of session and module)
            return [f"combined_{session_scoped_data[0]}_{module_scoped_processor[0]}"]
        
        results = combined_generator()
        assert "combined_session_data_module_processor" in results[0]


class TestMultiLevelDependencyChain:
    """Test multi-level dependency chains with automatic scope inference."""
    
    def test_multi_level_chain_inference(self):
        """Test automatic scope inference in multi-level chains."""
        @param_generator(scope="session")
        def algorithm():
            """Session-level algorithm generator."""
            return ["linear", "quadratic", "exponential"]
        
        @param_generator  # Scope inferred based on dependencies
        def processor(algorithm):
            """Processor depends on session-scoped algorithm."""
            # Should infer session scope (same as algorithm)
            return [f"processor_{alg}" for alg in algorithm]
        
        @param_generator  # No explicit scope
        def result_generator(processor):
            """Final result generator depends on processor."""
            # Should infer session scope (same as processor)
            return [f"result_{proc}" for proc in processor]
        
        results = result_generator()
        assert len(results) == 3
        assert all("result_processor_" in result for result in results)
    
    def test_function_scope_chain_with_session_dependency(self):
        """Test chain with function-scoped and session-scoped dependencies."""
        @param_generator(scope="session")
        def global_config():
            """Global configuration (session scope)."""
            return ["config_v1", "config_v2"]
        
        @param_generator(scope="function")
        def local_transformer():
            """Local transformation (function scope)."""
            return ["transform_a", "transform_b"]
        
        @param_generator  # No explicit scope
        def final_generator(global_config, local_transformer):
            """Depends on both session and function scoped generators."""
            # Should infer function scope (minimum of session and function)
            results = []
            for config in global_config:
                for transform in local_transformer:
                    results.append(f"{config}_{transform}")
            return results
        
        results = final_generator()
        assert len(results) == 4  # 2 configs × 2 transforms
        assert all("_config_" in result for result in results)


class TestManualScopeOverride:
    """Test manual scope override when automatic inference is insufficient."""
    
    def test_manual_scope_override_works(self):
        """Test that explicit scope parameter still works."""
        @param_generator(scope="module")  # Explicit scope
        def manual_scoped_generator():
            """Generator with explicit manual scope."""
            return ["manual_data"]
        
        results = manual_scoped_generator()
        assert results == ["manual_data"]
    
    def test_manual_scope_takes_precedence(self):
        """Test that explicit scope takes precedence over automatic inference."""
        @param_generator(scope="function")
        def function_dependency():
            """Function-scoped dependency."""
            return ["func_dep"]
        
        @param_generator(scope="session")  # Explicit session scope
        def manual_override_generator(function_dependency):
            """Generator with explicit scope override."""
            # Explicit session scope should be used despite function dependency
            return [f"override_{function_dependency[0]}"]
        
        results = manual_override_generator()
        assert results == ["override_func_dep"]


class TestComplexDependencyScenarios:
    """Test complex dependency scenarios for scope inference."""
    
    def test_generator_with_multiple_dependency_scopes(self):
        """Test generator depending on multiple generators with different scopes."""
        @param_generator(scope="session")
        def session_data():
            return ["session_value"]
        
        @param_generator(scope="module")
        def module_data():
            return ["module_value"]
        
        @param_generator(scope="function")
        def function_data():
            return ["function_value"]
        
        @param_generator  # No explicit scope
        def multi_scope_generator(session_data, module_data, function_data):
            """Depends on session, module, and function scoped generators."""
            # Should infer function scope (minimum of all dependencies)
            return [
                f"multi_{session_data[0]}_{module_data[0]}_{function_data[0]}"
            ]
        
        results = multi_scope_generator()
        expected = "multi_session_value_module_value_function_value"
        assert results[0] == expected
    
    def test_nested_dependency_resolution(self):
        """Test nested dependency resolution with automatic scope inference."""
        @param_generator(scope="session")
        def base_config():
            return ["base_config"]
        
        @param_generator  # Inferred scope from base_config
        def intermediate_processor(base_config):
            return [f"processed_{base_config[0]}"]
        
        @param_generator  # Inferred scope from intermediate_processor
        def final_output(intermediate_processor):
            return [f"final_{intermediate_processor[0]}"]
        
        results = final_output()
        assert results[0] == "final_processed_base_config"