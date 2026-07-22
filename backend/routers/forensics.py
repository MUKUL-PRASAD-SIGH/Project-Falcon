"""
backend/routers/forensics.py
-----------------------------
Step 2.5 — Kapoun Digital Evidence Forensic Verification.

POST /api/forensics/verify
  - Accepts a list of URLs (digital evidence links) + optional case context
  - Scrapes each URL via SmartBrowz-style headless extraction (httpx + BeautifulSoup fallback)
  - Scores each source against the 5 Kapoun Criteria:
      1. Accuracy    — cross-reference signals (citations, data sources, corroboration)
      2. Authority   — domain credibility (gov.in, judiciary, .ac.in, known news outlets)
      3. Objectivity — language bias detection (hedging words, sensational language)
      4. Currency    — publication/update recency (last-modified, article date)
      5. Coverage    — depth & breadth (word count, topic completeness proxy)
  - Returns ranked evidence list with per-criteria scores (0–20 each, total 0–100)
  - Also exposes GET /api/forensics/criteria — returns the Kapoun rubric definition

GET /api/forensics/case/{case_id}
  - Returns pre-linked digital evidence for a known CaseMasterID (from similarity index)
"""

import re
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl

# Optional scraping dependencies — graceful fallback if not installed
try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    _BS4_AVAILABLE = True
except ImportError:
    _BS4_AVAILABLE = False

router = APIRouter(prefix="/api/forensics", tags=["Forensic Verification"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
AUDIT_FILE = BASE_DIR / "backend" / "data" / "audit_log.json"

# ── Kapoun Criteria Rubric ────────────────────────────────────────────────

KAPOUN_RUBRIC = {
    "Accuracy": {
        "weight": 20,
        "description": "Evidence is factually verifiable; cites primary sources; no unsubstantiated claims.",
        "signals": ["citation_count", "primary_source_refs", "data_tables", "footnotes"],
    },
    "Authority": {
        "weight": 20,
        "description": "Source is an authoritative institution (government, judiciary, academic, established press).",
        "signals": ["domain_tld", "author_credentials", "publisher_reputation", "institutional_affiliation"],
    },
    "Objectivity": {
        "weight": 20,
        "description": "Content is balanced; avoids emotional language; presents multiple perspectives.",
        "signals": ["sentiment_balance", "hedging_language", "sensational_words_absent", "perspective_diversity"],
    },
    "Currency": {
        "weight": 20,
        "description": "Information is up-to-date; publication or last-modified date within acceptable window.",
        "signals": ["publication_date", "last_modified_header", "content_freshness"],
    },
    "Coverage": {
        "weight": 20,
        "description": "Evidence is comprehensive; addresses all relevant aspects of the case.",
        "signals": ["word_count", "topic_breadth", "supporting_media", "cross_references"],
    },
}

# ── Trusted domain registry (Authority scoring) ───────────────────────────

AUTHORITY_DOMAINS = {
    ".gov.in": 20,        # Indian government
    ".nic.in": 20,        # National Informatics Centre
    ".judiciary.gov.in": 20,
    ".ac.in": 17,         # Indian academic institutions
    ".edu": 16,
    ".int": 15,           # International organisations
    "thehindu.com": 15,
    "indianexpress.com": 15,
    "ndtv.com": 14,
    "timesofindia.indiatimes.com": 14,
    "deccanherald.com": 15,  # Karnataka-specific, high credibility
    "scroll.in": 13,
    "thewire.in": 13,
    "reuters.com": 16,
    "bbc.com": 16,
    "wikipedia.org": 8,   # Secondary source — moderate
}

SENSATIONAL_WORDS = [
    "shocking", "explosive", "bombshell", "jaw-dropping", "unbelievable",
    "insane", "disgusting", "outrage", "fury", "chaos", "crisis",
    "exposed", "leaked", "secret", "hidden truth", "they don't want you to know",
]

# ── Pydantic models ───────────────────────────────────────────────────────

class EvidenceURL(BaseModel):
    url: str
    label: Optional[str] = None
    case_id: Optional[int] = None

class ForensicsVerifyRequest(BaseModel):
    urls: List[EvidenceURL]
    case_context: Optional[str] = None
    analyst: Optional[str] = "analyst@ksp.gov.in"

class KapounScore(BaseModel):
    accuracy: int
    authority: int
    objectivity: int
    currency: int
    coverage: int
    total: int
    grade: str
    rationale: dict

class EvidenceResult(BaseModel):
    url: str
    label: Optional[str]
    domain: str
    title: str
    word_count: int
    publication_date: Optional[str]
    kapoun: KapounScore
    verified_at: str
    status: str

# ── Scoring helpers ───────────────────────────────────────────────────────

def _extract_domain(url: str) -> str:
    """Extract hostname from URL string."""
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower()
    except Exception:
        return url

def _score_authority(domain: str) -> tuple[int, str]:
    """Return (score 0-20, rationale)."""
    for pattern, score in AUTHORITY_DOMAINS.items():
        if domain.endswith(pattern) or pattern in domain:
            return score, f"Recognised authoritative domain: {pattern}"
    if domain.endswith(".in"):
        return 10, "Indian domain (.in) — moderate authority"
    if domain.endswith(".com") or domain.endswith(".net"):
        return 8, "Commercial domain — authority unverified"
    return 5, "Unknown domain — low authority confidence"

def _score_objectivity(text: str) -> tuple[int, str]:
    """Penalise sensational language; reward balanced tone."""
    text_lower = text.lower()
    hits = [w for w in SENSATIONAL_WORDS if w in text_lower]
    base = 18
    penalty = min(len(hits) * 3, 14)  # max -14 for extreme sensationalism
    score = max(4, base - penalty)
    if hits:
        return score, f"Sensational language detected ({len(hits)} instances): {', '.join(hits[:3])}"
    return score, "No significant bias language detected — content appears balanced"

def _score_currency(date_str: Optional[str]) -> tuple[int, str]:
    """Score freshness of publication date."""
    if not date_str:
        return 10, "Publication date not found — currency unverifiable"
    try:
        # Try ISO 8601 first, then common formats
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                pub_date = datetime.strptime(date_str[:10], fmt[:len(date_str[:10])])
                break
            except ValueError:
                continue
        else:
            return 10, f"Unable to parse date: {date_str}"

        days_old = (datetime.now() - pub_date).days
        if days_old <= 30:
            return 20, f"Very recent ({days_old} days old) — high currency"
        elif days_old <= 180:
            return 16, f"Recent ({days_old} days old) — good currency"
        elif days_old <= 365:
            return 12, f"Moderately dated ({days_old} days old)"
        elif days_old <= 730:
            return 8, f"Older content ({days_old} days old) — review for updates"
        else:
            return 4, f"Outdated ({days_old} days old) — verify still relevant"
    except Exception:
        return 10, "Date parsing failed — currency unverifiable"

def _score_accuracy(text: str, word_count: int) -> tuple[int, str]:
    """Proxy accuracy via citation signals and data references."""
    score = 10  # baseline
    rationale_parts = []

    # Citation indicators
    citation_patterns = [r"\[\d+\]", r"\(\d{4}\)", r"et al\.", r"ibid", r"source:", r"reference:"]
    citation_hits = sum(1 for p in citation_patterns if re.search(p, text, re.IGNORECASE))
    score += min(citation_hits * 2, 6)
    if citation_hits:
        rationale_parts.append(f"{citation_hits} citation signals found")

    # Data tables / numbers
    number_density = len(re.findall(r"\b\d+[\.,]?\d*\b", text)) / max(word_count, 1)
    if number_density > 0.05:
        score += 2
        rationale_parts.append("High numerical data density — factual content")

    # Named entities (crude: capitalized word sequences)
    named_entity_count = len(re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+", text))
    if named_entity_count > 10:
        score += 2
        rationale_parts.append("Rich named entity references")

    score = min(score, 20)
    rationale = "; ".join(rationale_parts) if rationale_parts else "Basic accuracy signals present"
    return score, rationale

def _score_coverage(word_count: int, text: str) -> tuple[int, str]:
    """Score based on depth and breadth of content."""
    if word_count >= 1500:
        base, note = 18, "Long-form article — comprehensive coverage"
    elif word_count >= 800:
        base, note = 15, "Medium-length article — adequate coverage"
    elif word_count >= 300:
        base, note = 10, "Short article — limited coverage depth"
    else:
        base, note = 5, "Very short content — insufficient coverage"

    # Bonus for structured content (headings, lists)
    heading_count = len(re.findall(r"^\s*#{1,4}\s+", text, re.MULTILINE))
    if heading_count >= 3:
        base = min(base + 2, 20)
        note += f"; {heading_count} structured sections"

    return min(base, 20), note

def _grade(total: int) -> str:
    if total >= 85: return "A — Strong Evidence"
    if total >= 70: return "B — Reliable Evidence"
    if total >= 55: return "C — Acceptable Evidence"
    if total >= 40: return "D — Weak Evidence"
    return "F — Unreliable / Inadmissible"

# ── SmartBrowz-style headless fetch ──────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjectFalcon/2.0; KSP Intelligence)",
    "Accept-Language": "en-IN,en;q=0.9",
}

def _fetch_and_parse(url: str) -> dict:
    """
    Attempt to fetch and parse the URL.
    Uses httpx (async-friendly sync) with BeautifulSoup parsing.
    Falls back to synthetic scored result if fetch fails or libs unavailable.
    """
    if not _HTTPX_AVAILABLE:
        return _synthetic_result(url, reason="httpx not installed")

    try:
        with httpx.Client(timeout=8.0, follow_redirects=True, headers=HEADERS) as client:
            response = client.get(url)
            response.raise_for_status()
            content_type = response.headers.get("content-type", "")
            last_modified = response.headers.get("last-modified")

        if "html" not in content_type:
            return _synthetic_result(url, reason=f"Non-HTML content: {content_type}")

        if _BS4_AVAILABLE:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title = soup.find("title")
            title = title.get_text(strip=True) if title else "Untitled"

            # Extract article/main text
            for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)

            # Try to find publication date
            pub_date = None
            date_selectors = [
                {"name": "meta", "attrs": {"property": "article:published_time"}},
                {"name": "meta", "attrs": {"name": "date"}},
                {"name": "time"},
            ]
            for sel in date_selectors:
                tag = soup.find(**sel)
                if tag:
                    pub_date = tag.get("content") or tag.get("datetime") or tag.get_text(strip=True)
                    if pub_date:
                        break

            if not pub_date and last_modified:
                pub_date = last_modified[:10]

        else:
            # No BS4 — crude text extraction
            text = re.sub(r"<[^>]+>", " ", response.text)
            text = re.sub(r"\s+", " ", text).strip()
            title = "Extracted Content"
            pub_date = None

        word_count = len(text.split())
        return {
            "success": True,
            "title": title[:200],
            "text": text,
            "word_count": word_count,
            "publication_date": pub_date,
            "fetch_status": "live",
        }

    except Exception as exc:
        return _synthetic_result(url, reason=str(exc)[:100])


def _synthetic_result(url: str, reason: str = "fetch unavailable") -> dict:
    """
    When real fetch is unavailable, generate a deterministic synthetic score
    seeded from the URL hash — so the same URL always gets the same demo result.
    """
    seed = int(hashlib.md5(url.encode()).hexdigest(), 16) % 1000
    word_count = 400 + (seed % 1200)
    return {
        "success": False,
        "title": f"[Cached / Offline] {_extract_domain(url)}",
        "text": "Sample content used for offline scoring demonstration.",
        "word_count": word_count,
        "publication_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "fetch_status": f"offline_demo ({reason})",
    }


# ── Main scoring function ─────────────────────────────────────────────────

def _score_url(evidence: EvidenceURL) -> dict:
    url = evidence.url
    domain = _extract_domain(url)
    fetched = _fetch_and_parse(url)

    text = fetched["text"]
    word_count = fetched["word_count"]
    pub_date = fetched["publication_date"]
    title = fetched["title"]

    auth_score,  auth_rationale  = _score_authority(domain)
    obj_score,   obj_rationale   = _score_objectivity(text)
    curr_score,  curr_rationale  = _score_currency(pub_date)
    acc_score,   acc_rationale   = _score_accuracy(text, word_count)
    cov_score,   cov_rationale   = _score_coverage(word_count, text)

    total = acc_score + auth_score + obj_score + curr_score + cov_score

    return {
        "url": url,
        "label": evidence.label or domain,
        "domain": domain,
        "title": title,
        "word_count": word_count,
        "publication_date": pub_date,
        "fetch_status": fetched.get("fetch_status", "unknown"),
        "kapoun": {
            "accuracy": acc_score,
            "authority": auth_score,
            "objectivity": obj_score,
            "currency": curr_score,
            "coverage": cov_score,
            "total": total,
            "grade": _grade(total),
            "rationale": {
                "accuracy": acc_rationale,
                "authority": auth_rationale,
                "objectivity": obj_rationale,
                "currency": curr_rationale,
                "coverage": cov_rationale,
            },
        },
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "status": "verified" if fetched["success"] else "offline_demo",
    }


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/verify")
def verify_digital_evidence(request: ForensicsVerifyRequest, background_tasks: BackgroundTasks):
    """
    POST /api/forensics/verify

    Accepts up to 10 evidence URLs.
    Scores each against the 5 Kapoun Criteria (Accuracy, Authority,
    Objectivity, Currency, Coverage) — total 0–100.

    Returns ranked list (highest Kapoun total first).
    """
    if len(request.urls) > 10:
        raise HTTPException(status_code=422, detail="Maximum 10 URLs per request.")
    if not request.urls:
        raise HTTPException(status_code=422, detail="At least 1 URL required.")

    results = []
    for ev in request.urls:
        try:
            scored = _score_url(ev)
            results.append(scored)
        except Exception as exc:
            results.append({
                "url": ev.url,
                "label": ev.label,
                "domain": _extract_domain(ev.url),
                "error": str(exc)[:200],
                "kapoun": None,
                "status": "error",
                "verified_at": datetime.now(timezone.utc).isoformat(),
            })

    # Rank by total Kapoun score (descending)
    ranked = sorted(results, key=lambda r: (r.get("kapoun") or {}).get("total", -1), reverse=True)

    # Background: log this forensics query to the audit trail
    background_tasks.add_task(
        _append_audit,
        analyst=request.analyst,
        url_count=len(request.urls),
        case_context=request.case_context or "",
    )

    top_score = ranked[0].get("kapoun", {}).get("total", 0) if ranked else 0
    return {
        "status": "success",
        "verified_count": len(results),
        "case_context": request.case_context,
        "kapoun_criteria_max": 100,
        "top_score": top_score,
        "top_grade": _grade(top_score),
        "evidence": ranked,
    }


@router.get("/criteria")
def get_kapoun_criteria():
    """
    GET /api/forensics/criteria

    Returns the full Kapoun Criteria rubric used for evidence scoring.
    Useful for the frontend to render scoring explanations.
    """
    return {
        "status": "success",
        "rubric": KAPOUN_RUBRIC,
        "max_score": 100,
        "grade_scale": {
            "A (85–100)": "Strong Evidence — admissible, high reliability",
            "B (70–84)":  "Reliable Evidence — corroboration recommended",
            "C (55–69)":  "Acceptable Evidence — use with caution",
            "D (40–54)":  "Weak Evidence — significant concerns",
            "F (0–39)":   "Unreliable / Inadmissible — do not rely on",
        },
    }


@router.get("/case/{case_id}")
def get_case_evidence(case_id: int):
    """
    GET /api/forensics/case/{case_id}

    Returns pre-linked digital evidence references for a given CaseMasterID.
    In production, these would come from the Stratus-stored forensic index;
    here they are derived from the TF-IDF similarity metadata.
    """
    SIM_FILE = BASE_DIR / "ml" / "outputs" / "similarity_index.json"
    if not SIM_FILE.exists():
        raise HTTPException(status_code=404, detail="Similarity index not found.")

    with open(SIM_FILE, "r", encoding="utf-8") as f:
        sim_data = json.load(f)

    key = str(case_id)
    if key not in sim_data:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not in similarity index.")

    similar = sim_data[key][:5]
    # Synthesise evidence links from case metadata
    evidence_refs = []
    for i, s in enumerate(similar):
        evidence_refs.append({
            "case_id": s.get("case_id", case_id + i),
            "similarity_score": s.get("score", 0.0),
            "crime_head": s.get("crime_head", "Unknown"),
            "district": s.get("district", "Unknown"),
            "suggested_evidence_query": (
                f"{s.get('crime_head', 'crime')} {s.get('district', 'Karnataka')} site:gov.in OR site:judiciary.gov.in"
            ),
        })

    return {
        "status": "success",
        "case_id": case_id,
        "linked_cases": len(evidence_refs),
        "evidence_refs": evidence_refs,
        "tip": "Use suggested_evidence_query in POST /api/forensics/verify to score each source.",
    }


# ── Background audit logger ────────────────────────────────────────────────

def _append_audit(analyst: str, url_count: int, case_context: str):
    """Append forensics verification event to the persistent audit log."""
    try:
        AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        if AUDIT_FILE.exists():
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
        logs.append({
            "user": analyst,
            "action": "forensics_verify",
            "query": f"Verified {url_count} URL(s) | context: {case_context[:80]}",
            "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "ip": "0.0.0.0",
            "role": "Analyst",
        })
        with open(AUDIT_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass  # Audit failure must never break the main response
