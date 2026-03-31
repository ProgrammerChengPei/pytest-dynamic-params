# Pytest hooks implementation

from pytest import Metafunc

from ..engine.parametrize.processor import ParametrizeProcessor

def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Generate test parameters
    
    This is the main hook function for pytest that generates test parameters
    based on the dynamic parametrization configuration.
    
    Args:
        metafunc: pytest's Metafunc object
    """
    processor = ParametrizeProcessor()
    processor.process(metafunc)
