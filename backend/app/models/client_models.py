"""
Client Management Models
Pydantic schemas for client management and related operations
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.user_models import UserCreate

# =====================
# CLIENT MODELS
# =====================

class ClientBase(BaseModel):
    """Base client fields"""
    client_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    contact_person: Optional[str] = Field(None, max_length=100)
    subscription_status: Optional[str] = "Pending"  # Active, Inactive, Pending
    is_active: bool = True

class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    password: str = Field(..., min_length=6, description="Password for the associated user account")
    subscription_plan_id: Optional[int] = None # Optional subscription selection during creation
    product_id: Optional[int] = None # Selected Project/Product
    amount: Optional[float] = 0.0 # Agreed Amount
    payment_frequency: Optional[str] = "Monthly" # Monthly, Yearly, Quarterly
    subscription_start_date: Optional[datetime] = None

class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    client_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    contact_person: Optional[str] = Field(None, max_length=100)
    subscription_status: Optional[str] = None
    is_active: Optional[bool] = None
    # Subscription Updates
    product_id: Optional[int] = None
    amount: Optional[float] = None
    payment_frequency: Optional[str] = None
    subscription_start_date: Optional[datetime] = None

class ClientResponse(ClientBase):
    """Schema for client response"""
    id: int
    user_id: str
    created_at: datetime
    created_by: Optional[str] = None

class ClientListResponse(BaseModel):
    """List response with pagination metadata"""
    items: List[ClientResponse]
    total: int
    page: int
    size: int

# =====================
# PAYMENT MODELS
# =====================

class PaymentBase(BaseModel):
    """Base payment fields"""
    amount: float
    payment_method: str = Field(..., description="Credit Card, Bank Transfer, PayPal, etc.")
    transaction_id: Optional[str] = None
    payment_date: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    """Schema for recording a payment"""
    client_id: int
    subscription_id: Optional[int] = None

class PaymentResponse(PaymentBase):
    """Schema for payment response"""
    id: int
    client_id: int
    created_at: datetime
    created_by: Optional[str] = None
