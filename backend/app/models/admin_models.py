"""
Admin/Employee Management Models
Pydantic schemas for employee management and lookups
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field

# =====================
# SHARED MODELS
# =====================

class LookupItem(BaseModel):
    """Generic lookup item (Id, Name)"""
    id: int
    name: str

class LookupResponse(BaseModel):
    """Response containing all lookup lists"""
    genders: List[LookupItem]
    marital_statuses: List[LookupItem]
    blood_groups: List[LookupItem]
    departments: List[LookupItem]
    designations: List[LookupItem]
    employment_types: List[LookupItem]
    employment_statuses: List[LookupItem]
    countries: List[LookupItem]
    roles: List[LookupItem]

# =====================
# EMPLOYEE MODELS
# =====================

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
    employee_code: Optional[str] = None  # Future field
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

# =====================
# USER MODELS
# =====================

class UserBase(BaseModel):
    """Base user fields"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    role_id: int
    is_active: bool = True

class UserCreate(UserBase):
    """Schema for creating a user"""
    password: Optional[str] = None  # If None, auto-generate

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """Schema for user response"""
    user_id: str
    role: str  # String representation (ADMIN, EMPLOYEE, PORTAL)
    role_name: Optional[str] = None # From Roles table
    created_at: Optional[datetime] = None

class UserListResponse(BaseModel):
    """List response for users"""
    items: List[UserResponse]
    total: int
    page: int
    size: int

class StatsResponse(BaseModel):
    """Dashboard statistics"""
    total_users: int
    active_employees: int
    total_roles: int
    total_modules: int

class UserRight(BaseModel):
    """User access right for a module"""
    id: Optional[int] = None
    user_id: int
    module_key: str
    can_view: bool = False
    can_create: bool = False
    can_update: bool = False
    can_delete: bool = False

class UserRightsResponse(BaseModel):
    """List of rights for a user"""
    user_id: str # user_id is string in other responses but int in DB? keeping int here to match table
    rights: List[UserRight]
