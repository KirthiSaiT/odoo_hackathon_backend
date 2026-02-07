from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user_token as get_current_user
from app.models.cart_models import CartItemCreate, CartItemUpdate, CartItemResponse, CartSummaryResponse
from app.services.cart_service import CartService

router = APIRouter()

@router.post("/", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_item: CartItemCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add item to cart or update quantity if already exists
    """
    try:
        user_id = current_user["user_id"]
        result = CartService.add_to_cart(user_id, cart_item)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to add item to cart")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=CartSummaryResponse)
async def get_cart(
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's cart with all items and summary
    """
    try:
        user_id = current_user["user_id"]
        return CartService.get_cart(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: int,
    update_data: CartItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update cart item quantity
    """
    try:
        user_id = current_user["user_id"]
        result = CartService.update_cart_item(user_id, cart_item_id, update_data.quantity)
        if not result:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    cart_item_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Remove item from cart
    """
    try:
        user_id = current_user["user_id"]
        success = CartService.remove_from_cart(user_id, cart_item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: dict = Depends(get_current_user)
):
    """
    Clear all items from cart
    """
    try:
        user_id = current_user["user_id"]
        CartService.clear_cart(user_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
