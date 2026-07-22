import os
import json
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pathlib import Path

router = APIRouter(prefix="/api/cases", tags=["Case Similarity"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SIMILARITY_FILE = BASE_DIR / "ml" / "outputs" / "similarity_index.json"

@router.get("/similar")
def get_similar_cases(case_id: int = Query(..., description="CaseMasterID to find similar FIRs for")):
    if not SIMILARITY_FILE.exists():
        # Fallback script path
        SIMILARITY_FILE_ALT = BASE_DIR / "ml" / "scripts" / "similarity_index.json"
        if not SIMILARITY_FILE_ALT.exists():
            raise HTTPException(status_code=404, detail="Similarity index not generated. Run ML pipeline first.")
        with open(SIMILARITY_FILE_ALT, 'r') as f:
            index_data = json.load(f)
    else:
        with open(SIMILARITY_FILE, 'r') as f:
            index_data = json.load(f)
            
    case_key = str(case_id)
    if case_key in index_data:
        return {
            "status": "success",
            "target_case_id": case_id,
            "similar_cases": index_data[case_key]
        }
        
    # Dynamically compute if not pre-indexed
    try:
        from ml.models.tfidf_similarity import TFIDFCaseSimilarity
        engine = TFIDFCaseSimilarity()
        results = engine.get_similar_cases(case_id, top_n=5)
        return {
            "status": "success",
            "target_case_id": case_id,
            "similar_cases": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate similarity: {str(e)}")
