from app.core.database import get_db_cursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_data():
    try:
        with get_db_cursor() as cursor:
            # Get a user (e.g., the first one)
            cursor.execute("SELECT TOP 1 user_id FROM Users")
            user = cursor.fetchone()
            if not user:
                logger.error("No users found to seed data for.")
                return
            
            user_id = user[0]
            logger.info(f"Seeding data for User ID: {user_id}")

            # Add some orders
            orders = [
                {'amount': 1200.0, 'status': 'Confirmed'},
                {'amount': 800.0, 'status': 'Confirmed'},
                {'amount': 450.0, 'status': 'Pending'},
                {'amount': 2300.0, 'status': 'Confirmed'},
            ]

            for o in orders:
                cursor.execute("""
                    INSERT INTO Orders (UserId, TotalAmount, Status)
                    OUTPUT INSERTED.Id
                    VALUES (?, ?, ?)
                """, (user_id, o['amount'], o['status']))
                order_id = cursor.fetchone()[0]
                
                # Add one item per order
                cursor.execute("""
                    INSERT INTO OrderItems (OrderId, ProductId, Quantity, Price)
                    VALUES (?, (SELECT TOP 1 Id FROM Products), 1, ?)
                """, (order_id, o['amount']))

            logger.info("✅ Test data seeded successfully. Check your dashboard!")
    except Exception as e:
        logger.error(f"❌ Error seeding data: {str(e)}")

if __name__ == "__main__":
    seed_data()
