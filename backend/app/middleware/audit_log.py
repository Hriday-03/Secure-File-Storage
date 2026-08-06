"""Request audit logging middleware."""

import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.jwt_handler import decode_access_token

_SENSITIVE_PATHS = ("/api/auth/login", "/api/auth/register")


def _extract_user_id(request) -> str | None:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    try:
        return decode_access_token(auth.split(" ", 1)[1].strip())
    except Exception:
        return None


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log a structured line per request with timing and user context."""

    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        user_id = _extract_user_id(request)
        context = {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 1),
            "user_id": user_id,
            "client": request.client.host if request.client else None,
        }

        if request.url.path in _SENSITIVE_PATHS:
            logger.info("AUTH_REQUEST {}", context)
        elif response.status_code >= 500:
            logger.error("SERVER_ERROR {}", context)
        elif response.status_code >= 400:
            logger.warning("CLIENT_ERROR {}", context)
        else:
            logger.debug("REQUEST {}", context)

        return response
