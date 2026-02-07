"""
Role & Rights Models
Pydantic schemas for role and access rights management
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    """Base role fields"""
    role_name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    """Schema for creating a role"""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    role_name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    """Schema for role response"""
    role_id: int
    created_at: Optional[datetime] = None


class RoleListResponse(BaseModel):
    """List response for roles"""
    items: List[RoleResponse]
    total: int
    page: int
    size: int


class UserRight(BaseModel):
    """User access right for a module"""
    id: Optional[int] = None
    user_id: str
    module_key: str
    can_view: bool = False
    can_create: bool = False
    can_update: bool = False
    can_delete: bool = False


class UserRightsResponse(BaseModel):
    """List of rights for a user"""
    user_id: str
    rights: List[UserRight]
