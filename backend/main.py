import os
import sys
import json
import time
import uvicorn
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure root is in path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.routers import geo, similarity, graph, forecast, risk, stats, admin, forensics
from backend.middleware.cache import set_cached, cache_stats

# ── Output asset paths ──────────────────────────────────────────────────────
ML_OUTPUTS = BASE_DIR / "ml" / "outputs"
ML_SCRIPTS = BASE_DIR / "ml" / "scripts"

ASSET_MAP = {
    "districts":   [ML_OUTPUTS / "district_stats.json",   ML_SCRIPTS / "district_stats.json"],
    "clusters":    [ML_OUTPUTS / "clusters.geojson",       ML_SCRIPTS / "clusters.geojson"],
    "forecasts":   [ML_OUTPUTS / "forecasts.json",         ML_SCRIPTS / "forecasts.json"],
    "gang_network":[ML_OUTPUTS / "gang_network.json",      ML_SCRIPTS / "gang_network.json"],
}


def _resolve_asset(paths: list) -> Path | None:
    for p in paths:
        if p.exists():
            return p
    return None


def _warm_cache():
    """
    Step 2.4 — Startup Stratus asset loader.
    Pre-loads heavy ML output files into the in-memory TTL cache on app boot
    so the first real user request is always a cache hit.

    On Catalyst AppSail:
      • Replace open() calls with CatalystStratus.download(url) → parse
      • Replace set_cached() with CatalystCache.put(key, value, ttl)
    """
    print("[Falcon] Warming cache from ML output assets...")
    t_start = time.perf_counter()
    loaded = []

    for key, paths in ASSET_MAP.items():
        asset = _resolve_asset(paths)
        if asset is None:
            print(f"  [WARN] {key}: no file found — skipping warm-up")
            continue
        try:
            with open(asset, "r", encoding="utf-8") as f:
                data = json.load(f)
            # For clusters GeoJSON, store just the features array
            if key == "clusters":
                data = data.get("features", data)
            set_cached(key, data)
            loaded.append(key)
            print(f"  [OK]   {key}: loaded from {asset.name}")
        except Exception as exc:
            print(f"  [ERR]  {key}: {exc}")

    elapsed = round((time.perf_counter() - t_start) * 1000)
    stats = cache_stats()
    print(f"[Falcon] Cache warm-up done in {elapsed}ms — {stats['total_keys']} keys cached")
    return loaded


# ── Lifespan context manager ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks then yield; run shutdown tasks after."""
    # STARTUP — pre-warm cache
    _warm_cache()
    yield
    # SHUTDOWN (nothing to clean up for local cache)
    print("[Falcon] AppSail shutting down.")


# ── FastAPI app ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Project Falcon Backend API",
    description=(
        "Catalyst AppSail FastAPI backend for KSP crime analytics. "
        "Provides geospatial clustering (DBSCAN/K-Means), TF-IDF case similarity, "
        "Louvain network graphs, SARIMA/ExponentialSmoothing forecasting, "
        "QuickML risk scoring, anomaly detection, and Kapoun forensic evidence verification."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API Routers ─────────────────────────────────────────────────────
app.include_router(geo.router)          # /api/districts, /api/clusters
app.include_router(similarity.router)   # /api/cases/similar
app.include_router(graph.router)        # /api/graph/accused/{id}, /api/graph/gangs
app.include_router(forecast.router)     # /api/forecast
app.include_router(risk.router)         # /api/offender/risk/{id}, /api/anomalies
app.include_router(stats.router)        # /api/stats
app.include_router(admin.router)        # /api/admin/*
app.include_router(forensics.router)    # /api/forensics/*


@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Project Falcon AppSail Backend",
        "version": "2.0.0",
        "phase": "Phase 2 — Analytics & ML Engine",
        "cache": cache_stats(),
        "endpoints": {
            "geospatial": [
                "GET /api/districts      — K-Means district risk (cache-backed, TTL=1h)",
                "GET /api/clusters       — DBSCAN crime clusters GeoJSON (cache-backed, TTL=30m)",
                "POST /api/cache/invalidate — flush geo cache on new data batch",
            ],
            "ml": [
                "GET /api/offender/risk/{id} — QuickML risk score 0-100",
                "GET /api/anomalies          — QuickML FIR anomaly detection feed",
                "GET /api/cases/similar      — TF-IDF cosine top-5 similar cases",
                "GET /api/forecast           — SARIMA/ETS 7d + 30d forecast",
                "GET /api/graph/accused/{id} — Louvain co-accused subgraph",
                "GET /api/graph/gangs        — Gang network overview",
            ],
            "forensics": [
                "POST /api/forensics/verify  — Kapoun Criteria evidence scoring (0-100)",
                "GET  /api/forensics/criteria — Kapoun rubric definition",
                "GET  /api/forensics/case/{id} — Case-linked evidence refs",
            ],
            "admin": [
                "GET  /api/admin/audit   — Security audit log",
                "GET  /api/admin/users   — User registry",
                "GET  /api/admin/victims — PII victim registry (Admin only)",
                "GET  /api/admin/stats   — System health metrics",
                "POST /api/admin/audit   — Append audit event",
            ],
            "kpi": ["GET /api/stats — Dashboard KPI metrics"],
        },
    }


@app.get("/health")
def health_check():
    """Lightweight health probe for Catalyst AppSail and load balancers."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "cache": cache_stats(),
        "timestamp": time.time(),
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BASE_DIR / "backend")],
    )
