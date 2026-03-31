"""
Functional tests for pytest-dynamic-params plugin.

These tests verify the complete functionality of the plugin from an end-user perspective,
testing real-world scenarios and use cases.
"""

import pytest
import sys
import os

# Add src to path so we can import the plugin
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
