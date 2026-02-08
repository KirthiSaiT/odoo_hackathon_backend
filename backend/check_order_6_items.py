from app.core.database import get_db_cursor

def check_items(order_id):
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM OrderItems WHERE OrderId = ?", (order_id,))
            rows = cursor.fetchall()
            print(f"Items for Order {order_id}: {rows}")
            
            # Also check if Product names are retrievable
            cursor.execute("""
                SELECT oi.ProductId, p.Name 
                FROM OrderItems oi 
                LEFT JOIN Products p ON oi.ProductId = p.Id 
                WHERE oi.OrderId = ?
            """, (order_id,))
            print(f"Product Names for Order {order_id}: {cursor.fetchall()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_items(6)
