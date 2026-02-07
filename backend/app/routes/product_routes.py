from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional, List

from app.core.dependencies import get_current_user_token as get_current_user
from app.models.product_models import ProductCreate, ProductResponse, ProductListResponse
from app.services.product_service import ProductService

router = APIRouter()

@router.get("/categories", response_model=List[str])
async def get_categories():
    """
    Get all product categories
    """
    try:
        return ProductService.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ProductResponse)
async def create_product(
    request: Request,
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new product
    """
    try:
        # Pass the user_id from the token (current_user)
        product = ProductService.create_product(product_data, current_user["user_id"])
        if not product:
            raise HTTPException(status_code=400, detail="Failed to create product")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None
):
    """
    Get paginated list of products
    """
    try:
        return ProductService.get_all_products(page, size, search)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recurring-templates")
async def get_recurring_templates(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all recurring plan templates
    """
    try:
        return ProductService.get_recurring_plan_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int
):
    """
    Get a single product by ID
    """
    try:
        product = ProductService.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
