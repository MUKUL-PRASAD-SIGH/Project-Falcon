"""
data/scripts/export_rag_chunks.py
-----------------------------------
Splits all 1000 FIR documents into uploadable .txt chunks
(≤ 450 KB each) for manual upload to the Zoho QuickML Knowledge Base.

Output: data/processed/rag_chunks/chunk_001.txt, chunk_002.txt, ...

Usage:
  python data/scripts/export_rag_chunks.py
"""

import csv
from pathlib import Path

BASE_DIR      = Path(__file__).resolve().parent.parent.parent
CSV_PATH      = BASE_DIR / "data" / "processed" / "fir_rag_documents.csv"
OUTPUT_DIR    = BASE_DIR / "data" / "processed" / "rag_chunks"
MAX_BYTES     = 450_000   # stay safely under 500 KB limit

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load all documents
docs = []
with open(CSV_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        docs.append(row["text"])

print(f"Loaded {len(docs)} FIR documents from CSV.")

# Pack into chunks
chunk_num   = 1
current     = []
current_size = 0
files_written = []

def write_chunk(chunk_num, lines):
    path = OUTPUT_DIR / f"fir_chunk_{chunk_num:03d}.txt"
    content = "\n\n---\n\n".join(lines)
    path.write_text(content, encoding="utf-8")
    size_kb = len(content.encode("utf-8")) / 1024
    print(f"  Written: {path.name}  ({len(lines)} docs, {size_kb:.1f} KB)")
    return path

for doc in docs:
    doc_bytes = len(doc.encode("utf-8")) + 10  # +10 for separator
    if current_size + doc_bytes > MAX_BYTES and current:
        files_written.append(write_chunk(chunk_num, current))
        chunk_num += 1
        current = []
        current_size = 0
    current.append(doc)
    current_size += doc_bytes

if current:
    files_written.append(write_chunk(chunk_num, current))

print(f"\nDone! Created {len(files_written)} chunk files in:")
print(f"  {OUTPUT_DIR}")
print(f"\nUpload each file to your QuickML Knowledge Base via the Catalyst Console.")
max_size_kb = max((p.stat().st_size / 1024 for p in files_written), default=0)
print(f"Max file size used: {max_size_kb:.1f} KB")
