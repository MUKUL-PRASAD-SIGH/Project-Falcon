"""
backend/auth/zoho_token.py
Auto-refreshing Zoho OAuth token manager.
Caches the access token in memory and refreshes it when it expires.
"""
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

ZOHO_TOKEN_URL    = "https://accounts.zoho.in/oauth/v2/token"
CLIENT_ID         = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET     = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN     = os.getenv("ZOHO_REFRESH_TOKEN")

# In-memory token cache
_access_token: str | None = None
_token_expiry: float = 0.0          # Unix timestamp when token expires


async def get_access_token() -> str:
    """
    Returns a valid Zoho access token.
    Automatically refreshes if expired or missing.
    """
    global _access_token, _token_expiry

    # Return cached token if still valid (with 60s buffer)
    if _access_token and time.time() < (_token_expiry - 60):
        return _access_token

    if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        raise RuntimeError(
            "Zoho OAuth is not configured. Set ZOHO_CLIENT_ID, "
            "ZOHO_CLIENT_SECRET, and ZOHO_REFRESH_TOKEN to enable live QuickML calls."
        )

    # Refresh the token
    params = {
        "grant_type":    "refresh_token",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(ZOHO_TOKEN_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    if "access_token" not in data:
        raise RuntimeError(f"Token refresh failed: {data}")

    _access_token  = data["access_token"]
    _token_expiry  = time.time() + data.get("expires_in", 3600)
    print("[ZohoToken] Access token refreshed successfully.")
    return _access_token


def get_auth_header() -> str:
    """Synchronous wrapper — returns the cached bearer string (for use in sync contexts)."""
    if _access_token:
        return f"Zoho-oauthtoken {_access_token}"
    return ""
