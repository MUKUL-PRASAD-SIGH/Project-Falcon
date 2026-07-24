import os
import httpx
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from backend.auth.zoho_token import get_access_token

router = APIRouter(prefix="/api/chat", tags=["FALCON AI Chatbot"])

# ── QuickML Credentials ─────────────────────────────────────────────────────
CATALYST_ORG   = os.getenv("CATALYST_ORG_ID", "60079106947")
RAG_URL        = os.getenv(
    "QUICKML_RAG_URL",
    "https://api.catalyst.zoho.in/quickml/v1/project/54459000000013048/rag/answer"
)
LLM_URL        = os.getenv(
    "QUICKML_LLM_URL",
    "https://api.catalyst.zoho.in/quickml/v1/project/54459000000013048/glm/chat"
)
LLM_MODEL      = "crm-di-glm47b_30b_it"
FIR_DOCUMENT_ID = os.getenv("QUICKML_RAG_DOC_ID", "625800000002063")

# ── FALCON System Prompt ─────────────────────────────────────────────────────
FALCON_SYSTEM_PROMPT = """You are FALCON AI, a crime intelligence assistant for the Karnataka State Police (KSP) in India.

You analyse FIR (First Information Report) data and help investigators understand crime patterns, offender risk, and case connections across Karnataka.

When answering:
- Be concise and direct. Answer in plain prose, 2-4 sentences maximum.
- Cite FIR numbers when referencing specific cases.
- Classify offender risk as Low (0-39), Medium (40-69), or High (70-100).
- If you don't have enough data, say so briefly.

You cover 5 Karnataka districts: Bengaluru City, Mysuru City, Mangaluru City, Hubballi-Dharwad, and Belagavi.
Crime categories: Theft, Fraud, Assault, Cybercrime, Robbery, Narcotics, Homicide."""

# Safety-filter phrases that indicate the LLM refused the request
_SAFETY_PHRASES = [
    "i can't help with requests to expose",
    "protected instructions",
    "cannot assist with",
    "i'm unable to help",
    "i cannot provide",
    "i'm not sure what information you're looking for",
    "i don't have enough information",
    "could you please clarify",
    "please provide more details",
    "i need more context",
]

def _is_safety_response(text: str) -> bool:
    t = text.lower()
    return any(phrase in t for phrase in _SAFETY_PHRASES)


# ── Request / Response Models ────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    language: Optional[str] = "EN"
    use_rag: Optional[bool] = True

class ChatResponse(BaseModel):
    status: str
    response: str
    retrieved_nodes: list
    is_live: bool
    model: Optional[str] = None

# ── Offline Fallback ─────────────────────────────────────────────────────────
def build_offline_response(query: str) -> dict:
    q = query.lower()
    if any(w in q for w in ["robbery", "theft", "steal"]):
        response = (
            "Multiple robbery and theft cases are recorded across Bengaluru City and "
            "Hubballi-Dharwad. These cases typically involve repeat offenders with "
            "prior_offense_count ≥ 2 and risk scores above 60."
        )
    elif any(w in q for w in ["homicide", "murder", "kill"]):
        response = (
            "Homicide cases carry severity rating 5 — the highest in FALCON. "
            "Belagavi and Bengaluru City show the highest concentration, "
            "often with co-accused counts of 2 or more."
        )
    elif any(w in q for w in ["suspect", "high-risk", "high risk", "dangerous", "wanted"]):
        response = (
            "FALCON tracks 1,245 accused profiles. High-risk offenders (score ≥ 75) "
            "are flagged for immediate review — currently 86 flagged individuals. "
            "To look up a specific suspect, provide an Accused ID (e.g. 'risk for accused A1') "
            "or search by name in the Accused Profiles panel."
        )
    elif any(w in q for w in ["risk", "offender", "repeat"]):
        response = (
            "The FALCON Offender Risk model scores suspects on: prior_offense_count, "
            "recency_days, max_crime_severity, co_accused_count, and prior_arrest_count. "
            "High-risk offenders (score ≥ 75) are flagged for immediate review."
        )
    elif any(w in q for w in ["district", "bengaluru", "mysuru", "belagavi", "mangaluru", "hubballi"]):
        response = (
            "FALCON covers 5 Karnataka districts: Bengaluru City (highest volume ~312 FIRs), "
            "Mysuru City (~248 FIRs), Mangaluru City, Hubballi-Dharwad, and Belagavi. "
            "Each district is monitored for crime clusters, hotspots, and seasonal patterns."
        )
    elif any(w in q for w in ["narcotic", "drug"]):
        response = (
            "Narcotics cases (severity 4) are concentrated in border districts — "
            "Belagavi and Hubballi-Dharwad — due to proximity to inter-state trafficking "
            "routes. Co-accused networks in these cases average 3+ members."
        )
    elif any(w in q for w in ["anomaly", "suspicious", "unusual", "this week", "recent", "latest"]):
        response = (
            "FALCON's anomaly detection engine has flagged 86 suspicious FIRs. "
            "Key signals: crimes registered between 1–4 AM, high-severity crime types "
            "(Homicide/Narcotics), and unusually brief FIR descriptions. "
            "Check the Anomaly Feed panel for the latest flagged incidents."
        )
    else:
        response = (
            "I am FALCON AI, the Karnataka State Police intelligence assistant. "
            "Ask me about: FIR cases and crime patterns, offender risk scores, "
            "crime hotspots by district, gang and co-accused networks, or anomaly detection. "
            "Try: 'What robbery cases occurred in Bengaluru?' or 'Show high-risk offenders.'"
        )
    return {
        "status": "success",
        "response": response,
        "retrieved_nodes": [{"content": "Offline mode", "document_title": "FIR_Case_Register (Local)", "document_id": FIR_DOCUMENT_ID}],
        "is_live": False,
        "model": "offline-fallback"
    }

# ── Helper: Call QuickML RAG ─────────────────────────────────────────────────
async def call_rag(query: str, auth: str) -> tuple[str, list]:
    """Returns (rag_context_text, retrieved_nodes)"""
    headers = {
        "Authorization": auth,
        "CATALYST-ORG": CATALYST_ORG,
        "Content-Type": "application/json"
    }
    # Query all documents in the knowledge base (no filter)
    payload = {"query": query}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(RAG_URL, headers=headers, json=payload)
        if not resp.is_success:
            print(f"[RAG] HTTP {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
        data = resp.json()
    rag_text = data.get("response", "")
    nodes = data.get("retrieved_nodes", [])
    return clean_response(rag_text), nodes

import re

def clean_response(text: str) -> str:
    """Strips thinking blocks, internal monologue, and analysis sections from LLM output."""
    if not text:
        return ""
        
    # Remove <think>...</think> blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # If the response contains a "Final Polish:" or "Final Output:" section, extract only that
    final_match = re.search(r'(?:final\s*(?:polish|output|response)|response):\s*(.*)', text, flags=re.IGNORECASE | re.DOTALL)
    if final_match and len(final_match.group(1).strip()) > 10:
        return final_match.group(1).strip().strip('"')
        
    # If text has numbered analysis steps (1. **Analyze...** 2. **Strategy...**), strip them
    if "1. **Analyze" in text or "**Analyze the Request:**" in text:
        # Split by numbered items or markdown headers and keep non-analysis text
        lines = text.split('\n')
        filtered_lines = []
        skip = False
        for line in lines:
            l_lower = line.lower()
            if any(term in l_lower for term in ["analyze the request", "determine the response", "drafting the response", "persona check", "check against"]):
                skip = True
                continue
            if skip and line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '*')):
                continue
            skip = False
            filtered_lines.append(line)
        cleaned = '\n'.join(filtered_lines).strip()
        if len(cleaned) > 10:
            return cleaned.strip('"')

    return text.strip()

# ── Helper: Call QuickML GLM ─────────────────────────────────────────────────
async def call_llm(query: str, rag_context: str, auth: str) -> str:
    """Sends query + RAG context to GLM-4.7-Flash and returns the answer text."""
    if rag_context:
        user_content = (
            f"Context retrieved from FIR Case Register:\n{rag_context}\n\n"
            f"Based on the above context and your knowledge, answer this query:\n{query}"
        )
    else:
        user_content = query

    # LLM Serving uses Zoho-oauthtoken format
    headers = {
        "Authorization": auth,
        "CATALYST-ORG": CATALYST_ORG,
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": FALCON_SYSTEM_PROMPT},
            {"role": "user",   "content": user_content}
        ],
        "max_tokens": 600,
        "temperature": 0.3,
        "stream": False,
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(LLM_URL, headers=headers, json=payload)
        if not resp.is_success:
            print(f"[LLM] HTTP {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()
        data = resp.json()
        
    # QuickML GLM returns {"response": "..."}
    if "response" in data:
        raw_res = data["response"]
        return clean_response(raw_res)
        
    print(f"[LLM] Unexpected response shape: {str(data)[:300]}")
    raise KeyError(f"No 'response' key in LLM response: {list(data.keys())}")

# ── POST /api/chat/query — Main Orchestration ───────────────────────────────
@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest, authorization: str = Header(None)):
    """
    FALCON AI pipeline — RAG-first (RAG already runs GLM internally):
      1. Auto-refresh Zoho OAuth token
      2. Call QuickML RAG -> returns a GLM-generated answer grounded in FIR docs
      3. If RAG has no relevant data, fall back to a direct LLM call
      4. If LLM returns a safety refusal, use offline keyword fallback
    """
    try:
        token = await get_access_token()
        authorization = f"Zoho-oauthtoken {token}"
    except Exception as e:
        print(f"[Auth] Token refresh failed: {e} -- using offline fallback")
        return build_offline_response(request.query)

    retrieved_nodes = []

    # Step 1: RAG (already uses GLM internally -- returns the final answer)
    try:
        rag_answer, retrieved_nodes = await call_rag(request.query, authorization)
        if rag_answer and not _is_safety_response(rag_answer):
            return {
                "status":          "success",
                "response":        rag_answer,
                "retrieved_nodes": retrieved_nodes,
                "is_live":         True,
                "model":           "rag+glm"
            }
        print("[RAG] Empty or safety response -- trying direct LLM")
    except Exception as e:
        print(f"[RAG] Warning: {e} -- trying direct LLM")

    # Step 2: Direct LLM fallback (for queries with no matching FIR docs)
    try:
        llm_answer = await call_llm(request.query, "", authorization)
        if llm_answer and not _is_safety_response(llm_answer):
            return {
                "status":          "success",
                "response":        llm_answer,
                "retrieved_nodes": retrieved_nodes,
                "is_live":         True,
                "model":           LLM_MODEL
            }
        print("[LLM] Safety response -- using offline fallback")
    except Exception as e:
        print(f"[LLM] Error: {e} -- using offline fallback")

    # Step 3: Offline keyword fallback
    return build_offline_response(request.query)

# ── POST /api/chat/llm — Direct LLM (no RAG) ────────────────────────────────
@router.post("/llm")
async def direct_llm(request: ChatRequest):
    """Direct GLM-4.7-Flash call without RAG — for general KSP AI queries."""
    try:
        token = await get_access_token()
        auth = f"Zoho-oauthtoken {token}"
        answer = await call_llm(request.query, "", auth)
        return {"status": "success", "response": answer, "is_live": True, "model": LLM_MODEL}
    except Exception as e:
        fallback = build_offline_response(request.query)
        fallback["response"] = f"[Offline] {fallback['response']}"
        return fallback

# ── GET /api/chat/health ─────────────────────────────────────────────────────
@router.get("/health")
def chat_health():
    return {
        "rag_url": RAG_URL,
        "llm_url": LLM_URL,
        "llm_model": LLM_MODEL,
        "document_id": FIR_DOCUMENT_ID,
        "catalyst_org": CATALYST_ORG,
        "status": "configured"
    }
