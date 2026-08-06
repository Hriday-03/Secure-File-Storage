"""Rate limiting middleware for sensitive endpoints."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.middleware.rate_limit import RateLimiter
from app.utils.exceptions import RateLimitExceededError

_AUTH_LIMITER = RateLimiter(window_seconds=60, max_requests=10)
_GENERAL_LIMITER = RateLimiter(window_seconds=60, max_requests=120)

_AUTH_PATHS = ("/api/auth/login", "/api/auth/register", "/api/users/change-password")


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforce per-IP sliding-window limits on API requests."""

    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        path = request.url.path
        if not path.startswith("/api"):
            return await call_next(request)

        key = _client_key(request)
        if path in _AUTH_PATHS:
            limiter = _AUTH_LIMITER
        else:
            limiter = _GENERAL_LIMITER

        allowed, retry_after = limiter.check(key)
        if not allowed:
            return JSONResponse(
                status_code=RateLimitExceededError.status_code,
                content={
                    "success": False,
                    "message": RateLimitExceededError.message,
                    "data": None,
                    "error": RateLimitExceededError.code,
                },
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)
