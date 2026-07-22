import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Pipeline Modules
from data.pipeline.validator import validate_firs, validate_accused
from data.pipeline.clean_text import clean_brief_facts
from data.pipeline.prepare_hotspots import extract_hotspot_features
from data.pipeline.prepare_forecast import extract_forecast_series
from data.pipeline.prepare_graph import extract_graph_features

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
RAW_FIRS = DATA_DIR / "scripts" / "firs_synthetic.json"
RAW_ACCUSED = DATA_DIR / "scripts" / "accused_synthetic.json"
FEATURE_STORE_BASE = DATA_DIR / "feature_store"

def load_raw_data():
    """Loads raw JSON datasets into DataFrames."""
    print("Loading raw data...")
    with open(RAW_FIRS, 'r') as f:
        firs_df = pd.DataFrame(json.load(f))
    with open(RAW_ACCUSED, 'r') as f:
        accused_df = pd.DataFrame(json.load(f))
    return firs_df, accused_df

def run_pipeline():
    """
    Orchestrates the data pipeline:
    1. Ingestion
    2. Validation
    3. Preprocessing (Cleaning & Feature Extraction)
    4. Feature Store (Save to Parquet)
    """
    start_time = datetime.now()
    version_id = start_time.strftime("v%Y%m%d_%H%M%S")
    store_dir = FEATURE_STORE_BASE / version_id
    store_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Feature Store Pipeline Run: {version_id}")
    print(f"{'='*60}")

    # 1. Ingestion
    raw_firs, raw_accused = load_raw_data()
    
    # 2. Validation
    valid_firs = validate_firs(raw_firs)
    valid_accused = validate_accused(raw_accused)
    
    # Save valid operational records for DataStore ingestion
    valid_firs.to_parquet(store_dir / "operational_casemaster.parquet")
    valid_accused.to_parquet(store_dir / "operational_accused.parquet")
    
    # 3. Preprocessing & Feature Extraction
    
    # TF-IDF Features
    firs_clean_text = clean_brief_facts(valid_firs)
    firs_clean_text[['CaseMasterID', 'BriefFacts_Cleaned']].to_parquet(store_dir / "tfidf_features.parquet")
    
    # Hotspot Features
    hotspots = extract_hotspot_features(valid_firs)
    hotspots.to_parquet(store_dir / "hotspot_features.parquet")
    
    # Forecast Features
    forecast = extract_forecast_series(valid_firs, freq='W')
    forecast.to_parquet(store_dir / "forecast_features.parquet")
    
    # Graph Features
    nodes, edges = extract_graph_features(valid_firs, valid_accused)
    nodes.to_parquet(store_dir / "graph_nodes.parquet")
    edges.to_parquet(store_dir / "graph_edges.parquet")
    
    # Write latest symlink or pointer
    pointer_path = FEATURE_STORE_BASE / "latest.txt"
    with open(pointer_path, 'w') as f:
        f.write(version_id)
        
    print(f"\n[PIPELINE DONE] All features saved to {store_dir}")
    print(f"  Operational tables: 2")
    print(f"  ML Feature tables:  5")
    print(f"{'='*60}\n")
    
if __name__ == "__main__":
    run_pipeline()
