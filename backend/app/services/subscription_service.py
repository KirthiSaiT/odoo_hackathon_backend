"""
Subscription Service
Business logic for subscription management
"""
from typing import Optional
from app.models.subscription_models import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionListResponse
)
from app.core.database import get_db_cursor
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for Subscription Management"""

    @staticmethod
    def create_subscription(data: SubscriptionCreate) -> Optional[SubscriptionResponse]:
        """Create a new subscription"""
        try:
            with get_db_cursor() as cursor:
                # Generate subscription number
                cursor.execute("SELECT COUNT(*) FROM Subscriptions")
                count = cursor.fetchone()[0]
                subscription_number = f"SO{str(count + 1).zfill(4)}"

                # Insert subscription
                cursor.execute("""
                    INSERT INTO Subscriptions (
                        SubscriptionNumber, CustomerId, QuotationTemplate, ExpirationDate,
                        RecurringPlan, PaymentTerm, TotalPrice, Salesperson, StartDate,
                        OrderDate, NextInvoiceDate,
                        PaymentMethod, PaymentDone, Status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    subscription_number,
                    data.customer_id,
                    data.quotation_template,
                    data.expiration_date,
                    data.recurring_plan,
                    data.payment_term,
                    data.total_price,
                    data.salesperson,
                    data.start_date,
                    data.order_date,
                    data.next_invoice_date,
                    data.payment_method,
                    data.payment_done,
                    data.status
                ))
                
                cursor.execute("SELECT @@IDENTITY")
                subscription_id = cursor.fetchone()[0]
                
                # Insert order lines
                for line in data.order_lines:
                    cursor.execute("""
                        INSERT INTO SubscriptionOrderLines (
                            SubscriptionId, ProductId, ProductName, Quantity,
                            UnitPrice, Discount, Taxes, Amount
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        subscription_id,
                        line.product_id,
                        line.product_name,
                        line.quantity,
                        line.unit_price,
                        line.discount,
                        line.taxes,
                        line.amount
                    ))
                
                return SubscriptionService.get_subscription_by_id(subscription_id)
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise e

    @staticmethod
    def get_all_subscriptions(page: int = 1, size: int = 10, search: str = None) -> SubscriptionListResponse:
        """Get paginated list of subscriptions"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                # Count query
                count_sql = "SELECT COUNT(*) FROM Subscriptions WHERE IsActive = 1"
                params = []
                if search:
                    count_sql += " AND (SubscriptionNumber LIKE ? OR Status LIKE ?)"
                    params.extend([f"%{search}%", f"%{search}%"])
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                # Fetch query
                sql = """
                SELECT 
                    s.Id, s.SubscriptionNumber, s.CustomerId, s.QuotationTemplate,
                    s.ExpirationDate, s.RecurringPlan, s.PaymentTerm, s.TotalPrice,
                    s.Salesperson, s.StartDate, s.PaymentMethod, s.PaymentDone,
                    s.Status, s.CreatedAt, s.ModifiedAt, s.IsActive,
                    s.OrderDate, s.NextInvoiceDate,
                    u.name as CustomerName
                FROM Subscriptions s
                LEFT JOIN Users u ON s.CustomerId = u.user_id
                WHERE s.IsActive = 1
                """
                
                if search:
                    sql += " AND (s.SubscriptionNumber LIKE ? OR s.Status LIKE ?)"
                
                sql += " ORDER BY s.CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, size])
                
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    items.append(SubscriptionResponse(
                        id=row[0],
                        subscription_number=row[1],
                        customer_id=str(row[2]),
                        customer_name=row[16] or "Unknown",
                        quotation_template=row[3],
                        expiration_date=row[4],
                        recurring_plan=row[5],
                        payment_term=row[6],
                        total_price=float(row[7]),
                        salesperson=row[8],
                        start_date=row[9],
                        payment_method=row[10],
                        payment_done=bool(row[11]),
                        status=row[12],
                        created_at=row[13],
                        modified_at=row[14],
                        is_active=bool(row[15]),
                        order_date=row[16],
                        next_invoice_date=row[17]
                    ))

                return SubscriptionListResponse(items=items, total=total, page=page, size=size)
        except Exception as e:
            logger.error(f"Error listing subscriptions: {str(e)}")
            raise e

    @staticmethod
    def get_subscription_by_id(subscription_id: int) -> Optional[SubscriptionResponse]:
        """Get subscription by ID"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        s.Id, s.SubscriptionNumber, s.CustomerId, s.QuotationTemplate,
                        s.ExpirationDate, s.RecurringPlan, s.PaymentTerm, s.TotalPrice,
                        s.Salesperson, s.StartDate, s.PaymentMethod, s.PaymentDone,
                        s.Status, s.CreatedAt, s.ModifiedAt, s.IsActive,
                        s.OrderDate, s.NextInvoiceDate,
                        u.name as CustomerName
                    FROM Subscriptions s
                    LEFT JOIN Users u ON s.CustomerId = u.user_id
                    WHERE s.Id = ? AND s.IsActive = 1
                """, (subscription_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None

                return SubscriptionResponse(
                    id=row[0],
                    subscription_number=row[1],
                    customer_id=str(row[2]),
                    customer_name=row[16] or "Unknown",
                    quotation_template=row[3],
                    expiration_date=row[4],
                    recurring_plan=row[5],
                    payment_term=row[6],
                    total_price=float(row[7]),
                    salesperson=row[8],
                    start_date=row[9],
                    payment_method=row[10],
                    payment_done=bool(row[11]),
                    status=row[12],
                    created_at=row[13],
                    modified_at=row[14],
                    is_active=bool(row[15]),
                    order_date=row[16],
                    next_invoice_date=row[17]
                )
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            raise e

    @staticmethod
    def update_subscription(subscription_id: int, data: SubscriptionUpdate) -> Optional[SubscriptionResponse]:
        """Update subscription"""
        try:
            with get_db_cursor() as cursor:
                update_fields = []
                params = []

                if data.quotation_template is not None:
                    update_fields.append("QuotationTemplate = ?")
                    params.append(data.quotation_template)
                if data.expiration_date is not None:
                    update_fields.append("ExpirationDate = ?")
                    params.append(data.expiration_date)
                if data.recurring_plan is not None:
                    update_fields.append("RecurringPlan = ?")
                    params.append(data.recurring_plan)
                if data.payment_term is not None:
                    update_fields.append("PaymentTerm = ?")
                    params.append(data.payment_term)
                if data.total_price is not None:
                    update_fields.append("TotalPrice = ?")
                    params.append(data.total_price)
                if data.salesperson is not None:
                    update_fields.append("Salesperson = ?")
                    params.append(data.salesperson)
                if data.start_date is not None:
                    update_fields.append("StartDate = ?")
                    params.append(data.start_date)
                if data.order_date is not None:
                    update_fields.append("OrderDate = ?")
                    params.append(data.order_date)
                if data.next_invoice_date is not None:
                    update_fields.append("NextInvoiceDate = ?")
                    params.append(data.next_invoice_date)
                if data.payment_method is not None:
                    update_fields.append("PaymentMethod = ?")
                    params.append(data.payment_method)
                if data.payment_done is not None:
                    update_fields.append("PaymentDone = ?")
                    params.append(data.payment_done)
                if data.status is not None:
                    update_fields.append("Status = ?")
                    params.append(data.status)

                # Update Order Lines if provided
                if data.order_lines is not None:
                    # 1. Delete existing lines
                    cursor.execute("DELETE FROM SubscriptionOrderLines WHERE SubscriptionId = ?", (subscription_id,))
                    
                    # 2. Insert new lines
                    for line in data.order_lines:
                        cursor.execute("""
                            INSERT INTO SubscriptionOrderLines (
                                SubscriptionId, ProductId, ProductName, Quantity,
                                UnitPrice, Discount, Taxes, Amount
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            subscription_id,
                            line.product_id,
                            line.product_name,
                            line.quantity,
                            line.unit_price,
                            line.discount,
                            line.taxes,
                            line.amount
                        ))

                if not update_fields:
                    return SubscriptionService.get_subscription_by_id(subscription_id)

                update_fields.append("ModifiedAt = GETDATE()")
                params.append(subscription_id)

                sql = f"UPDATE Subscriptions SET {', '.join(update_fields)} WHERE Id = ?"
                cursor.execute(sql, tuple(params))

                return SubscriptionService.get_subscription_by_id(subscription_id)
        except Exception as e:
            logger.error(f"Error updating subscription: {str(e)}")
            raise e

    @staticmethod
    def delete_subscription(subscription_id: int) -> bool:
        """Soft delete subscription"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    UPDATE Subscriptions 
                    SET IsActive = 0, ModifiedAt = GETDATE()
                    WHERE Id = ?
                """, (subscription_id,))
                return True
        except Exception as e:
            logger.error(f"Error deleting subscription: {str(e)}")
            raise e
