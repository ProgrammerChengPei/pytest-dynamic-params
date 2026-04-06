# Pytest plugin implementation

from pytest import Config

from ..config import config as plugin_config

# Create a global plugin instance
plugin = None

def pytest_configure(config: Config) -> None:
    """Configure the plugin
    
    Args:
        config: pytest's Config object
    """
    global plugin
    from .pytest_plugin import PytestPlugin
    plugin = PytestPlugin()
    
    # Register the plugin
    config.pluginmanager.register(plugin, "dynamic_params")
    
    # Load configuration from pytest.ini or conftest.py
    plugin._load_config(config)
    
    # Initialize sync manager
    _initialize_sync(config)

def _initialize_sync(config: Config) -> None:
    """Initialize synchronization manager
    
    Args:
        config: pytest's Config object
    """
    try:
        from ..engine.generator.sync_manager import sync_manager
        
        if hasattr(config, 'workerinput'):
            # Worker process
            hook_config = config.workerinput.get('sync_config', {})
            sync_manager.apply_sync_config(hook_config)
            sync_manager.config['is_master'] = False
            sync_manager.config['is_worker'] = True
            sync_manager.config['worker_id'] = config.workerinput.get('workerid', 'unknown')
            
            # Load preloaded data from sync file
            sync_manager.load_from_sync_file()
        else:
            # Master process
            sync_manager.config['is_master'] = True
            sync_manager.config['is_worker'] = False
            print("[pytest_configure] Sync initialized for master")
    except Exception as e:
        print(f"[pytest_configure] Failed to initialize sync: {e}")

try:
    import pytest_xdist

    # Only define this hook if pytest-xdist is available
    def pytest_configure_node(node) -> None:
        """Configure worker node (pytest-xdist specific hook)
        
        Args:
            node: Worker node object
        """
        try:
            from ..engine.generator.sync_manager import sync_manager

            # Pass sync config via pytest hook
            config_data = sync_manager.get_sync_config()
            node.workerinput['sync_config'] = config_data
            
            print(f"[pytest_configure_node] Sent config to worker {node.workerinput.get('workerid')}")
        except Exception as e:
            print(f"[pytest_configure_node] Failed to configure node: {e}")
except ImportError:
    # pytest-xdist not installed, skip this hook
    pass

def pytest_unconfigure(config: Config) -> None:
    """Cleanup on pytest unconfigure
    
    Args:
        config: pytest's Config object
    """
    # Cleanup sync manager
    try:
        from ..engine.generator.sync_manager import sync_manager
        sync_manager.cleanup()
    except Exception as e:
        print(f"[pytest_unconfigure] Failed to cleanup sync: {e}")
    
    # Cleanup worker pools
    try:
        from ..engine.generator.worker_pool import WorkerPool
        WorkerPool.close_all()
    except Exception as e:
        print(f"[pytest_unconfigure] Failed to cleanup worker pools: {e}")

def pytest_generate_tests(metafunc):
    """Generate test parameters
    
    Args:
        metafunc: pytest's Metafunc object
    """
    from ..engine.parametrize.processor import ParametrizeProcessor
    
    processor = ParametrizeProcessor()
    processor.process(metafunc)

class PytestPlugin:
    """pytest plugin class"""
    
    def __init__(self):
        """Initialize the plugin"""
        self.config = plugin_config
    
    def _load_config(self, config: Config) -> None:
        """Load configuration from pytest.ini or conftest.py
        
        Args:
            config: pytest's Config object
        """
        # Check if there's a dynamic_params section in pytest.ini
        if hasattr(config, 'getini'):
            # Load configuration values with default values
            try:
                default_cache = config.getini("dynamic_params_default_cache")
                if default_cache:
                    self.config.default_cache = default_cache.lower() == "true"
            except ValueError:
                pass
            
            try:
                default_lazy = config.getini("dynamic_params_default_lazy")
                if default_lazy:
                    self.config.default_lazy = default_lazy.lower() == "true"
            except ValueError:
                pass
            
            try:
                default_scope = config.getini("dynamic_params_default_scope")
                if default_scope:
                    self.config.default_scope = default_scope
            except ValueError:
                pass
