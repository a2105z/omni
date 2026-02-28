"""
Simple in-memory rate limiting for API routes.
Step 20: Basic security.
"""
import time
from collections import defaultdict
from typing import Callable

# In-memory store: ip -> [(timestamp, count)]
_store: dict[str, list[tuple[float, int]]] = defaultdict(list)
_CLEANUP_INTERVAL = 60.0
_LAST_CLEANUP = 0.0


def _cleanup() -> None:
    global _LAST_CLEANUP
    now = time.monotonic()
    if now - _LAST_CLEANUP < _CLEANUP_INTERVAL:
        return
    _LAST_CLEANUP = now
    cutoff = now - 60  # 1 minute window
    for key in list(_store.keys()):
        _store[key] = [(t, c) for t, c in _store[key] if t > cutoff]
        if not _store[key]:
            del _store[key]


def check_rate_limit(
    key: str, max_requests: int = 30, window_seconds: int = 60
) -> bool:
    """
    Returns True if under limit, False if rate limited.
    """
    _cleanup()
    now = time.monotonic()
    cutoff = now - window_seconds
    entries = _store[key]
    entries[:] = [(t, c) for t, c in entries if t > cutoff]
    total = sum(c for _, c in entries)
    if total >= max_requests:
        return False
    entries.append((now, 1))
    return True
