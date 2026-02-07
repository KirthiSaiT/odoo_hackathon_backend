"""
Cart Service
Business logic for shopping cart management
"""
from typing import Optional, List
import logging

from app.core.database import get_db_cursor
from app.models.cart_models import CartItemCreate, CartItemResponse, CartSummaryResponse

logger = logging.getLogger(__name__)

class CartService:
    """Service for Cart Management"""

    @staticmethod
    def add_to_cart(user_id: str, cart_item: CartItemCreate) -> Optional[CartItemResponse]:
        """
        Add item to cart or update quantity if already exists
        """
        try:
            with get_db_cursor() as cursor:
                # Check if item already exists in cart
                cursor.execute(
                    """
                    SELECT Id, Quantity FROM Cart
                    WHERE UserId = ? AND ProductId = ?
                    AND (SelectedVariantId = ? OR (SelectedVariantId IS NULL AND ? IS NULL))
                    AND (SelectedPlanName = ? OR (SelectedPlanName IS NULL AND ? IS NULL))
                    """,
                    (user_id, cart_item.product_id, 
                     cart_item.selected_variant_id, cart_item.selected_variant_id,
                     cart_item.selected_plan_name, cart_item.selected_plan_name)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update quantity
                    new_quantity = existing[1] + cart_item.quantity
                    cursor.execute(
                        "UPDATE Cart SET Quantity = ? WHERE Id = ?",
                        (new_quantity, existing[0])
                    )
                    cart_id = existing[0]
                else:
                    # Insert new cart item
                    cursor.execute(
                        """
                        INSERT INTO Cart (UserId, ProductId, Quantity, SelectedVariantId, SelectedPlanName)
                        OUTPUT INSERTED.Id
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (user_id, cart_item.product_id, cart_item.quantity,
                         cart_item.selected_variant_id, cart_item.selected_plan_name)
                    )
                    cart_id = cursor.fetchone()[0]

                # Fetch the cart item with product details
                return CartService._get_cart_item_by_id(cursor, cart_id)

        except Exception as e:
            logger.error(f"❌ Error adding to cart: {str(e)}")
            raise e

    @staticmethod
    def get_cart(user_id: str) -> CartSummaryResponse:
        """Get user's cart with all items and summary"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        c.Id, c.UserId, c.ProductId, c.Quantity,
                        c.SelectedVariantId, c.SelectedPlanName, c.AddedAt,
                        p.Name, p.ProductType, p.SalesPrice, p.MainImage
                    FROM Cart c
                    INNER JOIN Products p ON c.ProductId = p.Id
                    WHERE c.UserId = ?
                    ORDER BY c.AddedAt DESC
                    """,
                    (user_id,)
                )
                rows = cursor.fetchall()

                items = []
                subtotal = 0.0

                for row in rows:
                    sales_price = float(row[9]) if row[9] else 0.0
                    quantity = row[3]
                    item_total = sales_price * quantity
                    subtotal += item_total

                    items.append(CartItemResponse(
                        id=row[0],
                        user_id=row[1],
                        product_id=row[2],
                        quantity=quantity,
                        selected_variant_id=row[4],
                        selected_plan_name=row[5],
                        added_at=row[6],
                        product_name=row[7],
                        product_type=row[8],
                        sales_price=sales_price,
                        product_image=row[10],
                        item_total=item_total
                    ))

                # Calculate tax (assuming 10% for now, can be made dynamic)
                tax_amount = subtotal * 0.10
                total = subtotal + tax_amount

                return CartSummaryResponse(
                    items=items,
                    total_items=len(items),
                    subtotal=subtotal,
                    tax_amount=tax_amount,
                    total=total
                )

        except Exception as e:
            logger.error(f"❌ Error fetching cart: {str(e)}")
            raise e

    @staticmethod
    def update_cart_item(user_id: str, cart_item_id: int, quantity: int) -> Optional[CartItemResponse]:
        """Update cart item quantity"""
        try:
            with get_db_cursor() as cursor:
                # Verify ownership
                cursor.execute(
                    "SELECT Id FROM Cart WHERE Id = ? AND UserId = ?",
                    (cart_item_id, user_id)
                )
                if not cursor.fetchone():
                    return None

                # Update quantity
                cursor.execute(
                    "UPDATE Cart SET Quantity = ? WHERE Id = ?",
                    (quantity, cart_item_id)
                )

                return CartService._get_cart_item_by_id(cursor, cart_item_id)

        except Exception as e:
            logger.error(f"❌ Error updating cart item: {str(e)}")
            raise e

    @staticmethod
    def remove_from_cart(user_id: str, cart_item_id: int) -> bool:
        """Remove item from cart"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM Cart WHERE Id = ? AND UserId = ?",
                    (cart_item_id, user_id)
                )
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"❌ Error removing from cart: {str(e)}")
            raise e

    @staticmethod
    def clear_cart(user_id: str) -> bool:
        """Clear all items from user's cart"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("DELETE FROM Cart WHERE UserId = ?", (user_id,))
                return True

        except Exception as e:
            logger.error(f"❌ Error clearing cart: {str(e)}")
            raise e

    @staticmethod
    def _get_cart_item_by_id(cursor, cart_item_id: int) -> Optional[CartItemResponse]:
        """Helper method to fetch cart item with product details"""
        cursor.execute(
            """
            SELECT 
                c.Id, c.UserId, c.ProductId, c.Quantity,
                c.SelectedVariantId, c.SelectedPlanName, c.AddedAt,
                p.Name, p.ProductType, p.SalesPrice, p.MainImage
            FROM Cart c
            INNER JOIN Products p ON c.ProductId = p.Id
            WHERE c.Id = ?
            """,
            (cart_item_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        sales_price = float(row[9]) if row[9] else 0.0
        quantity = row[3]

        return CartItemResponse(
            id=row[0],
            user_id=row[1],
            product_id=row[2],
            quantity=quantity,
            selected_variant_id=row[4],
            selected_plan_name=row[5],
            added_at=row[6],
            product_name=row[7],
            product_type=row[8],
            sales_price=sales_price,
            product_image=row[10],
            item_total=sales_price * quantity
        )
