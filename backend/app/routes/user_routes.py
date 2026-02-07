"""
User Routes
API endpoints for user configuration management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from app.core.dependencies import require_role
from app.models.user_models import (
    UserCreate, UserUpdate, UserResponse, UserListResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Users"])


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="List users",
    description="Get paginated list of system users"
)
async def list_users(
    current_user: Annotated[dict, Depends(require_role("ADMIN"))],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str = Query(None)
):
    try:
        return UserService.get_all_users(page, size, search)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user",
    description="Create a new system user (admin, employee, portal)"
)
async def create_user(
    data: UserCreate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        return UserService.create_user(data, created_by_str='ADMIN')
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Update user details"
)
async def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        updated_user = UserService.update_user(user_id, data)
        if not updated_user:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/users/{user_id}",
    summary="Delete user (soft delete)"
)
async def delete_user(
    user_id: str,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        UserService.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
