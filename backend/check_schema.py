from app.core.database import get_db_cursor

def check_schema():
    try:
        with get_db_cursor() as cursor:
            # Check Users.user_id type
            cursor.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'user_id'")
            row = cursor.fetchone()
            print(f"Users.user_id type: {row[0] if row else 'Not Found'}")
            
            # Check Employees.UserId type
            cursor.execute("SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Employees' AND COLUMN_NAME = 'UserId'")
            row = cursor.fetchone()
            print(f"Employees.UserId type: {row[0] if row else 'Not Found'}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_schema()
