"""Optional external integrations with safe local fallbacks.

The UI always has a concrete API contract: PDF export works locally, while
speech transcription either uses a configured Zia-compatible gateway or
returns an explicit typed-input fallback instead of a 404 response.
"""

import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["Document & Voice Integrations"])

ZIA_STT_URL = os.getenv("ZIA_STT_URL")
ZIA_STT_KEY = os.getenv("ZIA_STT_KEY")
MAX_AUDIO_BYTES = 15 * 1024 * 1024


class EvidenceExportRequest(BaseModel):
    messages: list[dict] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


def _pdf_escape(value: str) -> str:
    safe = value.encode("latin-1", "replace").decode("latin-1")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_line(value: str, width: int = 96) -> list[str]:
    words = value.split()
    if not words:
        return [""]
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    lines.append(line)
    return lines


def _build_pdf(payload: EvidenceExportRequest) -> bytes:
    """Create a compact evidence PDF without adding a runtime dependency."""
    lines = [
        "Project Falcon Evidence Trail",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]
    for message in payload.messages[:100]:
        role = str(message.get("role", "note")).upper()
        text = str(message.get("text", "")).strip()
        if text:
            lines.extend(_wrap_line(f"{role}: {text}"))
    if payload.citations:
        lines.extend(["", "Citations:"])
        lines.extend(_wrap_line(", ".join(str(citation) for citation in payload.citations[:250])))
    if len(lines) <= 3:
        lines.append("No chat messages or citations were supplied.")

    content = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
    for line in lines[:48]:
        content.append(f"({_pdf_escape(line)}) Tj")
        content.append("T*")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return bytes(pdf)


@router.post("/export/pdf")
def export_evidence_pdf(payload: EvidenceExportRequest):
    document = _build_pdf(payload)
    return Response(
        content=document,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=falcon-evidence-trail.pdf"},
    )


@router.post("/voice/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), language: str = Form("EN")):
    if not ZIA_STT_URL:
        return {
            "text": "",
            "is_live": False,
            "message": "Voice transcription is not configured. Type your query instead.",
        }

    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Audio recording is empty.")
    if len(content) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio recording exceeds the 15 MB limit.")

    headers = {"X-ZIA-STT-KEY": ZIA_STT_KEY} if ZIA_STT_KEY else {}
    files = {"audio": (audio.filename or "recording.webm", content, audio.content_type or "audio/webm")}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(ZIA_STT_URL, data={"language": language}, files=files, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Voice transcription service is unavailable.") from exc

    data = response.json()
    text = data.get("text") or data.get("transcript") or data.get("response") or ""
    return {"text": str(text), "is_live": True, "language": language}
