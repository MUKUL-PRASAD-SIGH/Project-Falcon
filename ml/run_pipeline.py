import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from ml.scripts.build_features import build_feature_table
from ml.scripts.geo_clustering import build_geo_clusters
from ml.models.tfidf_similarity import build_tfidf_model
from ml.models.network_graph import build_network_model
from ml.models.sarima_forecast import build_sarima_model
from ml.models.quickml_risk_anomaly import build_quickml_models

def run_full_ml_pipeline():
    print("=" * 70)
    print(" PROJECT FALCON - PHASE 2 ML PIPELINE RUNNER")
    print("=" * 70)
    
    print("\n[Step 1/6] Building Denormalized Accused Feature Table...")
    build_feature_table()
    
    print("\n[Step 2/6] Running DBSCAN & K-Means Geospatial Crime Clustering...")
    build_geo_clusters()
    
    print("\n[Step 3/6] Fitting TF-IDF Case Similarity Model...")
    build_tfidf_model()
    
    print("\n[Step 4/6] Building NetworkX & Louvain Criminal Community Graph...")
    build_network_model()
    
    print("\n[Step 5/6] Fitting SARIMA Crime Forecasting Engine...")
    build_sarima_model()
    
    print("\n[Step 6/6] Executing QuickML Risk Scoring & Anomaly Detection Engine...")
    build_quickml_models()
    
    print("\n" + "=" * 70)
    print(" ALL ML PIPELINE TASKS COMPLETED SUCCESSFULLY!")
    print(" Output artifacts generated in ml/outputs/ and ml/scripts/")
    print("=" * 70)

if __name__ == "__main__":
    run_full_ml_pipeline()
