"""
Database Connection Module
Provides MSSQL connection using pyodbc with context manager support
"""
import pyodbc
from contextlib import contextmanager
from app.core.config import get_settings


def get_connection():
    """
    Get a database connection with MARS enabled
    MARS_Connection=yes fixes "Connection is busy" error
    autocommit=False for proper transaction control
    """
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
        f"Connection Timeout=60;"
    )
    return pyodbc.connect(conn_str, autocommit=False, timeout=30)


@contextmanager
def get_db_cursor():
    """
    Context manager for safe database operations
    Automatically handles commit/rollback and cleanup
    
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Users")
            result = cursor.fetchone()
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
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
                # Consume all remaining result sets from stored procedures
                while cursor.nextset():
                    pass
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
