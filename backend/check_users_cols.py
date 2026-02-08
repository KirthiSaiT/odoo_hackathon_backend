from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)

def check_cols():
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'")
            print(f"Users Columns: {[row[0] for row in cursor.fetchall()]}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cols()
