# Test plugin hooks module

import pytest
from unittest.mock import patch, MagicMock
from dynamic_params.plugin.hooks import pytest_generate_tests


class TestHooks:
    """Test pytest hooks"""
    
    @patch('dynamic_params.plugin.hooks.ParametrizeProcessor')
    def test_pytest_generate_tests(self, mock_processor_class):
        """Test pytest_generate_tests hook"""
        # Setup mock
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Create mock metafunc
        mock_metafunc = MagicMock()
        
        # Call the hook
        pytest_generate_tests(mock_metafunc)
        
        # Verify
        mock_processor_class.assert_called_once()
        mock_processor.process.assert_called_once_with(mock_metafunc)
    
    @patch('dynamic_params.plugin.hooks.ParametrizeProcessor')
    def test_pytest_generate_tests_with_different_metafunc(self, mock_processor_class):
        """Test pytest_generate_tests with different metafunc objects"""
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        
        # Test with multiple metafunc1
        mock_metafunc1 = MagicMock()
        pytest_generate_tests(mock_metafunc1)
        mock_processor.process.assert_called_with(mock_metafunc1)
        
        # Reset mock
        mock_processor.reset_mock()
        
        # Test with metafunc2
        mock_metafunc2 = MagicMock()
        pytest_generate_tests(mock_metafunc2)
        mock_processor.process.assert_called_with(mock_metafunc2)
