"""
Pytest configuration for dynamic parameters plugin tests
"""

import os
import sys

# Add the src directory to the path so tests can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 导入插件以确保pytest能够发现它
