"""
conftest.py for performance tests.

Provides fixtures and utilities for performance testing.
"""

import pytest
import time
import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def performance_thresholds():
    """
    Performance thresholds for different operations.
    
    Returns:
        dict: Performance thresholds in milliseconds
    """
    return {
        "cache_hit": 1,  # Cache hit should be < 1ms
        "cache_miss": 10,  # Cache miss should be < 10ms
        "lazy_load": 5,  # Lazy load should be < 5ms
        "dependency_resolve": 10,  # Dependency resolution should be < 10ms
        "param_generation_small": 50,  # Small param generation < 50ms
        "param_generation_medium": 200,  # Medium param generation < 200ms
        "param_generation_large": 1000,  # Large param generation < 1000ms
        "memory_usage_mb": 100,  # Memory usage should be < 100MB
    }


@pytest.fixture(scope="session")
def benchmark_config():
    """
    Benchmark configuration.
    
    Returns:
        dict: Benchmark configuration
    """
    return {
        "warmup_iterations": 3,
        "benchmark_iterations": 10,
        "sample_size": 100,
        "large_sample_size": 10000,
        "stress_sample_size": 100000,
    }


@pytest.fixture
def timer():
    """
    Simple timer context manager for benchmarking.
    
    Yields:
        Timer: Timer object with elapsed time
    """
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = 0
        
        def __enter__(self):
            self.start_time = time.perf_counter()
            return self
        
        def __exit__(self, *args):
            self.end_time = time.perf_counter()
            self.elapsed = (self.end_time - self.start_time) * 1000  # ms
    
    return Timer()


@pytest.fixture
def memory_tracker():
    """
    Track memory usage during tests.
    
    Yields:
        MemoryTracker: Memory tracking object
    """
    class MemoryTracker:
        def __init__(self):
            self.initial_memory = None
            self.peak_memory = None
            self.final_memory = None
        
        def _get_memory_mb(self):
            """Get current memory usage in MB."""
            try:
                import psutil
                process = psutil.Process(os.getpid())
                return process.memory_info().rss / 1024 / 1024
            except ImportError:
                # Fallback: return 0 if psutil not available
                return 0
        
        def __enter__(self):
            self.initial_memory = self._get_memory_mb()
            self.peak_memory = self.initial_memory
            return self
        
        def __exit__(self, *args):
            self.final_memory = self._get_memory_mb()
        
        def update_peak(self):
            """Update peak memory usage."""
            current = self._get_memory_mb()
            if current > self.peak_memory:
                self.peak_memory = current
        
        def get_delta(self):
            """Get memory delta in MB."""
            return self.final_memory - self.initial_memory
    
    return MemoryTracker()


@pytest.fixture(scope="session")
def large_dataset_generator():
    """
    Generate large datasets for performance testing.
    
    Returns:
        callable: Dataset generator function
    """
    def generate(size):
        """Generate a dataset of specified size."""
        return list(range(size))
    
    return generate


@pytest.fixture(scope="session")
def complex_dependency_graph():
    """
    Generate a complex dependency graph for testing.
    
    Returns:
        dict: Complex dependency graph
    """
    return {
        "nodes": 100,
        "edges": 500,
        "max_depth": 10,
        "cyclic": False,
    }
