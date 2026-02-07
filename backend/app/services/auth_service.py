"""
Authentication Service
Handles business logic for authentication operations
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.core.database import get_db_cursor
from app.core.security import Security
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management"""
    
    # =====================
    # TENANT OPERATIONS
    # =====================
    
    @staticmethod
    def create_tenant(tenant_name: str, created_by: str = "SYSTEM") -> Optional[str]:
        """
        Create a new tenant
        
        Returns:
            tenant_id if successful, None otherwise
        """
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Tenants (tenant_name, created_by)
                    OUTPUT INSERTED.tenant_id
                    VALUES (?, ?)
                    """,
                    (tenant_name, created_by)
                )
                result = cursor.fetchone()
                if result:
                    tenant_id = str(result[0])
                    logger.info(f"✅ Tenant created: {tenant_id}")
                    return tenant_id
                return None
        except Exception as e:
            logger.error(f"❌ Error creating tenant: {str(e)}")
            raise e
    
    # =====================
    # USER OPERATIONS
    # =====================
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        user_id,
                        tenant_id,
                        name,
                        email,
                        password_hash,
                        role,
                        is_email_verified,
                        is_active
                    FROM Users
                    WHERE email = ?
                    """,
                    (email,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                
                return {
                    "user_id": str(row[0]),
                    "tenant_id": str(row[1]),
                    "name": row[2],
                    "email": row[3],
                    "password_hash": row[4],
                    "role": row[5],
                    "is_email_verified": bool(row[6]),
                    "is_active": bool(row[7])
                }
        except Exception as e:
            logger.error(f"❌ Error getting user by email: {str(e)}")
            return None
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        user_id,
                        tenant_id,
                        name,
                        email,
                        password_hash,
                        role,
                        is_email_verified,
                        is_active
                    FROM Users
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                
                return {
                    "user_id": str(row[0]),
                    "tenant_id": str(row[1]),
                    "name": row[2],
                    "email": row[3],
                    "password_hash": row[4],
                    "role": row[5],
                    "is_email_verified": bool(row[6]),
                    "is_active": bool(row[7])
                }
        except Exception as e:
            logger.error(f"❌ Error getting user by ID: {str(e)}")
            return None
    
    @staticmethod
    def create_user(
        tenant_id: str,
        name: str,
        email: str,
        password: str,
        role: str = "PORTAL",
        created_by: str = "SYSTEM"
    ) -> Optional[str]:
        """
        Create a new user
        
        Returns:
            user_id if successful, None otherwise
        """
        try:
            password_hash = Security.hash_password(password)
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Users (tenant_id, name, email, password_hash, role, created_by)
                    OUTPUT INSERTED.user_id
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (tenant_id, name, email, password_hash, role, created_by)
                )
                result = cursor.fetchone()
                if result:
                    user_id = str(result[0])
                    logger.info(f"✅ User created: {user_id}")
                    return user_id
                return None
        except Exception as e:
            logger.error(f"❌ Error creating user: {str(e)}")
            raise e
    
    @staticmethod
    def verify_user_email(user_id: str) -> bool:
        """Mark user email as verified"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE Users
                    SET is_email_verified = 1, updated_at = SYSDATETIME()
                    WHERE user_id = ?
                    """,
                    (user_id,)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error verifying user email: {str(e)}")
            return False
    
    @staticmethod
    def update_user_password(user_id: str, new_password: str) -> bool:
        """Update user password"""
        try:
            password_hash = Security.hash_password(new_password)
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE Users
                    SET password_hash = ?, updated_at = SYSDATETIME()
                    WHERE user_id = ?
                    """,
                    (password_hash, user_id)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error updating user password: {str(e)}")
            return False
    
    # =====================
    # TOKEN OPERATIONS
    # =====================
    
    @staticmethod
    def store_verification_token(
        tenant_id: str,
        user_id: str,
        token: str,
        expires_at: datetime
    ) -> bool:
        """Store email verification token"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO EmailVerificationTokens 
                    (tenant_id, user_id, token, expires_at, created_by)
                    VALUES (?, ?, ?, ?, 'SYSTEM')
                    """,
                    (tenant_id, user_id, token, expires_at)
                )
                return True
        except Exception as e:
            logger.error(f"❌ Error storing verification token: {str(e)}")
            return False
    
    @staticmethod
    def get_verification_token(token: str) -> Optional[Dict[str, Any]]:
        """Get verification token details"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        verification_id,
                        tenant_id,
                        user_id,
                        token,
                        expires_at,
                        is_used
                    FROM EmailVerificationTokens
                    WHERE token = ? AND is_used = 0 AND expires_at > SYSDATETIME()
                    """,
                    (token,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                
                return {
                    "verification_id": str(row[0]),
                    "tenant_id": str(row[1]),
                    "user_id": str(row[2]),
                    "token": row[3],
                    "expires_at": row[4],
                    "is_used": bool(row[5])
                }
        except Exception as e:
            logger.error(f"❌ Error getting verification token: {str(e)}")
            return None
    
    @staticmethod
    def mark_verification_token_used(token: str) -> bool:
        """Mark verification token as used"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE EmailVerificationTokens
                    SET is_used = 1
                    WHERE token = ?
                    """,
                    (token,)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error marking verification token as used: {str(e)}")
            return False
    
    @staticmethod
    def store_password_reset_token(
        tenant_id: str,
        user_id: str,
        token: str,
        expires_at: datetime
    ) -> bool:
        """Store password reset token"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO PasswordResetTokens 
                    (tenant_id, user_id, token, expires_at, created_by)
                    VALUES (?, ?, ?, ?, 'SYSTEM')
                    """,
                    (tenant_id, user_id, token, expires_at)
                )
                return True
        except Exception as e:
            logger.error(f"❌ Error storing password reset token: {str(e)}")
            return False
    
    @staticmethod
    def get_password_reset_token(token: str) -> Optional[Dict[str, Any]]:
        """Get password reset token details"""
        try:
            logger.info(f"🔍 Looking up reset token (first 50 chars): {token[:50]}...")
            with get_db_cursor() as cursor:
                # First check if token exists at all
                cursor.execute(
                    """
                    SELECT 
                        reset_id,
                        tenant_id,
                        user_id,
                        token,
                        expires_at,
                        is_used
                    FROM PasswordResetTokens
                    WHERE token = ?
                    """,
                    (token,)
                )
                row = cursor.fetchone()
                if not row:
                    logger.warning(f"⚠️ Token not found in database at all")
                    return None
                
                logger.info(f"📦 Token found - is_used: {row[5]}, expires_at: {row[4]}")
                
                # Check if already used
                if bool(row[5]):
                    logger.warning(f"⚠️ Token already used")
                    return None
                
                # Check if expired (compare with current time)
                from datetime import datetime
                if row[4] < datetime.utcnow():
                    logger.warning(f"⚠️ Token expired at {row[4]}")
                    return None
                
                return {
                    "reset_id": str(row[0]),
                    "tenant_id": str(row[1]),
                    "user_id": str(row[2]),
                    "token": row[3],
                    "expires_at": row[4],
                    "is_used": bool(row[5])
                }
        except Exception as e:
            logger.error(f"❌ Error getting password reset token: {str(e)}")
            return None
    
    @staticmethod
    def mark_password_reset_token_used(token: str) -> bool:
        """Mark password reset token as used"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE PasswordResetTokens
                    SET is_used = 1
                    WHERE token = ?
                    """,
                    (token,)
                )
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"❌ Error marking password reset token as used: {str(e)}")
            return False
    
    # =====================
    # AUTHENTICATION FLOW
    # =====================
    
    @staticmethod
    def signup(name: str, email: str, password: str, tenant_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Register a new PORTAL user with a new tenant
        
        Returns:
            Dict with success status and message
        """
        # Check if email already exists
        existing_user = AuthService.get_user_by_email(email)
        if existing_user:
            return {"success": False, "message": "Email already registered"}
        
        # Auto-generate tenant name from email if not provided
        if not tenant_name:
            tenant_name = f"Tenant_{email.split('@')[0]}"
        
        try:
            # Create tenant
            tenant_id = AuthService.create_tenant(tenant_name, email)
            if not tenant_id:
                return {"success": False, "message": "Failed to create tenant"}
            
            # Create user (PORTAL role only for signup)
            user_id = AuthService.create_user(
                tenant_id=tenant_id,
                name=name,
                email=email,
                password=password,
                role="PORTAL",
                created_by=email
            )
            if not user_id:
                return {"success": False, "message": "Failed to create user"}
            
            # Generate verification token
            token = Security.create_verification_token(user_id, tenant_id)
            
            # Store token in database
            from datetime import datetime, timedelta
            from app.core.config import get_settings
            settings = get_settings()
            expires_at = datetime.utcnow() + timedelta(
                hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
            )
            AuthService.store_verification_token(tenant_id, user_id, token, expires_at)
            
            # Send verification email
            EmailService.send_verification_email(email, name, token)
            
            return {
                "success": True,
                "message": "Account created successfully. Please check your email to verify your account.",
                "user_id": user_id,
                "tenant_id": tenant_id
            }
            
        except Exception as e:
            logger.error(f"❌ Signup error: {str(e)}")
            return {"success": False, "message": f"Signup failed: {str(e)}"}
    
    @staticmethod
    def login(email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate JWT token
        
        Returns:
            Dict with access_token if successful
        """
        user = AuthService.get_user_by_email(email)
        
        if not user:
            return {"success": False, "message": "Invalid email or password"}
        
        if not user["is_active"]:
            return {"success": False, "message": "Account is deactivated"}
        
        if not user["is_email_verified"]:
            return {"success": False, "message": "Please verify your email before logging in"}
        
        if not Security.verify_password(password, user["password_hash"]):
            return {"success": False, "message": "Invalid email or password"}
        
        # Create JWT token
        token_payload = {
            "sub": user["email"],
            "user_id": user["user_id"],
            "tenant_id": user["tenant_id"],
            "role": user["role"]
        }
        access_token = Security.create_access_token(token_payload)
        
        return {
            "success": True,
            "access_token": access_token,
            "expires_in": Security.get_token_expiration_seconds(),
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "tenant_id": user["tenant_id"],
                "is_email_verified": user["is_email_verified"]
            }
        }
    
    @staticmethod
    def verify_email(token: str) -> Dict[str, Any]:
        """
        Verify user email using token
        
        Returns:
            Dict with success status
        """
        # Verify JWT token
        payload = Security.verify_token(token, expected_purpose="email_verification")
        if not payload:
            return {"success": False, "message": "Invalid or expired verification token"}
        
        user_id = payload.get("sub")
        
        # Check if token exists in database and is valid
        db_token = AuthService.get_verification_token(token)
        if not db_token:
            return {"success": False, "message": "Verification token not found or already used"}
        
        # Mark email as verified
        if not AuthService.verify_user_email(user_id):
            return {"success": False, "message": "Failed to verify email"}
        
        # Mark token as used
        AuthService.mark_verification_token_used(token)
        
        return {"success": True, "message": "Email verified successfully"}
    
    @staticmethod
    def forgot_password(email: str) -> Dict[str, Any]:
        """
        Initiate password reset process
        
        Returns:
            Dict with success status (always returns success for security)
        """
        user = AuthService.get_user_by_email(email)
        
        # Always return success for security (don't reveal if email exists)
        if not user:
            return {"success": True, "message": "If the email exists, a reset link has been sent"}
        
        try:
            # Generate reset token
            token = Security.create_password_reset_token(user["user_id"], user["tenant_id"])
            
            # Store token in database
            from datetime import datetime, timedelta
            from app.core.config import get_settings
            settings = get_settings()
            expires_at = datetime.utcnow() + timedelta(
                hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
            )
            AuthService.store_password_reset_token(
                user["tenant_id"],
                user["user_id"],
                token,
                expires_at
            )
            
            # Send reset email
            EmailService.send_password_reset_email(email, user["name"], token)
            
            return {"success": True, "message": "If the email exists, a reset link has been sent"}
            
        except Exception as e:
            logger.error(f"❌ Forgot password error: {str(e)}")
            return {"success": True, "message": "If the email exists, a reset link has been sent"}
    
    @staticmethod
    def reset_password(token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password using token
        
        Returns:
            Dict with success status
        """
        # Verify JWT token
        payload = Security.verify_token(token, expected_purpose="password_reset")
        if not payload:
            return {"success": False, "message": "Invalid or expired reset token"}
        
        user_id = payload.get("sub")
        
        # Check if token exists in database and is valid
        db_token = AuthService.get_password_reset_token(token)
        if not db_token:
            return {"success": False, "message": "Reset token not found or already used"}
        
        # Update password
        if not AuthService.update_user_password(user_id, new_password):
            return {"success": False, "message": "Failed to update password"}
        
        # Mark token as used
        AuthService.mark_password_reset_token_used(token)
        
        return {"success": True, "message": "Password reset successfully"}
