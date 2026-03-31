# Worker connection pool for independent database connections

from typing import Any, Callable, Dict, Optional
import threading


class WorkerPool:
    """Worker connection pool
    
    Provides independent connections for each worker process.
    Automatically manages connection lifecycle.
    
    Features:
    - One connection per worker per pool name
    - Thread-safe connection creation
    - Automatic cleanup
    - No configuration needed
    
    Usage:
        @param_generator(scope='function')
        def generate_orders():
            with WorkerPool.get_connection('orders_db', lambda: database.connect()) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM orders")
                for row in cursor.fetchall():
                    yield row
    """
    
    _pools: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_connection(cls, pool_name: str, create_func: Callable[[], Any]) -> Any:
        """Get or create a connection
        
        Args:
            pool_name: Name of the connection pool (e.g., 'orders_db', 'users_db')
            create_func: Function to create a new connection
        
        Returns:
            Connection instance
        
        Example:
            with WorkerPool.get_connection('db', lambda: database.connect()) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM data")
        """
        with cls._lock:
            if pool_name not in cls._pools:
                cls._pools[pool_name] = create_func()
            return cls._pools[pool_name]
    
    @classmethod
    def close_all(cls) -> None:
        """Close all connections
        
        Should be called during pytest cleanup.
        """
        with cls._lock:
            for pool_name, conn in cls._pools.items():
                try:
                    if hasattr(conn, 'close'):
                        conn.close()
                    print(f"[WorkerPool] Closed connection: {pool_name}")
                except Exception as e:
                    print(f"[WorkerPool] Failed to close {pool_name}: {e}")
            cls._pools.clear()
    
    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Get pool status
        
        Returns:
            Status dict with connection info
        """
        return {
            'pool_count': len(cls._pools),
            'pool_names': list(cls._pools.keys())
        }
