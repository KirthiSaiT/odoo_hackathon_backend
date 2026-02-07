"""
Subscription Models
Pydantic models for subscription management
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class OrderLineItem(BaseModel):
    """Schema for order line item"""
    product_id: Optional[int] = None
    product_name: str = ""
    quantity: int = 1
    unit_price: float = 0
    discount: float = 0
    taxes: float = 0
    amount: float = 0


class SubscriptionCreate(BaseModel):
    """Schema for creating a new subscription"""
    customer_id: str
    quotation_template: Optional[str] = None
    expiration_date: date
    recurring_plan: str  # Monthly, Yearly, etc.
    payment_term: Optional[str] = None
    total_price: float = 0
    salesperson: Optional[str] = None
    start_date: date
    order_date: Optional[date] = None
    next_invoice_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_done: bool = False
    status: str = "Quotation"
    order_lines: List[OrderLineItem] = []


class SubscriptionUpdate(BaseModel):
    """Schema for updating subscription"""
    quotation_template: Optional[str] = None
    expiration_date: Optional[date] = None
    recurring_plan: Optional[str] = None
    payment_term: Optional[str] = None
    total_price: Optional[float] = None
    salesperson: Optional[str] = None
    start_date: Optional[date] = None
    order_date: Optional[date] = None
    next_invoice_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_done: Optional[bool] = None
    status: Optional[str] = None
    order_lines: Optional[List[OrderLineItem]] = None


class SubscriptionResponse(BaseModel):
    """Schema for subscription response with details"""
    id: int
    subscription_number: str
    customer_id: str
    customer_name: str
    quotation_template: Optional[str] = None
    expiration_date: date
    recurring_plan: str
    payment_term: Optional[str] = None
    total_price: float
    salesperson: Optional[str] = None
    start_date: date
    order_date: Optional[date] = None
    next_invoice_date: Optional[date] = None
    payment_method: Optional[str] = None
    payment_done: bool
    status: str
    created_at: datetime
    modified_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Schema for paginated subscription list"""
    items: list[SubscriptionResponse]
    total: int
    page: int
    size: int
