from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user_token
from app.services.order_service import OrderService
from app.models.order_models import DashboardStatsResponse, OrdersListResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user_token)):
    """Get real-time dashboard stats for the current user"""
    try:
        # Resolve user_id from current_user
        user_id = str(current_user.get("user_id") or current_user.get("id"))
        return OrderService.get_user_stats(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout")
async def checkout(current_user: dict = Depends(get_current_user_token)):
    """Convert cart items into a confirmed order"""
    try:
        user_id = str(current_user.get("user_id") or current_user.get("id"))
        order_id = OrderService.create_order_from_cart(user_id)
        if not order_id:
            raise HTTPException(status_code=400, detail="Cart is empty")
        return {"message": "Checkout successful", "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=OrdersListResponse)
async def get_orders(current_user: dict = Depends(get_current_user_token)):
    """Get all orders for the current user"""
    try:
        user_id = str(current_user.get("user_id") or current_user.get("id"))
        orders = OrderService.get_user_orders(user_id)
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
