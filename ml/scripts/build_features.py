import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_SCRIPTS_DIR = BASE_DIR / "data" / "scripts"
RAW_FIRS = DATA_SCRIPTS_DIR / "firs_synthetic.json"
RAW_ACCUSED = DATA_SCRIPTS_DIR / "accused_synthetic.json"

PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUTS_DIR = BASE_DIR / "ml" / "outputs"
FEATURE_STORE_BASE = BASE_DIR / "data" / "feature_store"

# Mappings
CRIME_HEAD_MAP = {
    1: {"name": "Theft", "severity": 1},
    2: {"name": "Robbery", "severity": 4},
    3: {"name": "Assault", "severity": 3},
    4: {"name": "Cybercrime", "severity": 3},
    5: {"name": "Fraud", "severity": 2},
    6: {"name": "Narcotics", "severity": 4},
    7: {"name": "Homicide", "severity": 5}
}

DISTRICT_MAP = {
    1: "Bengaluru City",
    2: "Mysuru City",
    3: "Mangaluru City",
    4: "Hubballi-Dharwad",
    5: "Belagavi"
}

def load_data():
    """Loads raw FIR and Accused JSON files."""
    print("Loading FIRs and Accused raw datasets...")
    with open(RAW_FIRS, 'r') as f:
        firs_data = json.load(f)
    with open(RAW_ACCUSED, 'r') as f:
        accused_data = json.load(f)
        
    firs_df = pd.DataFrame(firs_data)
    accused_df = pd.DataFrame(accused_data)
    return firs_df, accused_df

def build_feature_table():
    """Builds denormalized accused feature table for QuickML and risk scoring."""
    firs_df, accused_df = load_data()
    
    print(f"Loaded {len(firs_df)} FIRs and {len(accused_df)} Accused records.")
    
    # Map CrimeHead details to FIRs
    firs_df['CrimeHeadName'] = firs_df['CrimeHeadID'].map(lambda x: CRIME_HEAD_MAP.get(x, {}).get("name", "Unknown"))
    firs_df['CrimeSeverity'] = firs_df['CrimeHeadID'].map(lambda x: CRIME_HEAD_MAP.get(x, {}).get("severity", 1))
    firs_df['DistrictName'] = firs_df['DistrictID'].map(lambda x: DISTRICT_MAP.get(x, "Karnataka"))
    firs_df['CrimeRegisteredDate'] = pd.to_datetime(firs_df['CrimeRegisteredDate'])
    
    # Calculate co-accused per FIR
    fir_co_accused = accused_df.groupby('CaseMasterID').size().to_dict()
    firs_df['FIR_AccusedCount'] = firs_df['CaseMasterID'].map(lambda x: fir_co_accused.get(x, 1))
    
    # Merge Accused with FIR details
    merged = pd.merge(accused_df, firs_df, on='CaseMasterID', how='inner')
    
    # Reference date for recency calculation (max registered date or now)
    ref_date = merged['CrimeRegisteredDate'].max()
    
    # Group by Accused Person/Name to aggregate repeat history
    features = []
    
    # Grouping by AccusedName to consolidate repeat offender records across cases
    for accused_name, group in merged.groupby('AccusedName'):
        accused_master_id = int(group['AccusedMasterID'].iloc[0])
        person_id = group['PersonID'].iloc[0]
        age = int(group['AgeYear'].mean())
        gender = int(group['GenderID'].iloc[0])
        
        offense_count = len(group)
        avg_severity = round(group['CrimeSeverity'].mean(), 2)
        max_severity = int(group['CrimeSeverity'].max())
        
        latest_crime_date = group['CrimeRegisteredDate'].max()
        recency_days = max(0, (ref_date - latest_crime_date).days)
        
        # Mode district and crime head
        district = group['DistrictName'].mode().iloc[0] if not group['DistrictName'].empty else "Bengaluru City"
        crime_head = group['CrimeHeadName'].mode().iloc[0] if not group['CrimeHeadName'].empty else "Theft"
        
        # Co-accused total across FIRs (subtract 1 for self)
        co_accused_sum = max(0, group['FIR_AccusedCount'].sum() - offense_count)
        
        # Prior arrests (derived from offense count + historical multiplier)
        prior_arrests = offense_count if offense_count > 1 else (1 if np.random.rand() > 0.7 else 0)
        
        # Target variable: Repeat Offender (1 if >1 offenses, else 0)
        is_repeat = 1 if offense_count > 1 else 0
        
        # Calculate heuristic baseline Risk Score (0 - 100)
        # Severity weight: 30%, Offense count weight: 35%, Recency weight: 20%, Co-accused weight: 15%
        severity_factor = (max_severity / 5.0) * 30.0
        offense_factor = min(35.0, (offense_count / 4.0) * 35.0)
        recency_factor = max(0.0, 20.0 * (1.0 - (recency_days / 365.0)))
        co_accused_factor = min(15.0, (co_accused_sum / 5.0) * 15.0)
        
        raw_risk = severity_factor + offense_factor + recency_factor + co_accused_factor
        risk_score = round(min(100.0, max(5.0, raw_risk)), 1)
        
        features.append({
            "AccusedMasterID": accused_master_id,
            "PersonID": person_id,
            "AccusedName": accused_name,
            "AgeYear": age,
            "GenderID": gender,
            "prior_offense_count": offense_count,
            "avg_crime_severity": avg_severity,
            "max_crime_severity": max_severity,
            "recency_days": recency_days,
            "district": district,
            "crime_head": crime_head,
            "co_accused_count": co_accused_sum,
            "prior_arrest_count": prior_arrests,
            "is_repeat_offender": is_repeat,
            "risk_score": risk_score
        })
        
    df_features = pd.DataFrame(features)
    
    # Create directories if needed
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    csv_path_processed = PROCESSED_DIR / "accused_features.csv"
    csv_path_outputs = OUTPUTS_DIR / "accused_features.csv"
    
    df_features.to_csv(csv_path_processed, index=False)
    df_features.to_csv(csv_path_outputs, index=False)
    
    # Save to feature store if latest version exists
    pointer_path = FEATURE_STORE_BASE / "latest.txt"
    if pointer_path.exists():
        latest_ver = pointer_path.read_text().strip()
        ver_dir = FEATURE_STORE_BASE / latest_ver
        df_features.to_parquet(ver_dir / "accused_features.parquet")
        print(f"Saved parquet to feature store: {ver_dir / 'accused_features.parquet'}")
        
    print(f"\n[BUILD_FEATURES DONE]")
    print(f"  Total unique accused profiles: {len(df_features)}")
    print(f"  Repeat offenders count: {df_features['is_repeat_offender'].sum()}")
    print(f"  Saved CSV to: {csv_path_processed}")
    print(f"  Saved CSV to: {csv_path_outputs}")
    
    return df_features

if __name__ == "__main__":
    build_feature_table()
