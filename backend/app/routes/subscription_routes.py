"""
Subscription Routes
API endpoints for subscription management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.models.subscription_models import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionListResponse
)
from app.services.subscription_service import SubscriptionService
from app.core.dependencies import get_current_user_token

router = APIRouter()


@router.post("/", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_user: dict = Depends(get_current_user_token)
):
    """Create a new subscription"""
    try:
        return SubscriptionService.create_subscription(subscription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=SubscriptionListResponse)
async def get_subscriptions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user_token)
):
    """Get paginated list of subscriptions"""
    try:
        return SubscriptionService.get_all_subscriptions(page, size, search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: dict = Depends(get_current_user_token)
):
    """Get subscription by ID"""
    try:
        subscription = SubscriptionService.get_subscription_by_id(subscription_id)
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    current_user: dict = Depends(get_current_user_token)
):
    """Update subscription"""
    try:
        updated = SubscriptionService.update_subscription(subscription_id, subscription)
        if not updated:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{subscription_id}")
async def delete_subscription(
    subscription_id: int,
    current_user: dict = Depends(get_current_user_token)
):
    """Delete subscription"""
    try:
        success = SubscriptionService.delete_subscription(subscription_id)
        if not success:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return {"message": "Subscription deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
