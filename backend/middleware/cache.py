"""
backend/middleware/cache.py
---------------------------
In-memory TTL cache — local equivalent of Catalyst Cache (Segmented).

When deployed to Catalyst AppSail, replace the `_cache` dict with:
    from catalystcache import CatalystCache
    cache = CatalystCache(segment="crimegpt-cache")
    cache.put(key, value, ttl_seconds=ttl)
    val = cache.get(key)

Usage:
    from backend.middleware.cache import get_cached, set_cached, invalidate

    data = get_cached("districts")
    if data is None:
        data = compute_data()
        set_cached("districts", data, ttl=3600)
"""

import time
import json
import threading
from typing import Any, Optional

_cache: dict[str, dict] = {}
_lock = threading.Lock()

# TTL defaults (seconds) — mirrors the Catalyst Cache TTL plan
TTL = {
    "districts":   3600,   # 1 hour
    "clusters":    1800,   # 30 min
    "anomalies":   300,    # 5 min (live-ish data)
    "stats":       600,    # 10 min
    "forecasts":   7200,   # 2 hours (SARIMA rarely changes)
    "gang_network":7200,   # 2 hours
    "default":     600,
}


def get_cached(key: str) -> Optional[Any]:
    """Return cached value if not expired, else None."""
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires_at"]:
            del _cache[key]
            return None
        return entry["data"]


def set_cached(key: str, data: Any, ttl: Optional[int] = None) -> None:
    """Store data in cache with TTL (seconds)."""
    resolved_ttl = ttl or TTL.get(key, TTL["default"])
    with _lock:
        _cache[key] = {
            "data": data,
            "cached_at": time.time(),
            "expires_at": time.time() + resolved_ttl,
        }


def invalidate(key: str) -> None:
    """Remove a specific key from cache."""
    with _lock:
        _cache.pop(key, None)


def invalidate_all() -> None:
    """Flush entire cache — call after a new data batch arrives."""
    with _lock:
        _cache.clear()


def cache_stats() -> dict:
    """Return cache diagnostics (for /api/admin/stats)."""
    with _lock:
        now = time.time()
        active = {k: v for k, v in _cache.items() if now <= v["expires_at"]}
        return {
            "total_keys": len(active),
            "keys": [
                {
                    "key": k,
                    "ttl_remaining_s": round(v["expires_at"] - now),
                }
                for k, v in active.items()
            ],
        }
