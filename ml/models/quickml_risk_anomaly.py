import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_SCRIPTS_DIR = BASE_DIR / "data" / "scripts"
RAW_FIRS = DATA_SCRIPTS_DIR / "firs_synthetic.json"
PROCESSED_CSV = BASE_DIR / "data" / "processed" / "accused_features.csv"

OUTPUTS_DIR = BASE_DIR / "ml" / "outputs"
SCRIPTS_OUT = BASE_DIR / "ml" / "scripts"

class QuickMLRiskAndAnomalyEngine:
    def __init__(self):
        self.risk_scores = {}
        self.anomalies = []

    def process_offender_risk(self):
        print("Processing QuickML Repeat Offender Risk Scores...")
        if not PROCESSED_CSV.exists():
            from ml.scripts.build_features import build_feature_table
            features_df = build_feature_table()
        else:
            features_df = pd.read_csv(PROCESSED_CSV)
            
        for _, row in features_df.iterrows():
            aid = int(row['AccusedMasterID'])
            name = str(row['AccusedName'])
            score = float(row['risk_score'])
            
            # Tier classification
            if score >= 70.0:
                classification = "High Risk Repeat Offender"
            elif score >= 40.0:
                classification = "Medium Risk Offender"
            else:
                classification = "Low Risk Offender"
                
            # Key risk factors list
            factors = []
            if int(row['prior_offense_count']) > 1:
                factors.append(f"Prior Offenses: {row['prior_offense_count']}")
            if int(row['prior_arrest_count']) > 0:
                factors.append(f"Prior Arrests: {row['prior_arrest_count']}")
            if int(row['max_crime_severity']) >= 4:
                factors.append(f"Severe Offence Code: {row['crime_head']}")
            if int(row['co_accused_count']) > 0:
                factors.append(f"Co-accused Association: {row['co_accused_count']} associates")
            if int(row['recency_days']) < 60:
                factors.append(f"Recent Activity: {row['recency_days']} days ago")
                
            if not factors:
                factors.append("First-time Record")
                
            self.risk_scores[str(aid)] = {
                "accused_id": aid,
                "accused_name": name,
                "person_id": str(row.get('PersonID', f"A{aid}")),
                "risk_score": score,
                "classification": classification,
                "district": str(row['district']),
                "crime_head": str(row['crime_head']),
                "prior_offense_count": int(row['prior_offense_count']),
                "factors": factors
            }
            
        print(f"Computed risk scores for {len(self.risk_scores)} accused profiles.")

    def process_fir_anomalies(self):
        print("Processing QuickML FIR Anomaly Detection...")
        with open(RAW_FIRS, 'r') as f:
            firs_data = json.load(f)
            
        firs_df = pd.DataFrame(firs_data)
        firs_df['CrimeRegisteredDate'] = pd.to_datetime(firs_df['CrimeRegisteredDate'])
        firs_df['hour'] = firs_df['CrimeRegisteredDate'].dt.hour
        
        # Flag night time / temporal outliers & rare crime heads
        anomalies_list = []
        for _, row in firs_df.iterrows():
            case_id = int(row['CaseMasterID'])
            hour = int(row['hour'])
            crime_head_id = int(row['CrimeHeadID'])
            
            # Anomaly scoring logic (late night + severe crime = high anomaly score)
            score = 0.1
            reasons = []
            
            if hour in [1, 2, 3, 4]:
                score += 0.4
                reasons.append(f"Temporal Anomaly: Crime registered at {hour}:00 AM")
            if crime_head_id in [6, 7]: # Narcotics, Homicide
                score += 0.35
                reasons.append(f"High Severity Anomaly: CrimeHead ID {crime_head_id}")
            if len(str(row['BriefFacts'])) < 40:
                score += 0.15
                reasons.append("Data Anomaly: Extremely brief FIR description")
                
            score = round(min(0.99, score), 2)
            
            if score >= 0.6:
                anomalies_list.append({
                    "CaseMasterID": case_id,
                    "CrimeNo": str(row['CrimeNo']),
                    "anomaly_score": score,
                    "is_anomaly": True,
                    "registered_date": str(row['CrimeRegisteredDate']),
                    "district_id": int(row['DistrictID']),
                    "reasons": reasons
                })
                
        # Sort by highest anomaly score
        self.anomalies = sorted(anomalies_list, key=lambda x: x['anomaly_score'], reverse=True)
        print(f"Flagged {len(self.anomalies)} FIR anomalies out of {len(firs_df)} total records.")

    def export_all(self):
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SCRIPTS_OUT.mkdir(parents=True, exist_ok=True)
        
        # Export risk scores
        with open(OUTPUTS_DIR / "offender_risk_scores.json", 'w') as f:
            json.dump(self.risk_scores, f, indent=2)
        with open(SCRIPTS_OUT / "offender_risk_scores.json", 'w') as f:
            json.dump(self.risk_scores, f, indent=2)
            
        # Export anomalies
        with open(OUTPUTS_DIR / "fir_anomalies.json", 'w') as f:
            json.dump(self.anomalies, f, indent=2)
        with open(SCRIPTS_OUT / "fir_anomalies.json", 'w') as f:
            json.dump(self.anomalies, f, indent=2)
            
        print("Exported offender_risk_scores.json and fir_anomalies.json successfully.")

def build_quickml_models():
    engine = QuickMLRiskAndAnomalyEngine()
    engine.process_offender_risk()
    engine.process_fir_anomalies()
    engine.export_all()
    print("\n[QUICKML RISK & ANOMALY ENGINE DONE]")
    return engine

if __name__ == "__main__":
    build_quickml_models()
