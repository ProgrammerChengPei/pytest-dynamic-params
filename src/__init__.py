"""
Dynamic Parameters Plugin for pytest

This package provides dynamic parameterization capabilities for pytest,
allowing parameters to be computed based on other parameters or fixtures.
"""

from .dynamic_params import *

__version__ = "0.1.0"
__author__ = "pytest-dynamic-params"
__all__ = [
    'ParamGenerator',
    'LazyResult', 
    'GeneratorRegistry',
    'DynamicParamError',
    'MissingParameterError',
    'InvalidGeneratorError',
    'param_generator',
    'with_dynamic_params',
    'pytest_configure',
    'pytest_generate_tests',
    'DynamicParamConfig'
]