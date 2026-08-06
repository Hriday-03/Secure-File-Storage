"""FastAPI application entry point."""

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.files import router as files_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.audit_log import AuditLogMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.utils.exceptions import AppException

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(files_router, prefix=settings.API_PREFIX)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Serialize custom application exceptions into the API envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "data": None,
            "error": exc.code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Serialize request validation errors into the API envelope."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Invalid input provided.",
            "data": None,
            "error": "VALIDATION_ERROR",
            "details": jsonable_encoder(exc.errors()),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Serialize Starlette/HTTP exceptions into the API envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
            "data": None,
            "error": "HTTP_ERROR",
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler that never leaks internals to the client."""
    from loguru import logger

    logger.exception("Unhandled error on {} {}", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Something went wrong. Please try again.",
            "data": None,
            "error": "INTERNAL_ERROR",
        },
    )


@app.get("/")
def root() -> dict:
    """Return basic API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }