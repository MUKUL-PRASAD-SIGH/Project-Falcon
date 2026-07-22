"""
backend/routers/graph.py
-------------------------
NetworkX + Louvain gang network graph endpoints.

GET /api/graph/accused/{accused_id}?depth={1-3}
  Returns a co-accused ego subgraph for the requested AccusedMasterID.

  Strategy (fastest → slowest):
    1. Return pre-built ego from gang_network.json index (O(1), <5ms)
    2. Fall back to sample_subgraph.json (demo / unknown IDs)
    3. If neither exists, raise 404

  The full NetworkX rebuild (12s) only happens in ml/models/network_graph.py
  (run_pipeline), never on a live API request.

GET /api/graph/gangs
  Full community list (Louvain) from gang_network.json.
"""

import json
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

from backend.middleware.cache import get_cached, set_cached

router = APIRouter(prefix="/api/graph", tags=["Network Graph"])

BASE_DIR             = Path(__file__).resolve().parent.parent.parent
SAMPLE_SUBGRAPH_FILE = BASE_DIR / "ml" / "outputs" / "sample_subgraph.json"
GANG_NETWORK_FILE    = BASE_DIR / "ml" / "outputs" / "gang_network.json"


def _load_gang_index() -> list | None:
    """Load gang_network.json from cache or disk (TTL 2h)."""
    cached = get_cached("gang_network")
    if cached is not None:
        return cached
    if GANG_NETWORK_FILE.exists():
        with open(GANG_NETWORK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        set_cached("gang_network", data)
        return data
    return None


def _build_ego_from_community(accused_id: int, gang_index: list, depth: int = 2) -> dict | None:
    """
    Extract a lightweight ego-subgraph from the pre-built community index.
    Returns None if accused_id not found in any community.
    """
    # Find the community containing this accused (top_members list)
    target_community = None
    for community in gang_index:
        members = community.get("top_members", [])
        ids = [m.get("id") for m in members]
        if accused_id in ids:
            target_community = community
            break

    if target_community is None:
        return None

    members = target_community.get("top_members", [])
    # For depth=1, include direct community members only (cap at 15 nodes)
    # For depth=2+, include full community (cap at 30)
    cap = 15 if depth == 1 else 30
    nodes_raw = members[:cap]

    nodes = []
    for m in nodes_raw:
        mid = m.get("id")  # gang_network.json uses 'id' not 'accused_id'
        nodes.append({
            "id": str(mid),
            "accused_id": mid,
            "name": m.get("name", f"Accused #{mid}"),
            "risk_score": m.get("risk_score", 50.0),
            "community": target_community.get("community_id", 0),
            "pagerank": m.get("pagerank", 0.001),
            "is_leader": mid == accused_id,
        })

    # Build edges between all node pairs that share a community (co-accused proxy)
    node_ids = [n["id"] for n in nodes]
    edges = []
    for i, a in enumerate(node_ids):
        for b in node_ids[i + 1:]:
            edges.append({"source": a, "target": b, "weight": 1})

    return {
        "center_accused_id": accused_id,
        "community_id": target_community.get("community_id", 0),
        "community_size": target_community.get("member_count", len(members)),
        "avg_risk_score": target_community.get("avg_risk_score", 50.0),
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


# ── GET /api/graph/accused/{accused_id} ─────────────────────────────────────

@router.get("/accused/{accused_id}")
def get_accused_subgraph(
    accused_id: int,
    depth: int = Query(2, ge=1, le=3, description="Hop depth for ego subgraph"),
):
    """
    Returns co-accused ego subgraph for AccusedMasterID.

    Served entirely from pre-built JSON (gang_network.json) — no NetworkX rebuild
    on the API path. Response time: <10ms from cache, <50ms from disk.
    """
    # 1. Try pre-built community index (fast path)
    gang_index = _load_gang_index()
    if gang_index:
        ego = _build_ego_from_community(accused_id, gang_index, depth)
        if ego:
            return {"status": "success", "source": "prebuilt", "data": ego}

    # 2. Fallback — return sample subgraph for demo/unknown IDs
    if SAMPLE_SUBGRAPH_FILE.exists():
        with open(SAMPLE_SUBGRAPH_FILE, "r", encoding="utf-8") as f:
            sample = json.load(f)
        # Patch the center node to reflect the requested accused_id
        sample["center_accused_id"] = accused_id
        if sample.get("nodes"):
            sample["nodes"][0]["accused_id"] = accused_id
            sample["nodes"][0]["id"] = str(accused_id)
            sample["nodes"][0]["is_leader"] = True
        return {
            "status": "success",
            "source": "sample_fallback",
            "note": f"AccusedID {accused_id} not in index — showing representative community sample.",
            "data": sample,
        }

    raise HTTPException(
        status_code=404,
        detail=f"No graph data found for accused {accused_id}. Run ML pipeline first."
    )


# ── GET /api/graph/gangs ────────────────────────────────────────────────────

@router.get("/gangs")
def get_gang_overview(
    min_size: int = Query(2, ge=1, description="Minimum community size to return"),
    top_n: int = Query(50, ge=1, le=500, description="Max communities to return"),
):
    """
    Returns top-N gang communities from the Louvain network (pre-built index).
    Sorted by avg_risk_score descending.
    Cache-backed (TTL = 2h).
    """
    gang_index = _load_gang_index()
    if gang_index is None:
        raise HTTPException(
            status_code=404,
            detail="Gang network not found. Run ML pipeline first."
        )

    filtered = [g for g in gang_index if g.get("member_count", 0) >= min_size]
    sorted_gangs = sorted(filtered, key=lambda g: g.get("avg_risk_score", 0), reverse=True)
    top = sorted_gangs[:top_n]

    return {
        "status": "success",
        "total_communities": len(gang_index),
        "returned": len(top),
        "gangs": top,
    }
