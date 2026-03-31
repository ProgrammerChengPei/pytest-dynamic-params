# Test utils functionality

import pytest
from dynamic_params.utils.cache import generate_cache_key
from dynamic_params.utils.decorators import create_decorator
from dynamic_params.utils.validation import validate_parametrize_args
from dynamic_params.errors import ParametrizeError


class TestGenerateCacheKey:
    """Test generate_cache_key function"""
    
    def test_generate_cache_key_simple(self):
        """Test generate_cache_key with simple arguments"""
        key1 = generate_cache_key("func", [1, 2], {"a": 3})
        key2 = generate_cache_key("func", [1, 2], {"a": 3})
        assert key1 == key2
    
    def test_generate_cache_key_different_args(self):
        """Test generate_cache_key with different arguments"""
        key1 = generate_cache_key("func", [1, 2], {"a": 3})
        key2 = generate_cache_key("func", [1, 3], {"a": 3})
        assert key1 != key2
    
    def test_generate_cache_key_different_kwargs(self):
        """Test generate_cache_key with different kwargs"""
        key1 = generate_cache_key("func", [1, 2], {"a": 3})
        key2 = generate_cache_key("func", [1, 2], {"a": 4})
        assert key1 != key2
    
    def test_generate_cache_key_different_func(self):
        """Test generate_cache_key with different function name"""
        key1 = generate_cache_key("func1", [1, 2], {"a": 3})
        key2 = generate_cache_key("func2", [1, 2], {"a": 3})
        assert key1 != key2
    
    def test_generate_cache_key_empty(self):
        """Test generate_cache_key with empty arguments"""
        key = generate_cache_key("func", [], {})
        assert isinstance(key, str)


class TestCreateDecorator:
    """Test create_decorator function"""
    
    def test_create_decorator_with_parentheses(self):
        """Test create_decorator with parentheses"""
        def decorator_func(func, arg1, arg2=None):
            func.decorator_arg1 = arg1
            func.decorator_arg2 = arg2
            return func
        
        decorator = create_decorator(decorator_func)
        
        @decorator(arg1="value1", arg2="value2")
        def test_func():
            pass
        
        assert test_func.decorator_arg1 == "value1"
        assert test_func.decorator_arg2 == "value2"
    
    def test_create_decorator_without_parentheses(self):
        """Test create_decorator without parentheses"""
        def decorator_func(func):
            func.decorator_applied = True
            return func
        
        decorator = create_decorator(decorator_func)
        
        @decorator
        def test_func():
            pass
        
        assert test_func.decorator_applied is True
    
    def test_create_decorator_no_args(self):
        """Test create_decorator with no arguments"""
        def decorator_func(func):
            func.decorator_applied = True
            return func
        
        decorator = create_decorator(decorator_func)
        
        @decorator()
        def test_func():
            pass
        
        assert test_func.decorator_applied is True


class TestValidateParametrizeArgs:
    """Test validate_parametrize_args function"""
    
    def test_validate_parametrize_args_valid(self):
        """Test validate_parametrize_args with valid arguments"""
        validate_parametrize_args("a,b", [[1, 2], [3, 4]])
    
    def test_validate_parametrize_args_invalid_argnames_type(self):
        """Test validate_parametrize_args with invalid argnames type"""
        with pytest.raises(ParametrizeError):
            validate_parametrize_args(123, [[1, 2]])
    
    def test_validate_parametrize_args_invalid_argvalues_type(self):
        """Test validate_parametrize_args with invalid argvalues type"""
        with pytest.raises(ParametrizeError):
            validate_parametrize_args("a,b", "not a list")
    
    def test_validate_parametrize_args_empty_argnames(self):
        """Test validate_parametrize_args with empty argnames"""
        with pytest.raises(ParametrizeError):
            validate_parametrize_args("", [[1, 2]])
    
    def test_validate_parametrize_args_empty_argvalues(self):
        """Test validate_parametrize_args with empty argvalues"""
        with pytest.raises(ParametrizeError):
            validate_parametrize_args("a,b", [])
