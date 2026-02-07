"""
Admin/Employee Routes
API endpoints for employee management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, List

from app.core.security import Security
from app.core.dependencies import require_role
from app.models.admin_models import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse, LookupResponse,
    UserCreate, UserUpdate, UserResponse, UserListResponse, StatsResponse,
    UserRight, UserRightsResponse
)
from app.services.admin_service import AdminService
from app.models.auth_models import ErrorResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

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
        return AdminService.get_lookups()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post(
    "/employees",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new employee",
    description="Create a new employee and automatically generate a User account"
)
async def create_employee(
    employee: EmployeeCreate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        # Pass admin user ID as creator
        return AdminService.create_employee(employee, created_by_id=1) 
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

@router.get(
    "/employees",
    response_model=EmployeeListResponse,
    summary="List employees",
    description="Get paginated list of employees with search"
)
async def list_employees(
    current_user: Annotated[dict, Depends(require_role("ADMIN", "EMPLOYEE"))],
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str = Query(None)
):
    try:
        return AdminService.get_all_employees(page, size, search)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/employees/{emp_id}",
    response_model=EmployeeResponse,
    summary="Get employee details"
)
async def get_employee(
    emp_id: int,
    current_user: Annotated[dict, Depends(require_role("ADMIN", "EMPLOYEE"))]
):
    emp = AdminService.get_employee_by_id(emp_id)
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    return emp

@router.put(
    "/employees/{emp_id}",
    response_model=EmployeeResponse,
    summary="Update employee details"
)
async def update_employee(
    emp_id: int,
    employee: EmployeeUpdate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        updated_emp = AdminService.update_employee(emp_id, employee, modified_by_id=1) # TODO: get user id from token
        if not updated_emp:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        return updated_emp
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
# =====================
# USER ENDPOINTS
# =====================

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
        return AdminService.get_all_users(page, size, search)
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
        # Pass admin user ID as creator (extract from token/current_user if avail)
        return AdminService.create_user(data, created_by_str='ADMIN')
    except ValueError as e:
        # Email duplicate
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
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
    user_id: int,
    data: UserUpdate,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        updated_user = AdminService.update_user(user_id, data)
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
        return AdminService.get_dashboard_stats()
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
    user_id: int,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        return AdminService.get_user_rights(user_id)
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
    user_id: int,
    rights: List[UserRight],
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        AdminService.save_user_rights(user_id, rights)
        return {"message": "Rights saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
