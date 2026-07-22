import os
import json
import argparse
import numpy as np
from sklearn.cluster import DBSCAN, KMeans

def load_firs(is_real=False):
    if is_real:
        print("Clustering using REAL DataStore / CSV data...")
        # Placeholder for real data
        return []
    else:
        print("Clustering using DEMO synthetic data...")
        firs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'scripts', 'firs_synthetic.json')
        
        if not os.path.exists(firs_path):
            print(f"Error: Could not find synthetic data at {firs_path}")
            return []
            
        with open(firs_path, 'r') as f:
            return json.load(f)

def build_geo_clusters(is_real=False):
    firs = load_firs(is_real)
    if not firs:
        return
        
    print(f"Loaded {len(firs)} FIRs for geospatial clustering.")
    
    # Extract coordinates for DBSCAN
    coords = []
    for fir in firs:
        coords.append([fir['latitude'], fir['longitude']])
        
    coords = np.array(coords)
    
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
    cluster_counts = {}
    
    # We will compute centroids for the clusters to output fewer points
    cluster_points = {}
    
    for i, label in enumerate(labels):
        if label == -1:
            continue # Noise
            
        if label not in cluster_points:
            cluster_points[label] = []
            
        cluster_points[label].append(coords[i])
        
    # Determine risk using simple K-Means on cluster sizes
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
    
    # Generate district rollups
    # DISTRICTS mapping based on generate_synthetic.py
    districts_map = {
        1: "Bengaluru City",
        2: "Mysuru City",
        3: "Mangaluru City",
        4: "Hubballi-Dharwad",
        5: "Belagavi"
    }
    
    crime_heads_map = {
        1: "Theft",
        2: "Robbery",
        3: "Assault",
        4: "Cybercrime",
        5: "Fraud",
        6: "Narcotics",
        7: "Homicide"
    }
    
    district_counts = {did: 0 for did in districts_map.keys()}
    district_crime_groups = {did: {name: 0 for name in crime_heads_map.values()} for did in districts_map.keys()}
    
    for fir in firs:
        did = fir['DistrictID']
        cid = fir['CrimeHeadID']
        district_counts[did] += 1
        c_name = crime_heads_map.get(cid, "Unknown")
        if c_name in district_crime_groups[did]:
            district_crime_groups[did][c_name] += 1
        
    districts_list = []
    for did, count in district_counts.items():
        # Simple risk logic for district
        risk = "Low"
        if count > 300: risk = "High"
        elif count > 150: risk = "Medium"
        
        districts_list.append({
            "id": did,
            "name": districts_map[did],
            "crimeCount": count,
            "risk": risk,
            "crimeGroups": district_crime_groups[did]
        })
        
    districts_output = {
        "status": "success",
        "districts": districts_list
    }
    
    # Save outputs
    out_dir = os.path.dirname(__file__)
    
    with open(os.path.join(out_dir, 'clusters.geojson'), 'w') as f:
        json.dump(geojson, f, indent=2)
        
    with open(os.path.join(out_dir, 'district_stats.json'), 'w') as f:
        json.dump(districts_output, f, indent=2)
        
    print("Successfully generated clusters.geojson and district_stats.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Geo Clusters using DBSCAN")
    parser.add_argument('--real', action='store_true', help="Use real DataStore data")
    args = parser.parse_args()
    build_geo_clusters(args.real)
