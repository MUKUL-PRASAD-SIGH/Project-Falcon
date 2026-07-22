import os
import json
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FEATURE_STORE_BASE = BASE_DIR / "data" / "feature_store"
RAW_FIRS = BASE_DIR / "data" / "scripts" / "firs_synthetic.json"
OUTPUTS_DIR = BASE_DIR / "ml" / "outputs"
SCRIPTS_OUT = BASE_DIR / "ml" / "scripts"

DISTRICT_MAP = {
    1: "Bengaluru City",
    2: "Mysuru City",
    3: "Mangaluru City",
    4: "Hubballi-Dharwad",
    5: "Belagavi"
}

def load_data():
    """Load hotspot data ensuring DistrictID is always present."""
    pointer_path = FEATURE_STORE_BASE / "latest.txt"
    if pointer_path.exists():
        latest_version = pointer_path.read_text().strip()
        hotspots_parquet = FEATURE_STORE_BASE / latest_version / "hotspot_features.parquet"
        if hotspots_parquet.exists():
            print(f"Loading preprocessed hotspot features from {hotspots_parquet}...")
            df = pd.read_parquet(hotspots_parquet)
            # If DistrictID is missing from parquet, merge it from raw data
            if 'DistrictID' not in df.columns and RAW_FIRS.exists():
                print("  DistrictID missing from parquet, merging from raw FIRs...")
                with open(RAW_FIRS, 'r') as f:
                    raw_df = pd.DataFrame(json.load(f))
                if 'DistrictID' in raw_df.columns and 'CaseMasterID' in raw_df.columns:
                    district_lookup = raw_df[['CaseMasterID', 'DistrictID']].drop_duplicates()
                    df = df.merge(district_lookup, on='CaseMasterID', how='left')
            return df
            
    print(f"Fallback loading raw FIRs for geo clustering from {RAW_FIRS}...")
    with open(RAW_FIRS, 'r') as f:
        firs_data = json.load(f)
    return pd.DataFrame(firs_data)

def build_geo_clusters():
    df = load_data()
    if df.empty:
        print("Error: DataFrame is empty.")
        return
        
    print(f"Loaded {len(df)} records for geospatial clustering.")
    
    # Map DistrictID → DistrictName
    if 'DistrictID' in df.columns:
        df['DistrictName'] = df['DistrictID'].map(lambda x: DISTRICT_MAP.get(int(x), "Karnataka"))
    else:
        df['DistrictName'] = "Karnataka"
    
    # Extract coordinates for DBSCAN
    coords = df[['latitude', 'longitude']].values
    
    # Run DBSCAN (epsilon = 5km approx, min_samples=3)
    print("Running DBSCAN for Hotspot Detection...")
    kms_per_radian = 6371.0088
    epsilon = 5.0 / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    
    labels = db.labels_
    df['cluster_label'] = labels
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"DBSCAN detected {n_clusters} spatial clusters (hotspots).")
    
    # Build GeoJSON features with per-cluster district assignment
    features = []
    cluster_points = {}
    cluster_districts = {}
    
    for i, label in enumerate(labels):
        if label == -1:
            continue  # Noise
        if label not in cluster_points:
            cluster_points[label] = []
            cluster_districts[label] = []
        cluster_points[label].append(coords[i])
        cluster_districts[label].append(df.iloc[i]['DistrictName'])
        
    # Determine risk using simple K-Means on cluster sizes
    if len(cluster_points) > 0:
        cluster_sizes = np.array([len(pts) for pts in cluster_points.values()]).reshape(-1, 1)
        
        n_risk_tiers = min(3, len(cluster_sizes))
        if n_risk_tiers >= 2:
            kmeans = KMeans(n_clusters=n_risk_tiers, random_state=42).fit(cluster_sizes)
            centers = kmeans.cluster_centers_.flatten()
            sorted_indices = np.argsort(centers)
            
            tier_names = ['Low', 'Medium', 'High'][:n_risk_tiers]
            risk_mapping = {}
            for original_label, sorted_index in enumerate(sorted_indices):
                risk_mapping[original_label] = tier_names[sorted_index]
                
            for label, pts in cluster_points.items():
                pts_array = np.array(pts)
                centroid = pts_array.mean(axis=0)
                size = len(pts)
                
                k_label = kmeans.predict([[size]])[0]
                risk = risk_mapping[k_label]
                
                # Determine dominant district of this cluster
                district_mode = pd.Series(cluster_districts[label]).mode()
                cluster_district = district_mode.iloc[0] if len(district_mode) > 0 else "Karnataka"
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(centroid[1]), float(centroid[0])]  # GeoJSON is [lon, lat]
                    },
                    "properties": {
                        "cluster_id": int(label),
                        "incident_count": size,
                        "risk_level": risk,
                        "district": cluster_district,
                        "crime_type": "Mixed"
                    }
                })
        else:
            # Only 1 cluster — assign Medium risk
            for label, pts in cluster_points.items():
                pts_array = np.array(pts)
                centroid = pts_array.mean(axis=0)
                district_mode = pd.Series(cluster_districts[label]).mode()
                cluster_district = district_mode.iloc[0] if len(district_mode) > 0 else "Karnataka"
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(centroid[1]), float(centroid[0])]
                    },
                    "properties": {
                        "cluster_id": int(label),
                        "incident_count": len(pts),
                        "risk_level": "Medium",
                        "district": cluster_district,
                        "crime_type": "Mixed"
                    }
                })
                
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Compute District Rollup Stats (district_stats.json)
    district_counts = df.groupby('DistrictName').size().to_dict()
    
    district_stats = []
    for dname in DISTRICT_MAP.values():
        cnt = district_counts.get(dname, 0)
        # Count hotspots belonging to this district
        district_hotspots = len([f for f in features
                                 if f['properties'].get('district') == dname
                                 and f['properties']['risk_level'] in ['High', 'Medium']])
        risk_tier = "High" if cnt > 250 else ("Medium" if cnt > 150 else "Low")
        district_stats.append({
            "district": dname,
            "incident_count": cnt,
            "risk_tier": risk_tier,
            "active_hotspots": district_hotspots
        })
        
    # Save outputs
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_OUT.mkdir(parents=True, exist_ok=True)
    
    for target_dir in [OUTPUTS_DIR, SCRIPTS_OUT]:
        with open(target_dir / 'clusters.geojson', 'w') as f:
            json.dump(geojson, f, indent=2)
        with open(target_dir / 'district_stats.json', 'w') as f:
            json.dump(district_stats, f, indent=2)
            
    print("Successfully generated clusters.geojson and district_stats.json")

if __name__ == "__main__":
    build_geo_clusters()

