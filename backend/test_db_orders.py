from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_orders():
    try:
        with get_db_cursor() as cursor:
            print("--- SCHEMA ---")
            cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Orders'")
            for row in cursor.fetchall():
                print(row)
            
            print("\n--- RECENT ORDERS ---")
            cursor.execute("SELECT TOP 5 Id, UserId, TotalAmount, Status, CreatedAt FROM Orders ORDER BY CreatedAt DESC")
            for row in cursor.fetchall():
                print(row)
                
            print("\n--- ORDER ITEMS ---")
            cursor.execute("SELECT TOP 5 * FROM OrderItems")
            for row in cursor.fetchall():
                print(row)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_orders()
