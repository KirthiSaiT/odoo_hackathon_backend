"""
Role & Rights Routes
API endpoints for role and access rights management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, List

from app.core.dependencies import require_role
from app.models.shared_models import LookupResponse, StatsResponse
from app.models.role_models import (
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    UserRight, UserRightsResponse
)
from app.services.role_service import RoleService

router = APIRouter(prefix="/admin", tags=["Roles & Rights"])


# =====================
# LOOKUPS & STATS
# =====================

@router.get(
    "/lookups",
    response_model=LookupResponse,
    summary="Get all lookup lists",
    description="Fetch all dropdown options for employee forms"
)
async def get_lookups(
    current_user: Annotated[dict, Depends(require_role("ADMIN", "EMPLOYEE"))]
):
    try:
        return RoleService.get_lookups()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get dashboard stats",
    description="Fetch counts for users, employees, roles, modules"
)
async def get_stats(
    current_user: Annotated[dict, Depends(require_role("ADMIN", "EMPLOYEE"))]
):
    try:
        return RoleService.get_dashboard_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================
# RIGHTS ENDPOINTS
# =====================

@router.get(
    "/rights/user/{user_id}",
    response_model=UserRightsResponse,
    summary="Get user access rights"
)
async def get_user_rights(
    user_id: str,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        return RoleService.get_user_rights(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/rights/me",
    response_model=UserRightsResponse,
    summary="Get current user's access rights",
    description="Fetch access rights for the currently logged-in user based on their token"
)
async def get_my_rights(
    current_user: Annotated[dict, Depends(require_role("ADMIN", "EMPLOYEE", "USER"))]
):
    """
    Returns the access rights for the currently authenticated user.
    Used by frontend to determine which actions to show/hide.
    """
    try:
        user_id = current_user.get("id") or current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )
        return RoleService.get_user_rights(str(user_id))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/rights/user/{user_id}",
    summary="Save user access rights"
)
async def save_user_rights(
    user_id: str,
    rights: List[UserRight],
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        RoleService.save_user_rights(user_id, rights)
        return {"message": "Rights saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# =====================
# ROLE CRUD ENDPOINTS
# =====================

@router.get(
    "/roles",
    response_model=RoleListResponse,
    summary="List roles",
    description="Get paginated list of system roles"
)
async def list_roles(
    current_user: Annotated[dict, Depends(require_role("ADMIN"))],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str = Query(None)
):
    try:
        return RoleService.get_all_roles(page, size, search)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new role",
    description="Create a new system role"
)
async def create_role(
    data: RoleCreate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        return RoleService.create_role(data)
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
    "/roles/{role_id}",
    response_model=RoleResponse,
    summary="Update role details"
)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        updated_role = RoleService.update_role(role_id, data)
        if not updated_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return updated_role
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/roles/{role_id}",
    summary="Delete role (soft delete)"
)
async def delete_role(
    role_id: int,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        RoleService.delete_role(role_id)
        return {"message": "Role deleted successfully"}
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
