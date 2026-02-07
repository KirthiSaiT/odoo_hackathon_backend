"""
Database Connection Module
Provides MSSQL connection using pyodbc with connection pooling
"""
import pyodbc
import logging
import threading
from queue import Queue, Empty
from contextlib import contextmanager
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Connection pool settings
POOL_SIZE = 5
POOL_TIMEOUT = 30  # seconds to wait for connection

# Thread-safe connection pool
_pool: Queue = None
_pool_lock = threading.Lock()


def _create_connection():
    """Create a new database connection"""
    settings = get_settings()
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={settings.DB_SERVER};"
        f"DATABASE={settings.DB_NAME};"
        f"UID={settings.DB_USER};"
        f"PWD={settings.DB_PASSWORD};"
        f"MARS_Connection=yes;"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str, autocommit=False, timeout=30)


def _init_pool():
    """Initialize connection pool (lazy initialization)"""
    global _pool
    with _pool_lock:
        if _pool is None:
            _pool = Queue(maxsize=POOL_SIZE)
            for _ in range(POOL_SIZE):
                try:
                    conn = _create_connection()
                    _pool.put(conn)
                except Exception as e:
                    logger.error(f"❌ Failed to create pool connection: {e}")


def _get_pooled_connection():
    """Get a connection from pool or create new one"""
    _init_pool()
    
    try:
        # Try to get from pool with timeout
        conn = _pool.get(timeout=POOL_TIMEOUT)
        
        # Validate connection is still alive
        try:
            conn.execute("SELECT 1")
            return conn
        except:
            # Connection is stale, create new one
            try:
                conn.close()
            except:
                pass
            return _create_connection()
            
    except Empty:
        # Pool exhausted, create new connection
        logger.warning("⚠️ Connection pool exhausted, creating new connection")
        return _create_connection()


def _return_connection(conn):
    """Return connection to pool or close if pool is full"""
    if conn is None:
        return
        
    try:
        # Check if connection is usable
        conn.execute("SELECT 1")
        
        # Try to return to pool
        try:
            _pool.put_nowait(conn)
        except:
            # Pool is full, close this connection
            conn.close()
    except:
        # Connection is broken, close it
        try:
            conn.close()
        except:
            pass


@contextmanager
def get_db_cursor():
    """
    Context manager for safe database operations
    Uses connection pooling for better performance
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Users")
            result = cursor.fetchone()
    """
    conn = None
    cursor = None
    try:
        conn = _get_pooled_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        raise e
    finally:
        if cursor:
            try:
                # Consume all remaining result sets
                while cursor.nextset():
                    pass
                cursor.close()
            except:
                pass
        _return_connection(conn)


def get_connection():
    """
    Legacy function for backward compatibility
    Prefer using get_db_cursor() context manager instead
    """
    return _get_pooled_connection()

