"""
Generates an official-style Karnataka districts GeoJSON using
approximate polygon boundaries for the 30 districts (WGS84).
Source coordinates are derived from known centroid data + approximate bounding polygons.
Suitable for demo/prototype use with Leaflet / Mapbox.
"""
import json
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "karnataka_districts.geojson"

DISTRICTS = [
    {"name": "Bagalkot",        "lat": 16.18, "lon": 75.70, "d": 0.65},
    {"name": "Ballari",         "lat": 15.15, "lon": 76.94, "d": 0.65},
    {"name": "Belagavi",        "lat": 15.85, "lon": 74.50, "d": 0.80},
    {"name": "Bengaluru Rural", "lat": 13.22, "lon": 77.57, "d": 0.45},
    {"name": "Bengaluru Urban", "lat": 12.97, "lon": 77.59, "d": 0.30},
    {"name": "Bidar",           "lat": 17.92, "lon": 77.52, "d": 0.55},
    {"name": "Chamarajanagar",  "lat": 11.92, "lon": 76.94, "d": 0.55},
    {"name": "Chikkaballapura", "lat": 13.43, "lon": 77.73, "d": 0.50},
    {"name": "Chikkamagaluru",  "lat": 13.32, "lon": 75.78, "d": 0.65},
    {"name": "Chitradurga",     "lat": 14.23, "lon": 76.40, "d": 0.70},
    {"name": "Dakshina Kannada","lat": 12.86, "lon": 75.35, "d": 0.55},
    {"name": "Davanagere",      "lat": 14.47, "lon": 75.92, "d": 0.60},
    {"name": "Dharwad",         "lat": 15.46, "lon": 75.02, "d": 0.45},
    {"name": "Gadag",           "lat": 15.43, "lon": 75.63, "d": 0.50},
    {"name": "Hassan",          "lat": 13.00, "lon": 76.10, "d": 0.65},
    {"name": "Haveri",          "lat": 14.80, "lon": 75.40, "d": 0.55},
    {"name": "Kalaburagi",      "lat": 17.33, "lon": 76.82, "d": 0.80},
    {"name": "Kodagu",          "lat": 12.42, "lon": 75.74, "d": 0.60},
    {"name": "Kolar",           "lat": 13.14, "lon": 78.13, "d": 0.50},
    {"name": "Koppal",          "lat": 15.35, "lon": 76.15, "d": 0.55},
    {"name": "Mandya",          "lat": 12.52, "lon": 76.90, "d": 0.55},
    {"name": "Mysuru",          "lat": 12.30, "lon": 76.65, "d": 0.70},
    {"name": "Raichur",         "lat": 16.20, "lon": 77.36, "d": 0.75},
    {"name": "Ramanagara",      "lat": 12.72, "lon": 77.28, "d": 0.45},
    {"name": "Shivamogga",      "lat": 13.93, "lon": 75.57, "d": 0.70},
    {"name": "Tumakuru",        "lat": 13.34, "lon": 77.10, "d": 0.70},
    {"name": "Udupi",           "lat": 13.34, "lon": 74.75, "d": 0.40},
    {"name": "Uttara Kannada",  "lat": 14.80, "lon": 74.70, "d": 0.80},
    {"name": "Vijayapura",      "lat": 16.83, "lon": 75.72, "d": 0.75},
    {"name": "Yadgir",          "lat": 16.77, "lon": 77.14, "d": 0.55},
]

def make_box(lat, lon, d):
    """Create an approximate bounding rectangle polygon around a centroid."""
    return [
        [lon - d, lat - d],
        [lon + d, lat - d],
        [lon + d, lat + d],
        [lon - d, lat + d],
        [lon - d, lat - d],
    ]

features = []
for i, dist in enumerate(DISTRICTS):
    features.append({
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [make_box(dist["lat"], dist["lon"], dist["d"])]
        },
        "properties": {
            "district_id": i + 1,
            "district": dist["name"],
            "state": "Karnataka",
        }
    })

geojson = {
    "type": "FeatureCollection",
    "name": "Karnataka Districts",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
    "features": features
}

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w") as f:
    json.dump(geojson, f, indent=2)

print(f"Saved karnataka_districts.geojson with {len(features)} districts to {OUTPUT_PATH}")
