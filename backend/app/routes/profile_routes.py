"""
Profile Routes
API endpoints for user profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from ..core.dependencies import get_current_user_token
from ..models.profile_models import ProfileUpdate, ProfileResponse
from ..services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user_token)):
    """
    Get the current user's profile.
    Creates an empty profile if one doesn't exist.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    
    try:
        profile = ProfileService.get_or_create_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    data: ProfileUpdate,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Update the current user's profile.
    """
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token"
        )
    
    try:
        # Ensure profile exists
        ProfileService.get_or_create_profile(user_id)
        
        # Update profile
        profile = ProfileService.update_profile(user_id, data)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get a specific user's profile (Admin only).
    """
    # Check if current user is admin
    current_role = current_user.get("role")
    current_role_id = current_user.get("role_id")
    
    is_admin = current_role == "ADMIN" or current_role_id == 1
    is_own_profile = current_user.get("user_id") == user_id
    
    if not is_admin and not is_own_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    try:
        profile = ProfileService.get_profile_by_user_id(user_id)
        if not profile:
            # Create empty profile for the user
            profile = ProfileService.get_or_create_profile(user_id)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )


@router.put("/{user_id}", response_model=ProfileResponse)
async def update_user_profile(
    user_id: str,
    data: ProfileUpdate,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Update a specific user's profile (Admin only, or own profile).
    """
    # Check permissions
    current_role = current_user.get("role")
    current_role_id = current_user.get("role_id")
    
    is_admin = current_role == "ADMIN" or current_role_id == 1
    is_own_profile = current_user.get("user_id") == user_id
    
    if not is_admin and not is_own_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    try:
        # Ensure profile exists
        ProfileService.get_or_create_profile(user_id)
        
        # Update profile
        profile = ProfileService.update_profile(user_id, data)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
