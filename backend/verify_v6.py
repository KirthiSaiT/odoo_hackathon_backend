from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)

def check_v6():
    try:
        with get_db_cursor() as cursor:
            order_id = 6
            print(f"--- CHECKING ORDER {order_id} ---")
            
            # 1. Check joined order/user
            cursor.execute("""
                SELECT o.Id, o.UserId, u.Email, u.FullNames
                FROM Orders o
                LEFT JOIN Users u ON o.UserId = u.Id
                WHERE o.Id = ?
            """, (order_id,))
            order_row = cursor.fetchone()
            print(f"Order/User: {order_row}")
            
            # 2. Check Order Items
            cursor.execute("""
                SELECT oi.OrderId, oi.ProductId, p.Name, oi.Quantity, oi.Price
                FROM OrderItems oi
                LEFT JOIN Products p ON oi.ProductId = p.Id
                WHERE oi.OrderId = ?
            """, (order_id,))
            items = cursor.fetchall()
            print(f"Items: {items}")
            
            # 3. Check Order Items schema
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'OrderItems'")
            print(f"OrderItems Columns: {cursor.fetchall()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_v6()
