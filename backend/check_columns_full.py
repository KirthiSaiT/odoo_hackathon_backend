from app.core.database import get_db_cursor

def check_all_cols():
    try:
        with get_db_cursor() as cursor:
            print("--- Users Columns ---")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users'")
            rows = cursor.fetchall()
            for r in rows:
                print(r[0])
                
            print("\n--- Employees Columns ---")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Employees'")
            rows = cursor.fetchall()
            for r in rows:
                print(r[0])

            print("\n--- Roles Columns ---")
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Roles'")
            rows = cursor.fetchall()
            for r in rows:
                print(r[0])

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_all_cols()
