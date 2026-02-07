"""
User Profile Models
Pydantic schemas for user profile management
"""
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    """Base profile fields"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country_id: Optional[int] = None
    profile_picture_url: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[date] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a profile"""
    pass


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile - all fields optional"""
    pass


class ProfileResponse(ProfileBase):
    """Schema for profile response with additional fields"""
    id: int
    user_id: str
    employee_id: Optional[int] = None
    country_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # User info (joined from Users table)
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None

    class Config:
        from_attributes = True
