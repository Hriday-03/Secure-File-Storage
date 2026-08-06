"""Security headers applied to every response."""

from starlette.middleware.base import BaseHTTPMiddleware

_DEFAULT_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "X-XSS-Protection": "0",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
}

_HSTS_HEADER = "Strict-Transport-Security"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach hardened response headers to all requests."""

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        for name, value in _DEFAULT_HEADERS.items():
            response.headers.setdefault(name, value)
        if request.url.scheme == "https":
            response.headers.setdefault(_HSTS_HEADER, "max-age=31536000; includeSubDomains")
        return response
