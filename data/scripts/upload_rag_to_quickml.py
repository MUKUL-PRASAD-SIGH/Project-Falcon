"""
data/scripts/upload_rag_to_quickml.py
--------------------------------------
Re-uploads all 1000 FIR documents from fir_rag_documents.csv
to the Zoho QuickML Knowledge Base (FIR_Case_Register).

Steps:
  1. Clears (deletes) existing documents from the Knowledge Base
  2. Re-uploads all fresh documents in batches of 50

Usage:
  python data/scripts/upload_rag_to_quickml.py
"""

import os
import sys
import json
import time
import csv
import asyncio
import httpx
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from backend.auth.zoho_token import get_access_token

BASE_DIR   = Path(__file__).resolve().parent.parent.parent
CSV_PATH   = BASE_DIR / "data" / "processed" / "fir_rag_documents.csv"

# QuickML Knowledge Base API
QUICKML_BASE     = "https://api.catalyst.zoho.in/quickml/v1"
RAG_PROJECT_ID   = os.getenv("QUICKML_PROJECT_ID", "54459000000013048")
KB_NAME          = "FIR_Case_Register"
BATCH_SIZE       = 50  # docs per upload batch


async def get_or_create_knowledge_base(client: httpx.AsyncClient, headers: dict) -> str:
    """Returns the Knowledge Base ID, creating it if it doesn't exist."""
    url = f"{QUICKML_BASE}/project/{RAG_PROJECT_ID}/knowledgebase"
    resp = await client.get(url, headers=headers)
    if resp.is_success:
        kbs = resp.json().get("data", [])
        for kb in kbs:
            if kb.get("name") == KB_NAME or kb.get("kb_name") == KB_NAME:
                kb_id = kb.get("kb_id") or kb.get("id")
                print(f"[KB] Found existing Knowledge Base '{KB_NAME}' — ID: {kb_id}")
                return str(kb_id)
    
    # Create new KB
    create_resp = await client.post(url, headers=headers, json={"name": KB_NAME})
    if create_resp.is_success:
        kb_id = create_resp.json()["data"].get("kb_id") or create_resp.json()["data"].get("id")
        print(f"[KB] Created new Knowledge Base '{KB_NAME}' — ID: {kb_id}")
        return str(kb_id)
    
    raise RuntimeError(f"Failed to get/create KB: {create_resp.status_code} {create_resp.text[:300]}")


async def delete_all_documents(client: httpx.AsyncClient, headers: dict, kb_id: str):
    """Deletes all existing documents from the Knowledge Base."""
    url = f"{QUICKML_BASE}/project/{RAG_PROJECT_ID}/knowledgebase/{kb_id}/document"
    resp = await client.get(url, headers=headers)
    if not resp.is_success:
        print(f"[KB] Could not list documents (may already be empty): {resp.status_code}")
        return
    
    docs = resp.json().get("data", {}).get("documents", []) or resp.json().get("data", [])
    if not docs:
        print("[KB] Knowledge Base is already empty — skipping deletion.")
        return
    
    print(f"[KB] Deleting {len(docs)} existing documents...")
    for doc in docs:
        doc_id = doc.get("document_id") or doc.get("id")
        del_resp = await client.delete(
            f"{QUICKML_BASE}/project/{RAG_PROJECT_ID}/knowledgebase/{kb_id}/document/{doc_id}",
            headers=headers
        )
        if not del_resp.is_success:
            print(f"  [WARN] Failed to delete doc {doc_id}: {del_resp.status_code}")
    print(f"[KB] Deletion complete.")


async def upload_batch(client: httpx.AsyncClient, headers: dict, kb_id: str, batch: list, batch_num: int):
    """Uploads a batch of documents to the Knowledge Base."""
    url = f"{QUICKML_BASE}/project/{RAG_PROJECT_ID}/knowledgebase/{kb_id}/document"
    payload = {"documents": batch}
    
    resp = await client.post(url, headers=headers, json=payload, timeout=60.0)
    if resp.is_success:
        print(f"  [OK] Batch {batch_num}: uploaded {len(batch)} documents.")
    else:
        print(f"  [ERR] Batch {batch_num} failed: {resp.status_code} — {resp.text[:200]}")


async def main():
    print("=" * 60)
    print("  FALCON — QuickML Knowledge Base Upload Script")
    print("=" * 60)
    
    # 1. Load CSV
    if not CSV_PATH.exists():
        print(f"[ERR] CSV not found: {CSV_PATH}")
        print("      Run: python data/scripts/index_rag.py first")
        sys.exit(1)
    
    documents = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            documents.append({
                "document_id": row["document_id"],
                "content":     row["text"],
                "metadata": {
                    "case_master_id": row.get("case_master_id", ""),
                    "crime_no":       row.get("crime_no", "")
                }
            })
    
    print(f"[CSV] Loaded {len(documents)} FIR documents from local corpus.")
    
    # 2. Get OAuth token
    print("[Auth] Fetching Zoho OAuth token...")
    token = await get_access_token()
    headers = {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type":  "application/json"
    }
    print("[Auth] Token obtained.")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 3. Get or create KB
        kb_id = await get_or_create_knowledge_base(client, headers)
        
        # 4. Delete old documents
        await delete_all_documents(client, headers, kb_id)
        
        # 5. Upload in batches
        total_batches = (len(documents) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"\n[Upload] Uploading {len(documents)} documents in {total_batches} batches of {BATCH_SIZE}...")
        
        for i in range(0, len(documents), BATCH_SIZE):
            batch = documents[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            await upload_batch(client, headers, kb_id, batch, batch_num)
            
            # Small delay between batches to avoid rate limiting
            if batch_num < total_batches:
                await asyncio.sleep(0.5)
    
    print(f"\n[DONE] Successfully uploaded {len(documents)} FIR documents to QuickML Knowledge Base '{KB_NAME}'.")
    print("       The RAG chatbot will now answer questions using the updated real FIR data.")


if __name__ == "__main__":
    asyncio.run(main())
