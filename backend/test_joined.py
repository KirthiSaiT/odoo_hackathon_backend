from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)

def test_joined():
    try:
        with get_db_cursor() as cursor:
            # Full joined query
            sql = "SELECT o.Id, o.TotalAmount, o.Status, o.CreatedAt, u.Email, u.FullNames, u.PhoneNumber FROM Orders o LEFT JOIN Users u ON o.UserId = u.Id WHERE o.Id = ?"
            cursor.execute(sql, (6,))
            print(f"Result: {cursor.fetchone()}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_joined()
