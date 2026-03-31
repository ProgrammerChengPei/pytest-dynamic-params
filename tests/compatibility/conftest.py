"""
Configuration and fixtures for compatibility tests.
"""
import pytest
import sys
import subprocess
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_dir():
    """Get the test directory path."""
    return Path(__file__).parent


@pytest.fixture(scope="session")
def root_dir():
    """Get the project root directory path."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def isolated_test_env(tmp_path):
    """Create an isolated test environment."""
    test_env = tmp_path / "isolated_test"
    test_env.mkdir()
    return test_env


@pytest.fixture
def run_pytest_cmd(root_dir):
    """Run pytest in a subprocess and return the result."""
    def run_pytest(test_file, args=None, cwd=None):
        # Add src directory to Python path
        env = os.environ.copy()
        src_path = str(root_dir / "src")
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{src_path};{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = src_path
        
        # Build the pytest command
        cmd = [sys.executable, "-m", "pytest"]
        if args:
            cmd.extend(args)
        cmd.append(str(test_file))
        
        # Run pytest directly
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            env=env
        )
        
        # Print debug information
        print("=" * 80)
        print(f"Command: {' '.join(cmd)}")
        print(f"CWD: {cwd}")
        print(f"Return code: {result.returncode}")
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print("=" * 80)
        
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    
    return run_pytest


@pytest.fixture(scope="session")
def python_version():
    """Get the current Python version."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


@pytest.fixture(scope="session")
def get_pytest_version():
    """Get the current pytest version."""
    import pytest
    return pytest.__version__
