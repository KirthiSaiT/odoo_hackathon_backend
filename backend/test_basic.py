from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)

def test_basic():
    try:
        with get_db_cursor() as cursor:
            # Try plain SELECT with int
            cursor.execute("SELECT Id, TotalAmount FROM Orders WHERE Id = 6")
            print(f"Result without params: {cursor.fetchone()}")
            
            # Try with params
            cursor.execute("SELECT Id, TotalAmount FROM Orders WHERE Id = ?", (6,))
            print(f"Result with params: {cursor.fetchone()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_basic()
