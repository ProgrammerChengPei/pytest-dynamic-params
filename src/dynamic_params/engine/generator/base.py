# Generator base class implementation

import hashlib
import inspect
from typing import Any, Dict, List, Optional

from ...types import GeneratorFunc
from .cache import GeneratorCache


class GeneratorBase:
    """Base class for parameter generators

    Features:
    - Automatic preload support for session/module scope
    - External resource detection (database, network, file)
    - Sync (file + pytest hook) support
    - Worker connection pool integration
    """

    # Global configuration (class-level defaults)
    _global_config: Dict[str, Any] = {
        "preload_enabled": True,  # Auto-preload for session/module scope
        "use_file_sync": True,  # Use file sync for large data
        "auto_detect_resource": True,  # Auto-detect resource types
    }

    def __init__(
        self,
        func: GeneratorFunc,
        scope: str = "function",
        cache: bool = False,
        lazy: bool = False,
    ):
        """Initialize a generator

        Args:
            func: The generator function
            scope: The scope of the generator (function, class, module, session)
            cache: Whether to cache the generator results
            lazy: Whether to lazy load the generator
        """
        self.func = func
        self.scope = scope
        self.cache = cache
        self.lazy = lazy
        self.cache_instance = GeneratorCache()

        # Internal attributes for sync
        self._preloaded_data: Optional[List[Any]] = None
        self._resource_type: Optional[str] = None
        self._worker_pool_name: Optional[str] = None

        # Auto-detect resource type
        if self._global_config["auto_detect_resource"]:
            self._detect_resource_type()

        # Auto-enable preload for session/module scope
        if scope in ("session", "module") and self._global_config["preload_enabled"]:
            self._enable_preload()

        # Register with sync manager
        self._register_with_manager()

    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """Execute the generator function

        Args:
            *args: Positional arguments for the generator function
            **kwargs: Keyword arguments for the generator function

        Returns:
            List of generated parameter values
        """
        # Use preloaded data if available
        if self._preloaded_data is not None:
            return self._preloaded_data

        # Generate cache key if caching is enabled
        cache_key = None
        if self.cache:
            cache_key = self.get_cache_key(*args, **kwargs)
            # Check if result is in cache
            cached_result = self.cache_instance.get(self.scope, cache_key)
            if cached_result is not None:
                return cached_result

        # Execute the generator function
        result = self._execute_func(*args, **kwargs)

        # Store in cache if caching is enabled
        if self.cache and cache_key is not None:
            self.cache_instance.set(self.scope, cache_key, result)

        return result

    def _detect_resource_type(self) -> None:
        """Auto-detect resource type from function code"""
        try:
            source = inspect.getsource(self.func)
            if "database.connect" in source or "db.connect" in source:
                self._resource_type = "database"
            elif "requests.get" in source or "requests.post" in source:
                self._resource_type = "network"
            elif "open(" in source or "Path(" in source:
                self._resource_type = "file"
        except (OSError, TypeError):
            # Cannot get source code, skip detection
            pass

    def _enable_preload(self) -> None:
        """Enable preload for this generator"""
        # Mark for preload (actual preload happens in manager)
        pass

    def _register_with_manager(self) -> None:
        """Register with sync manager"""
        try:
            from .sync_manager import sync_manager

            sync_manager.register_generator(self)
        except (ImportError, Exception):
            # Manager not available, skip registration
            pass

    def set_preloaded_data(self, data: Optional[List[Any]]) -> None:
        """Set preloaded data (called by sync manager)

        Args:
            data: Preloaded data list
        """
        self._preloaded_data = data

    def get_preloaded_data(self) -> Optional[List[Any]]:
        """Get preloaded data

        Returns:
            Preloaded data list or None
        """
        return self._preloaded_data

    @classmethod
    def configure(cls, **kwargs: Any) -> None:
        """Configure global generator behavior

        Args:
            **kwargs: Configuration options

        Example:
            GeneratorBase.configure(preload_enabled=True)
            GeneratorBase.configure(use_file_sync=False)
        """
        cls._global_config.update(kwargs)

    def _execute_func(self, *args: Any, **kwargs: Any) -> List[Any]:
        """Execute the generator function and convert result to list

        Args:
            *args: Positional arguments for the generator function
            **kwargs: Keyword arguments for the generator function

        Returns:
            List of generated parameter values
        """
        result = self.func(*args, **kwargs)
        # Convert generator to list
        if inspect.isgenerator(result):
            return list(result)
        # Ensure result is a list
        if not isinstance(result, list):
            return [result]
        return result

    def get_cache_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate a cache key based on function signature and arguments

        Args:
            *args: Positional arguments for the generator function
            **kwargs: Keyword arguments for the generator function

        Returns:
            Cache key as a string
        """
        # Create a string representation of the function and arguments
        func_name = self.func.__name__
        args_repr = repr(args)
        kwargs_repr = repr(sorted(kwargs.items()))

        # Create a hash of the combined string
        combined = f"{func_name}:{args_repr}:{kwargs_repr}"
        return hashlib.md5(combined.encode()).hexdigest()

    def __call__(self, *args: Any, **kwargs: Any) -> List[Any]:
        """Call the generator as a function

        Args:
            *args: Positional arguments for the generator function
            **kwargs: Keyword arguments for the generator function

        Returns:
            List of generated parameter values
        """
        return self.execute(*args, **kwargs)

    def __iter__(self):
        """Allow GeneratorBase to be used directly in pytest.mark.parametrize"""
        return iter(self.execute())
