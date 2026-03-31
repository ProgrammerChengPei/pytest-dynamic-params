# Test plugin hooks functionality

import pytest
from unittest.mock import Mock, patch
from dynamic_params.plugin.hooks import pytest_generate_tests


class TestPytestGenerateTests:
    """Test pytest_generate_tests hook"""
    
    def test_hook_with_no_markers(self):
        """Test hook with no markers"""
        metafunc = Mock()
        metafunc.definition.iter_markers.return_value = []
        
        # Should not raise any error
        pytest_generate_tests(metafunc)
    
    def test_hook_with_dynamic_parametrize_marker(self):
        """Test hook with dynamic_parametrize marker"""
        # 使用 spec_set 确保没有额外的属性
        metafunc = Mock(spec_set=['definition', 'parametrize', 'function'])
        metafunc.function = Mock(spec_set=[])  # function 没有任何属性
        metafunc.definition = Mock()
        
        marker = Mock()
        marker.name = "dynamic_parametrize"
        marker.kwargs = {"argnames": "a", "argvalues": [[1], [2]]}
        metafunc.definition.iter_markers.return_value = [marker]
        
        # Should call parametrize
        pytest_generate_tests(metafunc)
        
        metafunc.parametrize.assert_called_once()
    
    def test_hook_with_multiple_markers(self):
        """Test hook with multiple markers"""
        metafunc = Mock()
        
        marker1 = Mock()
        marker1.name = "dynamic_parametrize"
        marker1.kwargs = {"argnames": "a", "argvalues": [[1]]}
        
        marker2 = Mock()
        marker2.name = "other_marker"
        marker2.kwargs = {}
        
        metafunc.definition.iter_markers.return_value = [marker1, marker2]
        
        # Should not raise any error
        pytest_generate_tests(metafunc)
    
    def test_hook_creates_processor(self):
        """Test that hook creates ParametrizeProcessor"""
        metafunc = Mock()
        metafunc.definition.iter_markers.return_value = []
        
        with patch('dynamic_params.plugin.hooks.ParametrizeProcessor') as mock_processor:
            pytest_generate_tests(metafunc)
            
            mock_processor.assert_called_once()
            mock_processor.return_value.process.assert_called_once_with(metafunc)
