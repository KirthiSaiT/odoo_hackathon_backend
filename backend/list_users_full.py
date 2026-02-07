from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)

def list_all():
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'")
            rows = cursor.fetchall()
            print(f"Users FULL Columns: {[r[0] for r in rows]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_all()
