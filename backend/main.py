import os
import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(
    title="Project Falcon Backend API",
    description="Catalyst AppSail FastAPI backend for crime analytics, geospatial clustering, and network graph data.",
    version="1.0.0"
)

# Helper function to load ML output files
def load_ml_json(filename):
    filepath = os.path.join(os.path.dirname(__file__), '..', 'ml', 'scripts', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Project Falcon AppSail Backend",
        "version": "1.0.0"
    }

@app.get("/api/districts")
def get_districts():
    data = load_ml_json('district_stats.json')
    if data:
        return data
        
    return {
        "status": "error",
        "message": "district_stats.json not found. Run ML pipeline first."
    }

@app.get("/api/clusters")
def get_clusters(district: Optional[str] = None):
    data = load_ml_json('clusters.geojson')
    if data:
        # Note: In production we could filter `data['features']` by district
        return {
            "status": "success",
            "type": "FeatureCollection",
            "features": data['features']
        }
        
    return {
        "status": "error",
        "message": "clusters.geojson not found. Run ML pipeline first."
    }

@app.get("/api/offender/risk/{accused_id}")
def get_offender_risk(accused_id: str):
    return {
        "status": "success",
        "accused_id": accused_id,
        "risk_score": 84.5,
        "classification": "High Risk Repeat Offender",
        "factors": ["Prior Arrests: 4", "Severe Offence Code: 307", "Gang Association: Community #3"]
    }
