from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    amount: float
    order_id: Optional[int] = None
    currency: str = "INR"
    metadata: Optional[dict] = None

class PaymentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
    status: str
