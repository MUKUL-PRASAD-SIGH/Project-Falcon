"""End-to-end smoke test for a locally running Project Falcon backend.

Start the API first with:
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("FALCON_API_URL", "http://127.0.0.1:8000").rstrip("/")


def request(method: str, path: str, body=None, headers=None):
    payload = None if body is None else json.dumps(body).encode("utf-8")
    request_headers = {"Content-Type": "application/json"} if payload else {}
    request_headers.update(headers or {})
    req = urllib.request.Request(BASE_URL + path, data=payload, headers=request_headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status, response.headers, response.read()


def check(name, method, path, body=None, validator=None):
    try:
        status, headers, content = request(method, path, body)
        if status != 200:
            raise AssertionError(f"unexpected HTTP {status}")
        data = json.loads(content) if "application/json" in headers.get_content_type() else content
        if validator:
            validator(data)
        print(f"[PASS] {name}")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, AssertionError, json.JSONDecodeError) as exc:
        print(f"[FAIL] {name}: {exc}")
        return False


def has_keys(*keys):
    def validate(data):
        missing = [key for key in keys if key not in data]
        if missing:
            raise AssertionError(f"missing keys: {', '.join(missing)}")
    return validate


def has_data_keys(*keys):
    def validate(data):
        nested = data.get("data", {})
        missing = [key for key in keys if key not in nested]
        if missing:
            raise AssertionError(f"missing data keys: {', '.join(missing)}")
    return validate


def valid_pdf(data):
    if not data.startswith(b"%PDF-"):
        raise AssertionError("response is not a PDF")


def test_voice_fallback():
    boundary = "FalconE2EBoundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="language"\r\n\r\n'
        "EN\r\n"
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="audio"; filename="sample.webm"\r\n'
        "Content-Type: audio/webm\r\n\r\n"
    ).encode("utf-8") + b"demo-audio" + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + "/api/voice/transcribe",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.load(response)
    if payload["is_live"] or payload["text"] or not payload["message"]:
        raise AssertionError("voice fallback response is incomplete")
    print("[PASS] voice fallback")


TESTS = [
    ("service root", "GET", "/", None, has_keys("status", "endpoints")),
    ("health", "GET", "/health", None, has_keys("status", "cache")),
    ("dashboard stats", "GET", "/api/stats", None, has_keys("status", "data")),
    ("district risk", "GET", "/api/districts", None, has_keys("status", "districts")),
    ("crime clusters", "GET", "/api/clusters", None, has_keys("status", "features")),
    ("forecast", "GET", "/api/forecast", None, has_keys("status", "chart_data")),
    ("risk profile", "GET", "/api/offender/risk/1", None, has_keys("status", "data")),
    ("anomaly feed", "GET", "/api/anomalies", None, has_keys("status", "anomalies")),
    ("similar cases", "GET", "/api/cases/similar?case_id=1", None, has_keys("status", "similar_cases")),
    ("accused graph", "GET", "/api/graph/accused/1", None, has_data_keys("nodes", "edges")),
    ("gang overview", "GET", "/api/graph/gangs", None, has_keys("status", "gangs")),
    ("forensics rubric", "GET", "/api/forensics/criteria", None, has_keys("status", "rubric")),
    ("admin stats", "GET", "/api/admin/stats", None, has_keys("status", "data")),
    ("offline chat", "POST", "/api/chat/query", {"query": "Where are the crime hotspots?"}, has_keys("status", "response", "is_live")),
    ("evidence PDF", "POST", "/api/export/pdf", {"messages": [{"role": "user", "text": "Test evidence"}], "citations": ["FIR_1"]}, valid_pdf),
]


def main():
    passed = sum(check(*test) for test in TESTS)
    try:
        test_voice_fallback()
        passed += 1
    except (urllib.error.URLError, urllib.error.HTTPError, AssertionError, json.JSONDecodeError) as exc:
        print(f"[FAIL] voice fallback: {exc}")
    total = len(TESTS) + 1
    print(f"\n{passed}/{total} backend checks passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
