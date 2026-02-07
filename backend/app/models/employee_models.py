"""
Employee/HR Models
Pydantic schemas for employee management
"""
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field


class EmployeeBase(BaseModel):
    """Shared employee fields"""
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = None
    marital_status_id: Optional[int] = None
    blood_group_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    designation_id: Optional[int] = None
    department_id: Optional[int] = None
    employment_type: Optional[int] = None
    employment_status: Optional[int] = 1  # Default Active
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_id: Optional[int] = 1
    additional_notes: Optional[str] = None
    role_id: Optional[int] = 3  # Default User role
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    pass


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender_id: Optional[int] = None
    marital_status_id: Optional[int] = None
    blood_group_id: Optional[int] = None
    date_of_joining: Optional[date] = None
    designation_id: Optional[int] = None
    department_id: Optional[int] = None
    employment_type: Optional[int] = None
    employment_status: Optional[int] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_id: Optional[int] = None
    additional_notes: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response with joined data"""
    id: int
    employee_code: Optional[str] = None
    user_id: Optional[str] = None
    
    # Joined Names (for display)
    gender_name: Optional[str] = None
    marital_status_name: Optional[str] = None
    blood_group_name: Optional[str] = None
    designation_name: Optional[str] = None
    department_name: Optional[str] = None
    employment_type_name: Optional[str] = None
    employment_status_name: Optional[str] = None
    country_name: Optional[str] = None
    role_name: Optional[str] = None
    
    # Metadata
    created_at: datetime
    created_by: Optional[int] = None
    modified_at: Optional[datetime] = None
    modified_by: Optional[int] = None


class EmployeeListResponse(BaseModel):
    """List response with pagination metadata"""
    items: List[EmployeeResponse]
    total: int
    page: int
    size: int
