from app.core.database import get_db_cursor

def check_cart_schema():
    print("Checking Cart table columns...")
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Cart'")
            columns = [row.COLUMN_NAME for row in cursor.fetchall()]
            print(f"Cart Columns: {columns}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cart_schema()
