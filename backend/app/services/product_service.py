"""
Product Service
Business logic for product management
"""
from typing import Optional, List
import logging

from app.core.database import get_db_cursor
from app.models.product_models import ProductCreate, ProductResponse, ProductListResponse

logger = logging.getLogger(__name__)

class ProductService:
    """Service for Product Management"""

    @staticmethod
    def create_product(data: ProductCreate, user_id: str) -> Optional[ProductResponse]:
        """
        Create a new product using SP_CreateProduct
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    DECLARE @ProductId INT;
                    EXEC @ProductId = SP_CreateProduct
                        @Name = ?,
                        @ProductType = ?,
                        @SalesPrice = ?,
                        @CostPrice = ?,
                        @Tax = ?,
                        @UserId = ?;
                    
                    SELECT @ProductId;
                    """,
                    (
                        data.name, 
                        data.product_type, 
                        data.sales_price, 
                        data.cost_price, 
                        data.tax, 
                        user_id
                    )
                )
                row = cursor.fetchone()
                
                if not row or not row[0]:
                    return None
                
                product_id = row[0]

                # Insert Recurring Plans
                if data.recurring_plans:
                    for plan in data.recurring_plans:
                        cursor.execute(
                            """
                            INSERT INTO ProductRecurringPlans (ProductId, PlanName, Price, MinQty, StartDate, EndDate)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                product_id,
                                plan.plan_name,
                                plan.price,
                                plan.min_qty,
                                plan.start_date,
                                plan.end_date
                            )
                        )

                # Insert Variants
                if data.variants:
                    for variant in data.variants:
                        cursor.execute(
                            """
                            INSERT INTO ProductVariants (ProductId, Attribute, Value, ExtraPrice)
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                product_id,
                                variant.attribute,
                                variant.value,
                                variant.extra_price
                            )
                        )

                # Fetch created product
                cursor.execute(
                     """
                    SELECT 
                        Id, Name, ProductType, SalesPrice, CostPrice, Tax, 
                        CreatedByEmployeeId, CreatedAt, ModifiedAt, IsActive
                    FROM Products
                    WHERE Id = ?;
                    """,
                    (product_id,)
                )
                row = cursor.fetchone()

                sales_price = float(row[3]) if row[3] is not None else 0.0
                cost_price = float(row[4]) if row[4] is not None else 0.0
                profit_margin = sales_price - cost_price

                return ProductResponse(
                    id=row[0],
                    name=row[1],
                    product_type=row[2],
                    sales_price=sales_price,
                    cost_price=cost_price,
                    profit_margin=profit_margin,
                    tax=row[5],
                    created_by_employee_id=row[6],
                    created_at=row[7],
                    modified_at=row[8],
                    is_active=bool(row[9])
                )
        except Exception as e:
            logger.error(f"❌ Error creating product: {str(e)}")
            raise e

    @staticmethod
    def get_all_products(page: int = 1, size: int = 10, search: str = None) -> ProductListResponse:
        """Fetch paginated list of products"""
        offset = (page - 1) * size
        try:
            with get_db_cursor() as cursor:
                # Count Query
                count_sql = "SELECT COUNT(*) FROM Products WHERE IsActive = 1"
                params = []
                if search:
                    count_sql += " AND (Name LIKE ?)"
                    params.append(f"%{search}%")
                
                cursor.execute(count_sql, tuple(params))
                total = cursor.fetchone()[0]

                # Fetch Query
                sql = """
                SELECT 
                    Id, Name, ProductType, SalesPrice, CostPrice, Tax, 
                    CreatedByEmployeeId, CreatedAt, ModifiedAt, IsActive
                FROM Products
                WHERE IsActive = 1
                """
                
                if search:
                    sql += " AND (Name LIKE ?)"
                
                sql += " ORDER BY CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
                params.extend([offset, size])
                
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall()

                items = []
                for row in rows:
                    sales_price = float(row[3]) if row[3] is not None else 0.0
                    cost_price = float(row[4]) if row[4] is not None else 0.0
                    profit_margin = sales_price - cost_price

                    items.append(ProductResponse(
                        id=row[0],
                        name=row[1],
                        product_type=row[2],
                        sales_price=sales_price,
                        cost_price=cost_price,
                        profit_margin=profit_margin,
                        tax=row[5],
                        created_by_employee_id=row[6],
                        created_at=row[7],
                        modified_at=row[8],
                        is_active=bool(row[9])
                    ))

                return ProductListResponse(items=items, total=total, page=page, size=size)

        except Exception as e:
            logger.error(f"❌ Error listing products: {str(e)}")
            raise e

    @staticmethod
    def get_recurring_plan_templates() -> List[dict]:
        """Fetch recurring plan templates"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT Id, PlanName, DurationMonths, PriceMultiplier FROM RecurringPlanTemplates WHERE IsActive = 1"
                )
                rows = cursor.fetchall()
                
                templates = []
                for row in rows:
                    templates.append({
                        "id": row[0],
                        "plan_name": row[1],
                        "duration_months": row[2],
                        "price_multiplier": float(row[3])
                    })
                return templates
        except Exception as e:
            logger.error(f"❌ Error fetching recurring plan templates: {str(e)}")
            raise e
