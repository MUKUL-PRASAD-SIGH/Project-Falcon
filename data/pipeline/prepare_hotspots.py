import pandas as pd
import numpy as np

def extract_hotspot_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts features for DBSCAN clustering.
    - Requires valid latitude and longitude
    - Selects relevant columns
    - Drops NaNs
    """
    required_cols = ['CaseMasterID', 'latitude', 'longitude', 'CrimeHeadID', 'DistrictID']
    
    # Only require columns that exist; DistrictID may be absent in legacy data
    available_cols = [c for c in required_cols if c in df.columns]
    missing_critical = [c for c in ['CaseMasterID', 'latitude', 'longitude'] if c not in df.columns]
    if missing_critical:
        raise ValueError(f"Missing critical columns for hotspot features: {missing_critical}")
        
    df_hotspots = df[available_cols].copy()
    
    # Ensure they are numeric
    df_hotspots['latitude'] = pd.to_numeric(df_hotspots['latitude'], errors='coerce')
    df_hotspots['longitude'] = pd.to_numeric(df_hotspots['longitude'], errors='coerce')
    
    # Drop rows with NaN coordinates
    df_hotspots = df_hotspots.dropna(subset=['latitude', 'longitude'])
    
    print(f"[PREPARE_HOTSPOTS] Extracted {len(df_hotspots)} rows for spatial clustering.")
    return df_hotspots

