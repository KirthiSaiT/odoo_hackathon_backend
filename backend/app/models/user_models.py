"""
User Configuration Models
Pydantic schemas for user management
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


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
    role_name: Optional[str] = None
    created_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    """List response for users"""
    items: List[UserResponse]
    total: int
    page: int
    size: int
