"""
backend/routers/geo.py
----------------------
Geospatial endpoints — DBSCAN crime clusters + K-Means district risk rollup.

Step 2.4: Cache-aside pattern wraps both endpoints.
  • /api/districts  — TTL 1 hour  (served from in-memory cache on warm hits)
  • /api/clusters   — TTL 30 min  (backed by ml/outputs/clusters.geojson)

On Catalyst AppSail, swap the in-process cache for CatalystCache(segment="crimegpt-cache").
"""

import json
import time
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pathlib import Path

from backend.middleware.cache import get_cached, set_cached, TTL

router = APIRouter(prefix="/api", tags=["Geospatial & Districts"])

BASE_DIR       = Path(__file__).resolve().parent.parent.parent
DISTRICTS_FILE = BASE_DIR / "ml" / "outputs" / "district_stats.json"
CLUSTERS_FILE  = BASE_DIR / "ml" / "outputs" / "clusters.geojson"

# Fallback script-dir paths (written during ML pipeline)
_DISTRICTS_ALT = BASE_DIR / "ml" / "scripts" / "district_stats.json"
_CLUSTERS_ALT  = BASE_DIR / "ml" / "scripts" / "clusters.geojson"


def _resolve(primary: Path, fallback: Path) -> Path:
    """Return the first path that exists."""
    if primary.exists():
        return primary
    if fallback.exists():
        return fallback
    return primary  # let callers raise the 404


# ── GET /api/districts ──────────────────────────────────────────────────────

@router.get("/districts")
def get_districts():
    """
    K-Means district risk rollup (3 tiers: Low / Medium / High).

    Cache-aside:
      • Warm hit  → returns in < 5 ms (in-memory dict)
      • Cold miss → reads JSON from disk, writes to cache (TTL = 1 h)
    On Catalyst: replace with CatalystCache.get / .put calls.
    """
    # ── Cache check ────────────────────────────────────────────────────────
    cached = get_cached("districts")
    if cached is not None:
        return {
            "status": "success",
            "source": "cache",
            "districts": cached,
        }

    # ── Cache miss → load from disk ────────────────────────────────────────
    t0 = time.perf_counter()
    target_file = _resolve(DISTRICTS_FILE, _DISTRICTS_ALT)
    if not target_file.exists():
        raise HTTPException(
            status_code=404,
            detail="District stats not found. Run ML pipeline first."
        )

    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ── Write-back to cache ────────────────────────────────────────────────
    set_cached("districts", data)
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)

    return {
        "status": "success",
        "source": "disk",
        "latency_ms": latency_ms,
        "cache_ttl_s": TTL["districts"],
        "districts": data,
    }


# ── GET /api/clusters ───────────────────────────────────────────────────────

@router.get("/clusters")
def get_clusters(
    district: Optional[str] = Query(None, description="Filter by district name"),
    time_bucket: Optional[str] = Query(None, alias="time", description="AM / PM / Night / All"),
):
    """
    DBSCAN crime cluster GeoJSON.

    Cache-aside with optional district + time-of-day filter applied post-cache.
    Cache key = 'clusters' (full unfiltered dataset — filtering is cheap in-memory).
    TTL = 30 min.
    """
    # ── Cache check ────────────────────────────────────────────────────────
    cached = get_cached("clusters")
    if cached is None:
        t0 = time.perf_counter()
        target_file = _resolve(CLUSTERS_FILE, _CLUSTERS_ALT)
        if not target_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Clusters GeoJSON not found. Run ML pipeline first."
            )
        with open(target_file, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        cached = geojson_data.get("features", [])
        set_cached("clusters", cached)
        source = "disk"
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    else:
        source = "cache"
        latency_ms = None

    features = cached

    # ── Optional filters (applied in-memory, no disk re-read) ─────────────
    if district:
        features = [
            f for f in features
            if f.get("properties", {}).get("district", "").lower() == district.lower()
        ]

    if time_bucket and time_bucket.lower() != "all":
        features = [
            f for f in features
            if f.get("properties", {}).get("time_bucket", "").lower() == time_bucket.lower()
        ]

    response = {
        "status": "success",
        "source": source,
        "type": "FeatureCollection",
        "feature_count": len(features),
        "features": features,
    }
    if latency_ms is not None:
        response["latency_ms"] = latency_ms

    return response


# ── POST /api/cache/invalidate ──────────────────────────────────────────────
# (Called by the data-ingest pipeline when a new FIR batch lands)

@router.post("/cache/invalidate")
def invalidate_geo_cache():
    """
    Flush district_stats and clusters cache segments.
    Next request to /api/districts or /api/clusters will re-read from disk.
    """
    from backend.middleware.cache import invalidate
    invalidate("districts")
    invalidate("clusters")
    return {"status": "success", "flushed": ["districts", "clusters"]}
