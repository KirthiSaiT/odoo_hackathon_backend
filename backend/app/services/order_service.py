from typing import List, Optional
import logging
from app.core.database import get_db_cursor
from app.models.order_models import DashboardStatsResponse, OrderResponse

logger = logging.getLogger(__name__)

class OrderService:
    @staticmethod
    def get_user_stats(user_id: str) -> DashboardStatsResponse:
        """
        Calculate dashboard stats for a specific user
        - Total Subscriptions: Count of distinct products with type 'subscription' in confirmed orders
        - Total Spent: Sum of confirmed orders TotalAmount
        - Total Due: Sum of pending orders TotalAmount
        """
        try:
            with get_db_cursor() as cursor:
                # 1. Total Spent (Confirmed)
                cursor.execute(
                    "SELECT SUM(TotalAmount) FROM Orders WHERE UserId = ? AND Status = 'Confirmed'",
                    (user_id,)
                )
                total_spent = cursor.fetchone()[0] or 0.0

                # 2. Total Due (Pending)
                cursor.execute(
                    "SELECT SUM(TotalAmount) FROM Orders WHERE UserId = ? AND Status = 'Pending'",
                    (user_id,)
                )
                total_due = cursor.fetchone()[0] or 0.0

                # 3. Total Subscriptions
                cursor.execute("""
                    SELECT COUNT(DISTINCT oi.ProductId)
                    FROM OrderItems oi
                    JOIN Orders o ON oi.OrderId = o.Id
                    JOIN Products p ON oi.ProductId = p.Id
                    WHERE o.UserId = ? AND o.Status = 'Confirmed'
                    AND p.ProductType = 'Service' -- Assuming subscriptions are 'Service' or similar
                """, (user_id,))
                total_subscriptions = cursor.fetchone()[0] or 0

                # 4. Spending History (e.g., last 6 months for bars)
                # This is a simplified version, ideally we group by month
                cursor.execute("""
                    SELECT TOP 6 TotalAmount 
                    FROM Orders 
                    WHERE UserId = ? AND Status = 'Confirmed' 
                    ORDER BY CreatedAt DESC
                """, (user_id,))
                history = [float(row[0]) for row in cursor.fetchall()]

                return DashboardStatsResponse(
                    total_subscriptions=total_subscriptions,
                    total_spent=float(total_spent),
                    total_due=float(total_due),
                    spending_history=history[::-1] # Reverse to show chronological
                )
        except Exception as e:
            logger.error(f"❌ Error fetching user stats: {str(e)}")
            raise e

    @staticmethod
    def create_order_from_cart(user_id: str, payment_intent_id: Optional[str] = None):
        """
        Convert cart items to an order (Simplified checkout)
        """
        try:
            with get_db_cursor() as cursor:
                # Get cart items
                cursor.execute("""
                    SELECT c.ProductId, c.Quantity, p.SalesPrice, c.SelectedVariantId, c.SelectedPlanName
                    FROM Cart c
                    JOIN Products p ON c.ProductId = p.Id
                    WHERE c.UserId = ?
                """, (user_id,))
                cart_items = cursor.fetchall()

                if not cart_items:
                    return None

                total_amount = sum(float(row[1]) * float(row[2]) for row in cart_items)

                # Create Order
                cursor.execute("""
                    INSERT INTO Orders (UserId, TotalAmount, Status)
                    OUTPUT INSERTED.Id
                    VALUES (?, ?, 'Confirmed')
                """, (user_id, total_amount))
                order_id = cursor.fetchone()[0]

                # Create Order Items
                for item in cart_items:
                    cursor.execute("""
                        INSERT INTO OrderItems (OrderId, ProductId, Quantity, Price, VariantId, PlanName)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (order_id, item[0], item[1], item[2], item[3], item[4]))

                # Link Payment if provided
                if payment_intent_id:
                    cursor.execute("""
                        UPDATE Payments
                        SET OrderId = ?
                        WHERE StripePaymentIntentId = ?
                    """, (order_id, payment_intent_id))

                # Clear Cart
                cursor.execute("DELETE FROM Cart WHERE UserId = ?", (user_id,))
                
                return order_id
        except Exception as e:
            logger.error(f"❌ Error creating order from cart: {str(e)}")
            raise e

    @staticmethod
    def get_user_orders(user_id: str) -> List[dict]:
        """Fetch all orders for a user"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT Id, TotalAmount, Status, CreatedAt
                    FROM Orders
                    WHERE UserId = ?
                    ORDER BY CreatedAt DESC
                """, (user_id,))
                
                orders = []
                for row in cursor.fetchall():
                    orders.append({
                        "id": str(row[0]),
                        "amount": float(row[1]),
                        "status": row[2],
                        "created_at": row[3].strftime("%d/%m/%Y") if row[3] else "N/A"
                    })
                return orders
        except Exception as e:
            logger.error(f"❌ Error fetching user orders: {str(e)}")
            raise e
    @staticmethod
    def get_order_details(order_id: str) -> Optional[dict]:
        """Fetch full order details using multiple safe queries"""
        try:
            # 1. Ensure order_id is an integer
            try:
                numeric_id = int(order_id)
            except (ValueError, TypeError):
                return None

            with get_db_cursor() as cursor:
                # 2. Fetch Order basic info
                cursor.execute("SELECT Id, UserId, TotalAmount, Status, CreatedAt FROM Orders WHERE Id = ?", (numeric_id,))
                order_row = cursor.fetchone()
                
                if not order_row:
                    return None
                
                order_id_val = order_row[0]
                user_id_val = order_row[1]
                total_amount = float(order_row[2])
                status = order_row[3]
                created_at = order_row[4].strftime("%d/%m/%Y %H:%M") if order_row[4] else "N/A"

                # 3. Fetch User info (Optional)
                user_info = {"email": "N/A", "name": "Valued Customer", "phone": "N/A"}
                if user_id_val:
                    cursor.execute("SELECT email, full_names FROM Users WHERE user_id = ?", (user_id_val,))
                    u_row = cursor.fetchone()
                    if u_row:
                        user_info["email"] = u_row[0]
                        user_info["name"] = u_row[1]

                # 4. Fetch Order Items
                items = []
                # Joining OrderItems with Products for names
                cursor.execute("""
                    SELECT oi.ProductId, p.Name, oi.Quantity, oi.Price, oi.VariantId, oi.PlanName 
                    FROM OrderItems oi 
                    LEFT JOIN Products p ON oi.ProductId = p.Id 
                    WHERE oi.OrderId = ?
                """, (numeric_id,))

                for item in cursor.fetchall():
                    items.append({
                        "product_id": str(item[0]),
                        "product_name": item[1] or "Unknown Product",
                        "quantity": float(item[2]),
                        "price": float(item[3]),
                        "variant_id": str(item[4]) if item[4] else None,
                        "plan_name": item[5]
                    })

                return {
                    "id": str(order_id_val),
                    "amount": total_amount,
                    "status": status,
                    "created_at": created_at,
                    "user": user_info,
                    "items": items
                }

        except Exception as e:
            logger.error(f"❌ Error fetching order details: {str(e)}")
            raise e
