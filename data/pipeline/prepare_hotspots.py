import pandas as pd
import numpy as np

def extract_hotspot_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts features for DBSCAN clustering.
    - Requires valid latitude and longitude
    - Selects relevant columns
    - Drops NaNs
    """
    required_cols = ['CaseMasterID', 'latitude', 'longitude', 'CrimeHeadID']
    
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for hotspot features: {missing}")
        
    df_hotspots = df[required_cols].copy()
    
    # Ensure they are numeric
    df_hotspots['latitude'] = pd.to_numeric(df_hotspots['latitude'], errors='coerce')
    df_hotspots['longitude'] = pd.to_numeric(df_hotspots['longitude'], errors='coerce')
    
    # Drop rows with NaN coordinates
    df_hotspots = df_hotspots.dropna(subset=['latitude', 'longitude'])
    
    print(f"[PREPARE_HOTSPOTS] Extracted {len(df_hotspots)} rows for spatial clustering.")
    return df_hotspots
