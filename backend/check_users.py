from app.core.database import get_db_cursor

def check_users_schema():
    print("Checking Users table columns...")
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'")
            columns = [row.COLUMN_NAME for row in cursor.fetchall()]
            print(f"Users Columns: {columns}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users_schema()
