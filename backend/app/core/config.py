"""
Application Configuration
Loads settings from environment variables
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DB_SERVER: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # Stripe
    STRIPE_SECRET_KEY: str
    
    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "SaaS Auth Module"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Tenant
    DEFAULT_TENANT_ID: str = "1F1CA876-2C19-41C3-87AA-00890071A591"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    print(f"DEBUG: Loaded STRIPE_SECRET_KEY: {'Found' if settings.STRIPE_SECRET_KEY else 'Missing'}")
    if settings.STRIPE_SECRET_KEY:
        print(f"DEBUG: Key starts with: {settings.STRIPE_SECRET_KEY[:4]}")
    return settings
