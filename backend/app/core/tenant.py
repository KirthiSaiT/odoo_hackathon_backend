"""
Tenant Configuration Module
Provides default tenant ID for multi-tenant operations
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Default tenant ID from environment
DEFAULT_TENANT_ID: str = os.getenv("DEFAULT_TENANT_ID", "1F1CA876-2C19-41C3-87AA-00890071A591")

def get_tenant_id() -> str:
    """
    Get the current tenant ID.
    In a full multi-tenant implementation, this would be extracted from
    the authenticated user's context. For now, uses a default.
    """
    return DEFAULT_TENANT_ID

def get_tenant_id_for_user(user: Optional[dict] = None) -> str:
    """
    Get tenant ID from user context or return default.
    Future: Extract from JWT token or user session.
    """
    if user and user.get("tenant_id"):
        return user["tenant_id"]
    return DEFAULT_TENANT_ID
