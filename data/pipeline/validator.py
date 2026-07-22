import pandas as pd
import numpy as np

# Karnataka bounding box
KARNATAKA_BBOX = {
    "min_lat": 11.5,
    "max_lat": 18.5,
    "min_lon": 74.0,
    "max_lon": 78.5
}

def validate_firs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates FIRs DataFrame:
    1. Checks required columns.
    2. Drops rows with missing critical information.
    3. Validates GPS bounds.
    4. Validates and parses dates.
    """
    required_cols = [
        "CaseMasterID", "CrimeNo", "CrimeRegisteredDate", 
        "latitude", "longitude", "BriefFacts", "DistrictID", "CrimeHeadID"
    ]
    
    # Ensure columns exist
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in FIRs data: {missing_cols}")

    # Drop nulls in critical fields
    df_valid = df.dropna(subset=["CaseMasterID", "CrimeNo", "latitude", "longitude"]).copy()

    # GPS Validation
    lat_valid = df_valid['latitude'].between(KARNATAKA_BBOX['min_lat'], KARNATAKA_BBOX['max_lat'])
    lon_valid = df_valid['longitude'].between(KARNATAKA_BBOX['min_lon'], KARNATAKA_BBOX['max_lon'])
    df_valid = df_valid[lat_valid & lon_valid]

    # Date Parsing (ISO 8601)
    df_valid['CrimeRegisteredDate'] = pd.to_datetime(df_valid['CrimeRegisteredDate'], errors='coerce')
    df_valid = df_valid.dropna(subset=['CrimeRegisteredDate'])

    print(f"[VALIDATOR] FIRs: Validated {len(df_valid)} out of {len(df)} records.")
    return df_valid


def validate_accused(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates Accused DataFrame:
    1. Checks required columns.
    2. Drops rows with missing keys (AccusedMasterID, CaseMasterID).
    3. Handles missing AgeYear.
    """
    required_cols = [
        "AccusedMasterID", "CaseMasterID", "AccusedName", "AgeYear", "GenderID", "PersonID"
    ]
    
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in Accused data: {missing_cols}")

    # Drop nulls in critical fields
    df_valid = df.dropna(subset=["AccusedMasterID", "CaseMasterID", "AccusedName"]).copy()
    
    # Fill missing AgeYear with median or 0, here we leave it or fill with 0
    df_valid['AgeYear'] = df_valid['AgeYear'].fillna(0).astype(int)

    print(f"[VALIDATOR] Accused: Validated {len(df_valid)} out of {len(df)} records.")
    return df_valid
