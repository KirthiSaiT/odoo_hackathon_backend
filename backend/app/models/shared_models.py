"""
Shared Models
Common models used across multiple modules
"""
from typing import Optional, List
from pydantic import BaseModel


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


class StatsResponse(BaseModel):
    """Dashboard statistics"""
    total_users: int
    active_employees: int
    total_roles: int
    total_modules: int
