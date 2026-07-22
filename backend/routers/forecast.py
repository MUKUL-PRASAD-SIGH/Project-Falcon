"""
backend/routers/forecast.py
----------------------------
SARIMA / ExponentialSmoothing crime forecast endpoint.

GET /api/forecast?district={name}
  - Returns raw JSON from ml/outputs/forecasts.json
  - Also returns chart-ready arrays (dates, actual, forecast7, upper, lower)
    compatible with ForecastChart.jsx (ECharts line series format).

District names: Bengaluru City, Mysuru City, Mangaluru City,
                Hubballi-Dharwad, Belagavi, Statewide Total
"""

import json
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pathlib import Path

from backend.middleware.cache import get_cached, set_cached

router = APIRouter(prefix="/api/forecast", tags=["Crime Forecast"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FORECAST_FILE = BASE_DIR / "ml" / "outputs" / "forecasts.json"
_FORECAST_ALT = BASE_DIR / "ml" / "scripts" / "forecasts.json"


def _load_forecasts():
    """Load forecasts from cache or disk."""
    cached = get_cached("forecasts")
    if cached is not None:
        return cached

    target = FORECAST_FILE if FORECAST_FILE.exists() else _FORECAST_ALT
    if not target.exists():
        return None

    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    set_cached("forecasts", data)
    return data


def _to_chart_format(district_data: dict) -> dict:
    """
    Transform ml/outputs/forecasts.json district entry into
    ECharts-compatible arrays for ForecastChart.jsx.

    Input format (per district):
      { district, historical: [{date, incidents}], forecast: [{date, predicted_incidents, lower_bound, upper_bound}] }

    Output format (ForecastChart props):
      { dates, actual, forecast7, upper, lower }
    """
    historical = district_data.get("historical", [])
    forecast = district_data.get("forecast", [])

    hist_dates = [h["date"] for h in historical]
    hist_vals = [h["incidents"] for h in historical]

    fc_dates = [f["date"] for f in forecast]
    fc_vals = [f["predicted_incidents"] for f in forecast]
    fc_upper = [f["upper_bound"] for f in forecast]
    fc_lower = [f["lower_bound"] for f in forecast]

    # Merge timelines: historical + forecast dates
    all_dates = hist_dates + fc_dates
    n_hist = len(hist_dates)

    # actual: historical values, then None for forecast range
    actual = hist_vals + [None] * len(fc_dates)

    # forecast7: None for historical, then forecast values
    forecast7 = [None] * n_hist + fc_vals

    # upper / lower bands: same pattern
    upper = [None] * n_hist + fc_upper
    lower = [None] * n_hist + fc_lower

    return {
        "dates": all_dates,
        "actual": actual,
        "forecast7": forecast7,
        "upper": upper,
        "lower": lower,
    }


@router.get("")
def get_crime_forecast(
    district: Optional[str] = Query(None, description="District name or 'Statewide Total'"),
    chart: bool = Query(True, description="Include ECharts-ready chart_data arrays"),
):
    """
    SARIMA + ExponentialSmoothing crime forecast.

    Returns:
      - raw historical + forecast data from ML pipeline
      - chart_data arrays (dates, actual, forecast7, upper, lower) for ForecastChart.jsx
    """
    data = _load_forecasts()
    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Forecasts file not found. Run ML pipeline first."
        )

    if district:
        if district not in data:
            available = list(data.keys())
            raise HTTPException(
                status_code=404,
                detail=f"District '{district}' not found. Available: {available}"
            )
        district_data = data[district]
        result = {
            "status": "success",
            "district": district,
            "data": district_data,
        }
        if chart:
            result["chart_data"] = _to_chart_format(district_data)
        return result

    # Return all districts
    response = {
        "status": "success",
        "all_districts": list(data.keys()),
        "data": data,
    }
    if chart:
        # Return chart-ready format for "Statewide Total" as default chart
        default_district = "Statewide Total" if "Statewide Total" in data else list(data.keys())[0]
        response["chart_data"] = _to_chart_format(data[default_district])
        response["chart_district"] = default_district
    return response
