"""
Authentication Routes
API endpoints for authentication operations
"""
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.models.auth_models import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    TokenResponse,
    MessageResponse,
    UserResponse
)
from app.services.auth_service import AuthService
from app.core.security import Security

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for protected endpoints
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Dependency to get current authenticated user"""
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


# =====================
# PUBLIC ENDPOINTS
# =====================

@router.post("/signup", response_model=MessageResponse)
async def signup(request: SignupRequest):
    """
    Register a new PORTAL user
    
    - Creates a new tenant with the provided tenant_name
    - Creates a new user with PORTAL role
    - Sends verification email
    """
    logger.info(f"📝 Signup attempt for email: {request.email}")
    
    result = AuthService.signup(
        name=request.name,
        email=request.email,
        password=request.password,
        tenant_name=request.tenant_name
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return MessageResponse(message=result["message"], success=True)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT access token
    
    - Validates email and password
    - Checks if email is verified
    - Returns access token with user info
    """
    logger.info(f"🔐 Login attempt for email: {request.email}")
    
    result = AuthService.login(
        email=request.email,
        password=request.password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )
    
    return TokenResponse(
        access_token=result["access_token"],
        expires_in=result["expires_in"],
        user=UserResponse(**result["user"])
    )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(request: VerifyEmailRequest):
    """
    Verify user email address using token from email link
    
    - Validates token
    - Marks email as verified
    - Invalidates token after use
    """
    logger.info("📧 Email verification attempt")
    
    result = AuthService.verify_email(request.token)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return MessageResponse(message=result["message"], success=True)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Initiate password reset process
    
    - Sends password reset email if email exists
    - Always returns success for security (doesn't reveal if email exists)
    """
    logger.info(f"🔑 Forgot password request for: {request.email}")
    
    result = AuthService.forgot_password(request.email)
    
    return MessageResponse(message=result["message"], success=True)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using token from email link
    
    - Validates reset token
    - Updates password with new value
    - Invalidates token after use
    """
    logger.info("🔒 Password reset attempt")
    
    result = AuthService.reset_password(
        token=request.token,
        new_password=request.new_password
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return MessageResponse(message=result["message"], success=True)


# =====================
# PROTECTED ENDPOINTS
# =====================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info
    
    Requires valid JWT access token in Authorization header
    """
    user = AuthService.get_user_by_id(current_user.get("user_id"))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=user["user_id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        tenant_id=user["tenant_id"],
        is_email_verified=user["is_email_verified"]
    )
