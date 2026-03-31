# Test version functionality

from dynamic_params import __version__


class TestVersion:
    """Test version information"""
    
    def test_version_exists(self):
        """Test that version exists"""
        assert __version__ is not None
    
    def test_version_format(self):
        """Test that version has correct format"""
        assert isinstance(__version__, str)
        parts = __version__.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()
