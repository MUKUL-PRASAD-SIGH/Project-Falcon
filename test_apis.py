"""Quick diagnostic — tests the RAG and LLM APIs with the current token."""
import asyncio
import os
import sys
sys.path.insert(0, '.')

async def main():
    import httpx
    from dotenv import load_dotenv
    load_dotenv()

    # Step 1: refresh token
    import urllib.request, urllib.parse, json
    params = urllib.parse.urlencode({
        'grant_type':    'refresh_token',
        'client_id':     os.getenv('ZOHO_CLIENT_ID'),
        'client_secret': os.getenv('ZOHO_CLIENT_SECRET'),
        'refresh_token': os.getenv('ZOHO_REFRESH_TOKEN'),
    }).encode()
    req = urllib.request.Request('https://accounts.zoho.in/oauth/v2/token', data=params, method='POST')
    with urllib.request.urlopen(req) as r:
        tok = json.loads(r.read())
    access = tok['access_token']
    print(f"[TOKEN] OK: {access[:30]}...\n")

    org = os.getenv('CATALYST_ORG_ID', '60079106947')
    project = '54459000000013048'

    # Step 2: Test RAG — no documents filter
    print("=== RAG (no documents filter) ===")
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"https://api.catalyst.zoho.in/quickml/v1/project/{project}/rag/answer",
            headers={"Authorization": f"Zoho-oauthtoken {access}", "CATALYST-ORG": org, "Content-Type": "application/json"},
            json={"query": "robbery in Bengaluru"}
        )
        print(f"Status: {r.status_code}")
        print(f"Body:   {r.text[:500]}\n")

    # Step 3: Test LLM — Bearer format
    print("=== LLM (Bearer token) ===")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"https://api.catalyst.zoho.in/quickml/v1/project/{project}/glm/chat",
            headers={"Authorization": f"Bearer {access}", "CATALYST-ORG": org, "Content-Type": "application/json"},
            json={
                "model": "crm-di-glm47b_30b_it",
                "messages": [{"role": "user", "content": "Say hello in one sentence."}],
                "max_tokens": 50,
                "temperature": 0.3,
                "stream": False
            }
        )
        print(f"Status: {r.status_code}")
        print(f"Body:   {r.text[:500]}\n")

    # Step 4: Test LLM — Zoho-oauthtoken format
    print("=== LLM (Zoho-oauthtoken) ===")
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"https://api.catalyst.zoho.in/quickml/v1/project/{project}/glm/chat",
            headers={"Authorization": f"Zoho-oauthtoken {access}", "CATALYST-ORG": org, "Content-Type": "application/json"},
            json={
                "model": "crm-di-glm47b_30b_it",
                "messages": [{"role": "user", "content": "Say hello in one sentence."}],
                "max_tokens": 50,
                "temperature": 0.3,
                "stream": False
            }
        )
        print(f"Status: {r.status_code}")
        print(f"Body:   {r.text[:500]}\n")

asyncio.run(main())
