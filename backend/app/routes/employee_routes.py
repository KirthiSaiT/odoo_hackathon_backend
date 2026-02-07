"""
Employee Routes
API endpoints for employee management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from app.core.dependencies import require_role
from app.models.employee_models import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/admin", tags=["Employees"])


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
        return EmployeeService.create_employee(employee, created_by_id=1)
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
        return EmployeeService.get_all_employees(page, size, search)
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
    emp = EmployeeService.get_employee_by_id(emp_id)
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
        updated_emp = EmployeeService.update_employee(emp_id, employee, modified_by_id=1)
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


@router.delete(
    "/employees/{emp_id}",
    summary="Delete employee (soft delete)"
)
async def delete_employee(
    emp_id: int,
    current_user: Annotated[dict, Depends(require_role("ADMIN"))]
):
    try:
        EmployeeService.delete_employee(emp_id)
        return {"message": "Employee deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
