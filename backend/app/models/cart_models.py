"""
Cart Models
Pydantic schemas for shopping cart management
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class CartItemCreate(BaseModel):
    """Schema for adding item to cart"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(1, gt=0)
    selected_variant_id: Optional[int] = None
    selected_plan_name: Optional[str] = None

class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    """Schema for cart item response with product details"""
    id: int
    user_id: str
    product_id: int
    product_name: str
    product_type: str
    product_image: Optional[str] = None
    sales_price: float
    quantity: int
    selected_variant_id: Optional[int] = None
    selected_plan_name: Optional[str] = None
    added_at: datetime
    item_total: float  # quantity * price

class CartSummaryResponse(BaseModel):
    """Schema for complete cart summary"""
    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    tax_amount: float
    total: float
