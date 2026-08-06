"""In-memory sliding-window rate limiting per client IP."""

import time
from collections import defaultdict, deque


class RateLimiter:
    """Sliding-window limiter tracking request timestamps per key."""

    def __init__(self, window_seconds: int, max_requests: int) -> None:
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds) for the given key."""
        now = time.monotonic()
        window_start = now - self.window_seconds
        hits = self._hits[key]

        while hits and hits[0] <= window_start:
            hits.popleft()

        if len(hits) >= self.max_requests:
            retry_after = max(1, int(self.window_seconds - (now - hits[0])) + 1)
            return False, retry_after

        hits.append(now)
        return True, 0

    def clear(self, key: str) -> None:
        """Remove tracked timestamps for a key."""
        self._hits.pop(key, None)
