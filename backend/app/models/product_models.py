"""
Product Models
Pydantic schemas for product management
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    """Base product fields"""
    name: str = Field(..., min_length=2, max_length=255)
    product_type: str = Field(..., description="Storable Product, Consumable, or Service")
    sales_price: Optional[float] = 0.00
    cost_price: Optional[float] = 0.00
    tax: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True

class RecurringPlanBase(BaseModel):
    """Base fields for recurring plans"""
    plan_name: str
    price: float
    min_qty: int = 1
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class RecurringPlanCreate(RecurringPlanBase):
    """Schema for creating a recurring plan"""
    pass

class ProductVariantBase(BaseModel):
    """Base fields for product variants"""
    attribute: str
    value: str
    extra_price: Optional[float] = 0.00

class ProductVariantCreate(ProductVariantBase):
    """Schema for creating a product variant"""
    pass

class ProductCreate(ProductBase):
    """Schema for creating a product"""
    recurring_plans: Optional[List[RecurringPlanCreate]] = []
    variants: Optional[List[ProductVariantCreate]] = []
    main_image: Optional[str] = None
    sub_images: Optional[List[str]] = []

class RecurringPlanTemplate(BaseModel):
    """Schema for recurring plan templates"""
    id: int
    plan_name: str
    duration_months: int
    price_multiplier: float

class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    profit_margin: Optional[float] = 0.00
    created_by_employee_id: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    main_image: Optional[str] = None
    sub_images: Optional[List[str]] = []

class ProductListResponse(BaseModel):
    """List response for products"""
    items: List[ProductResponse]
    total: int
    page: int
    size: int
