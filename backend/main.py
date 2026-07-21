from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI(
    title="Project Falcon Backend API",
    description="Catalyst AppSail FastAPI backend for crime analytics, geospatial clustering, and network graph data.",
    version="1.0.0"
)

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
    return {
        "status": "success",
        "districts": [
            {"id": 1, "name": "Bengaluru City", "risk": "High", "crimeCount": 3420},
            {"id": 2, "name": "Mysuru City", "risk": "Medium", "crimeCount": 1240},
            {"id": 3, "name": "Mangaluru City", "risk": "High", "crimeCount": 1890},
            {"id": 4, "name": "Hubballi-Dharwad", "risk": "Medium", "crimeCount": 980},
            {"id": 5, "name": "Belagavi", "risk": "Low", "crimeCount": 650}
        ]
    }

@app.get("/api/clusters")
def get_clusters(district: Optional[str] = None):
    return {
        "status": "success",
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [77.5946, 12.9716]},
                "properties": {"cluster_id": 1, "district": "Bengaluru City", "crime_type": "Theft", "risk_level": "High"}
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [76.6394, 12.2958]},
                "properties": {"cluster_id": 2, "district": "Mysuru City", "crime_type": "Robbery", "risk_level": "Medium"}
            }
        ]
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
