from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user_token as get_current_user
from app.models.payment_models import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    responses={404: {"description": "Not found"}},
)

@router.post("/create-intent", response_model=PaymentResponse)
async def create_payment_intent(data: PaymentCreate, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user["user_id"]
        return PaymentService.create_payment_intent(data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/confirm/{payment_intent_id}")
async def confirm_payment(payment_intent_id: str, current_user: dict = Depends(get_current_user)):
    try:
        status = PaymentService.confirm_payment(payment_intent_id)
        return {"status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
