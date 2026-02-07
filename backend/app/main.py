"""
FastAPI Application Entry Point
SaaS Authentication Module
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import os

from app.routes.auth_routes import router as auth_router
from app.routes.employee_routes import router as employee_router
from app.routes.user_routes import router as user_router
from app.routes.role_routes import router as role_router
from app.routes.profile_routes import router as profile_router
from app.routes.product_routes import router as product_router
from app.routes.cart_routes import router as cart_router
from app.routes.cart_routes import router as cart_router
from app.routes.subscription_routes import router as subscription_router
from app.routes.payment_routes import router as payment_router
from app.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SaaS Authentication API",
    description="Multi-tenant authentication module with JWT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# =====================
# CORS Configuration
# =====================
def get_allowed_origins():
    """Get allowed origins based on environment"""
    settings = get_settings()
    environment = settings.ENVIRONMENT.lower()
    
    # Base origins for development
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    # Add frontend URL from settings
    if settings.FRONTEND_URL:
        origins.append(settings.FRONTEND_URL)
    
    logger.info(f"🌍 Environment: {environment}")
    logger.info(f"🔗 Allowed CORS origins: {origins}")
    
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# Exception Handlers
# =====================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation Error",
            "errors": errors,
            "success": False
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "success": False
        }
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "success": False
        }
    )


# =====================
# Routes
# =====================
from app.routes.order_routes import router as order_router

# ... inside routes section ...
app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(profile_router)
app.include_router(product_router, prefix="/api/products", tags=["Products"])
app.include_router(cart_router, prefix="/api/cart", tags=["Cart"])
app.include_router(subscription_router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(payment_router, prefix="/api", tags=["Payments"])
app.include_router(order_router, prefix="/api", tags=["Orders"])



# =====================
# Health Check
# =====================
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SaaS Authentication API",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB health check
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
