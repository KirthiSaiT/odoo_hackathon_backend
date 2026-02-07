from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float
    variant_id: Optional[int] = None
    plan_name: Optional[str] = None

class OrderCreate(BaseModel):
    user_id: str
    items: List[OrderItemBase]
    total_amount: float

class OrderResponse(BaseModel):
    id: int
    user_id: str
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemBase] = []

class DashboardStatsResponse(BaseModel):
    total_subscriptions: int
    total_spent: float
    total_due: float
    # Data for the animated bars
    spending_history: Optional[List[float]] = []

class OrderListItem(BaseModel):
    id: str
    amount: float
    status: str
    created_at: str

class OrdersListResponse(BaseModel):
    orders: List[OrderListItem]

class CheckoutRequest(BaseModel):
    payment_intent_id: Optional[str] = None
