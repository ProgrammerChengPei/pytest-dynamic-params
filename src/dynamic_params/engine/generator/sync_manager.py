# Sync manager for file + pytest hook synchronization

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading


class SyncManager:
    """Synchronization manager
    
    Combines file sync (for large data) with pytest hook (for small config):
    - File sync: Generator metadata, preloaded data
    - Pytest hook: Worker config, runtime parameters
    
    Features:
    - Automatic preload for session/module scope generators
    - File-based sync for large datasets
    - Pytest hook for small config data
    - Thread-safe operations
    """
    
    _instance: Optional['SyncManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'SyncManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.generators: Dict[str, Any] = {}
            self.sync_file: Optional[Path] = None
            self.config: Dict[str, Any] = {
                'is_master': True,
                'is_worker': False,
                'worker_id': 'master'
            }
            self._lock = threading.Lock()
    
    def register_generator(self, generator: Any) -> None:
        """Register a generator
        
        Args:
            generator: Generator instance (GeneratorBase or subclass)
        """
        with self._lock:
            name = generator.func.__name__
            self.generators[name] = generator
            
            # Auto-preload for master process (only for session/module scope)
            if self.config['is_master'] and generator.scope in ('session', 'module'):
                self._preload_generator(generator)
    
    def _preload_generator(self, generator: Any) -> None:
        """Preload generator data
        
        Args:
            generator: Generator instance to preload
        """
        try:
            # Execute generator to get data
            data = generator._execute_func()
            generator.set_preloaded_data(data)
            
            # Write to sync file
            self._write_sync_file()
            
            print(f"[SyncManager] Preloaded {len(data) if data else 0} items for {generator.func.__name__}")
        except Exception as e:
            print(f"[SyncManager] Failed to preload {generator.func.__name__}: {e}")
    
    def _write_sync_file(self) -> None:
        """Write preloaded data to sync file"""
        if not self.generators:
            return
        
        # Collect all preloaded data
        sync_data = {
            'generators': {}
        }
        
        for name, gen in self.generators.items():
            preloaded = gen.get_preloaded_data()
            if preloaded is not None:
                sync_data['generators'][name] = {
                    'data': preloaded,
                    'scope': gen.scope,
                    'cache': gen.cache,
                    'resource_type': getattr(gen, '_resource_type', None)
                }
        
        # Only write if there's data
        if sync_data['generators']:
            try:
                # Create sync file if not exists
                if not self.sync_file:
                    self.sync_file = Path(tempfile.mktemp(suffix='_sync.json'))
                
                # Atomic write
                temp_file = self.sync_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(sync_data, f, indent=2, default=str)
                temp_file.replace(self.sync_file)
                
                print(f"[SyncManager] Sync file written: {self.sync_file}")
            except Exception as e:
                print(f"[SyncManager] Failed to write sync file: {e}")
    
    def load_from_sync_file(self) -> bool:
        """Load preloaded data from sync file (Worker process)
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.sync_file or not self.sync_file.exists():
            print(f"[SyncManager] Sync file not found: {self.sync_file}")
            return False
        
        try:
            with open(self.sync_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            generators_data = data.get('generators', {})
            
            for name, gen_data in generators_data.items():
                if name in self.generators:
                    generator = self.generators[name]
                    preloaded = gen_data.get('data')
                    if preloaded is not None:
                        generator.set_preloaded_data(preloaded)
                        print(f"[SyncManager] Loaded {len(preloaded)} items for {name}")
            
            return True
        except Exception as e:
            print(f"[SyncManager] Failed to load from sync file: {e}")
            return False
    
    def get_sync_config(self) -> Dict[str, Any]:
        """Get sync config for pytest hook
        
        Returns:
            Config dict (small data, suitable for pytest hook)
        """
        return {
            'sync_file_path': str(self.sync_file) if self.sync_file else None,
            'generator_count': len(self.generators),
            'is_master': self.config['is_master'],
            'is_worker': self.config['is_worker'],
            'worker_id': self.config['worker_id']
        }
    
    def apply_sync_config(self, config: Dict[str, Any]) -> None:
        """Apply sync config from pytest hook
        
        Args:
            config: Config dict from pytest hook
        """
        self.config.update(config)
        print(f"[SyncManager] Applied config: worker_id={config.get('worker_id', 'unknown')}")
    
    def cleanup(self) -> None:
        """Cleanup temporary files (master process only)"""
        if self.config['is_master'] and self.sync_file:
            try:
                self.sync_file.unlink(missing_ok=True)
                self.sync_file.with_suffix('.tmp').unlink(missing_ok=True)
                print(f"[SyncManager] Cleaned up sync file: {self.sync_file}")
            except Exception as e:
                print(f"[SyncManager] Failed to cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status
        
        Returns:
            Status dict
        """
        return {
            'initialized': self._initialized,
            'is_master': self.config['is_master'],
            'is_worker': self.config['is_worker'],
            'worker_id': self.config['worker_id'],
            'generator_count': len(self.generators),
            'sync_file_exists': self.sync_file.exists() if self.sync_file else False,
            'sync_file_path': str(self.sync_file) if self.sync_file else None
        }


# Global sync manager instance
sync_manager = SyncManager()
