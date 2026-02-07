"""
Security Module
JWT token creation and verification, password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import bcrypt
from jose import jwt, JWTError
from app.core.config import get_settings


class Security:
    """Security utilities for JWT and password handling"""
    
    @staticmethod
    def _pre_hash(password: str) -> str:
        """
        Pre-hash password using SHA-256 to remove bcrypt 72-byte limit.
        
        bcrypt has a hard limit of 72 bytes. By pre-hashing with SHA-256,
        we convert any length password to a fixed 64-character hex string,
        which bcrypt can then safely hash.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA-256 pre-hash + bcrypt.
        Supports passwords of any length.
        """
        prehashed = Security._pre_hash(password)
        # Use bcrypt directly to avoid passlib length check issues
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(prehashed.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            prehashed = Security._pre_hash(plain_password)
            return bcrypt.checkpw(
                prehashed.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time
        
        Returns:
            Encoded JWT token string
        """
        settings = get_settings()
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_verification_token(user_id: str, tenant_id: str) -> str:
        """Create an email verification token"""
        settings = get_settings()
        expire = datetime.utcnow() + timedelta(
            hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS
        )
        data = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "purpose": "email_verification",
            "exp": expire
        }
        return jwt.encode(
            data,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def create_password_reset_token(user_id: str, tenant_id: str) -> str:
        """Create a password reset token"""
        settings = get_settings()
        expire = datetime.utcnow() + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        data = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "purpose": "password_reset",
            "exp": expire
        }
        return jwt.encode(
            data,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
    
    @staticmethod
    def verify_token(token: str, expected_purpose: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: The JWT token to verify
            expected_purpose: Optional purpose to validate (email_verification, password_reset)
        
        Returns:
            Decoded token payload if valid, None otherwise
        """
        settings = get_settings()
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check purpose if specified
            if expected_purpose and payload.get("purpose") != expected_purpose:
                return None
            
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def get_token_expiration_seconds() -> int:
        """Get access token expiration time in seconds"""
        settings = get_settings()
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
