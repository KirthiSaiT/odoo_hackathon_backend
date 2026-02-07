from app.core.database import get_db_cursor

def check_users_schema():
    print("Checking Users table columns...")
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'")
            rows = cursor.fetchall()
            for row in rows:
                print(f"{row[0]}: {row[1]}", flush=True)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users_schema()
