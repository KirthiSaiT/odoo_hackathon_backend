"""
Shared Dependencies
Common dependencies for API routes
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.core.security import Security

# Security scheme for protected endpoints
security = HTTPBearer(auto_error=False)

def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user payload from token
    Returns the decoded JWT payload as a dict
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token = credentials.credentials
    payload = Security.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload

def require_role(*allowed_roles: str):
    """
    Dependency factor for role-based access control
    Internal usage: Depends(require_role("ADMIN"))
    """
    def role_checker(current_user: dict = Depends(get_current_user_token)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required role: {allowed_roles}"
            )
        return current_user
    return role_checker

def get_current_active_user(
    current_user: dict = Depends(get_current_user_token)
) -> dict:
    """
    Dependency to get current active user.
    For now, it just returns the user from token.
    In future, we can add DB check here.
    """
    # We could check DB here to ensure user is still active
    # For performance, we rely on token validity for now
    return current_user
