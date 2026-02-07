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
    def _log_debug(message: str):
        try:
            with open("debug_log.txt", "a") as f:
                f.write(f"{message}\n")
        except:
            pass

    @staticmethod
    def create_product(data: ProductCreate, user_id: str) -> Optional[ProductResponse]:
        """
        Create a new product using SP_CreateProduct
        """
        try:
            ProductService._log_debug(f"Creating Product: {data.name}")
            ProductService._log_debug(f"  - Main Image: {data.main_image}")
            ProductService._log_debug(f"  - Sub Images: {data.sub_images}")

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
                ProductService._log_debug(f"  - Created Product ID: {product_id}")

                # ... (rest of logic)

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
                
                # Update Main Image
                if data.main_image:
                    cursor.execute(
                        "UPDATE Products SET MainImage = ? WHERE Id = ?",
                        (data.main_image, product_id)
                    )

                # Insert Sub Images
                if data.sub_images:
                    for img_url in data.sub_images:
                        cursor.execute(
                            "INSERT INTO ProductSubImages (ProductId, ImageURL) VALUES (?, ?)",
                            (product_id, img_url)
                        )

                # Fetch created product
                cursor.execute(
                     """
                    SELECT 
                        Id, Name, ProductType, SalesPrice, CostPrice, Tax, 
                        CreatedByEmployeeId, CreatedAt, ModifiedAt, IsActive, MainImage
                    FROM Products
                    WHERE Id = ?;
                    """,
                    (product_id,)
                )
                row = cursor.fetchone()

                sales_price = float(row[3]) if row[3] is not None else 0.0
                cost_price = float(row[4]) if row[4] is not None else 0.0
                profit_margin = sales_price - cost_price

                # Fetch Sub Images
                cursor.execute("SELECT ImageURL FROM ProductSubImages WHERE ProductId = ?", (product_id,))
                sub_images = [r[0] for r in cursor.fetchall()]

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
                    is_active=bool(row[9]),
                    main_image=row[10],
                    sub_images=sub_images
                )
        except Exception as e:
            logger.error(f"❌ Error creating product: {str(e)}")
            raise e

    @staticmethod
    def get_all_products(page: int = 1, size: int = 10, search: str = None) -> ProductListResponse:
        """Fetch paginated list of products"""
        offset = (page - 1) * size
        try:
            ProductService._log_debug(f"Fetching all products: page={page}, size={size}")
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
                    CreatedByEmployeeId, CreatedAt, ModifiedAt, IsActive, MainImage
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
                        is_active=bool(row[9]),
                        main_image=row[10]
                    ))

                return ProductListResponse(items=items, total=total, page=page, size=size)

        except Exception as e:
            ProductService._log_debug(f"❌ Error listing products: {str(e)}")
            logger.error(f"❌ Error listing products: {str(e)}")
            raise e

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[ProductResponse]:
        """Fetch a single product by ID"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        Id, Name, ProductType, SalesPrice, CostPrice, Tax, 
                        CreatedByEmployeeId, CreatedAt, ModifiedAt, IsActive, MainImage
                    FROM Products
                    WHERE Id = ? AND IsActive = 1
                    """,
                    (product_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    return None

                sales_price = float(row[3]) if row[3] is not None else 0.0
                cost_price = float(row[4]) if row[4] is not None else 0.0
                profit_margin = sales_price - cost_price

                # Fetch Sub Images
                cursor.execute("SELECT ImageURL FROM ProductSubImages WHERE ProductId = ?", (product_id,))
                sub_images = [r[0] for r in cursor.fetchall()]

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
                    is_active=bool(row[9]),
                    main_image=row[10],
                    sub_images=sub_images
                )
        except Exception as e:
            logger.error(f"❌ Error fetching product by ID: {str(e)}")
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
