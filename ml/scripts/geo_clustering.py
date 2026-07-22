import os
import json
import argparse
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
import numpy as np

# Load preprocessed hotspots from Feature Store
FEATURE_STORE_BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'feature_store')
with open(os.path.join(FEATURE_STORE_BASE, 'latest.txt'), 'r') as f:
    latest_version = f.read().strip()
store_dir = os.path.join(FEATURE_STORE_BASE, latest_version)

HOTSPOTS_PARQUET = os.path.join(store_dir, 'hotspot_features.parquet')
CLUSTER_GEOJSON = os.path.join(os.path.dirname(__file__), 'clusters.geojson')
DISTRICTS_JSON = os.path.join(os.path.dirname(__file__), 'districts_rollup.json')

def load_data():
    print(f"Loading preprocessed hotspot features from {HOTSPOTS_PARQUET}...")
    df = pd.read_parquet(HOTSPOTS_PARQUET)
    return df

def build_geo_clusters():
    df = load_data()
    if df.empty:
        print("Error: DataFrame is empty.")
        return
        
    print(f"Loaded {len(df)} records for geospatial clustering.")
    
    # Extract coordinates for DBSCAN
    coords = df[['latitude', 'longitude']].values
    
    # Run DBSCAN (epsilon = 5km approx, min_samples=3)
    print("Running DBSCAN for Hotspot Detection...")
    # Convert km to radians for haversine (epsilon = 5.0km)
    kms_per_radian = 6371.0088
    epsilon = 5.0 / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    
    labels = db.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"DBSCAN detected {n_clusters} spatial clusters (hotspots).")
    
    # Build GeoJSON features
    features = []
    cluster_points = {}
    
    for i, label in enumerate(labels):
        if label == -1:
            continue # Noise
            
        if label not in cluster_points:
            cluster_points[label] = []
            
        cluster_points[label].append(coords[i])
        
    # Determine risk using simple K-Means on cluster sizes
    if len(cluster_points) > 0:
        cluster_sizes = np.array([len(pts) for pts in cluster_points.values()]).reshape(-1, 1)
        
        if len(cluster_sizes) >= 3:
            kmeans = KMeans(n_clusters=3, random_state=42).fit(cluster_sizes)
            # Sort centers to map to Low, Medium, High
            centers = kmeans.cluster_centers_.flatten()
            sorted_indices = np.argsort(centers)
            
            # Map original kmeans label to risk tier
            risk_mapping = {}
            for original_label, sorted_index in enumerate(sorted_indices):
                if sorted_index == 0: risk_mapping[original_label] = 'Low'
                elif sorted_index == 1: risk_mapping[original_label] = 'Medium'
                else: risk_mapping[original_label] = 'High'
                
            for label, pts in cluster_points.items():
                pts_array = np.array(pts)
                centroid = pts_array.mean(axis=0)
                size = len(pts)
                
                k_label = kmeans.predict([[size]])[0]
                risk = risk_mapping[k_label]
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [centroid[1], centroid[0]] # GeoJSON is [lon, lat]
                    },
                    "properties": {
                        "cluster_id": int(label),
                        "incident_count": size,
                        "risk_level": risk,
                        "crime_type": "Mixed" # Simplified for demo
                    }
                })
                
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Save outputs
    out_dir = os.path.dirname(__file__)
    
    with open(os.path.join(out_dir, 'clusters.geojson'), 'w') as f:
        json.dump(geojson, f, indent=2)
        
    print("Successfully generated clusters.geojson")

if __name__ == "__main__":
    build_geo_clusters()
