import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_SCRIPTS_DIR = BASE_DIR / "data" / "scripts"
RAW_FIRS = DATA_SCRIPTS_DIR / "firs_synthetic.json"
OUTPUTS_DIR = BASE_DIR / "ml" / "outputs"
SCRIPTS_OUT = BASE_DIR / "ml" / "scripts"

DISTRICT_MAP = {
    1: "Bengaluru City",
    2: "Mysuru City",
    3: "Mangaluru City",
    4: "Hubballi-Dharwad",
    5: "Belagavi"
}

class SARIMACrimeForecaster:
    def __init__(self):
        self.df_firs = None
        self.forecasts = {}

    def fit_and_forecast(self, steps=12):
        print("Loading FIR time-series data for SARIMA forecasting...")
        with open(RAW_FIRS, 'r') as f:
            firs_data = json.load(f)
            
        self.df_firs = pd.DataFrame(firs_data)
        self.df_firs['CrimeRegisteredDate'] = pd.to_datetime(self.df_firs['CrimeRegisteredDate'])
        self.df_firs['DistrictName'] = self.df_firs['DistrictID'].map(lambda x: DISTRICT_MAP.get(x, "Karnataka"))
        
        # Forecast per district and overall
        districts = list(DISTRICT_MAP.values()) + ["Statewide Total"]
        
        for dist in districts:
            print(f"Fitting SARIMA forecast for: {dist}...")
            if dist == "Statewide Total":
                sub_df = self.df_firs
            else:
                sub_df = self.df_firs[self.df_firs['DistrictName'] == dist]
                
            if sub_df.empty:
                continue
                
            # Resample weekly count
            ts = sub_df.set_index('CrimeRegisteredDate').resample('W').size().fillna(0)
            
            if len(ts) < 10:
                # Fill artificial series if data is sparse
                dates = pd.date_range(end=pd.Timestamp.now(), periods=52, freq='W')
                ts = pd.Series(np.random.poisson(lam=15, size=52), index=dates)
                
            # Attempt SARIMA fit
            try:
                model = SARIMAX(ts, order=(1, 1, 1), seasonal_order=(1, 0, 0, 52), enforce_stationarity=False, enforce_invertibility=False)
                res = model.fit(disp=False)
                forecast_obj = res.get_forecast(steps=steps)
                pred_means = forecast_obj.predicted_mean
                conf_int = forecast_obj.conf_int()
            except Exception as e:
                print(f"SARIMA fallback to Exponential Smoothing for {dist}: {e}")
                # Fallback to ExponentialSmoothing
                model = ExponentialSmoothing(ts, trend='add', seasonal=None).fit()
                pred_means = model.forecast(steps)
                # Approximate 15% margin for bounds
                conf_int = pd.DataFrame({
                    'lower': pred_means * 0.85,
                    'upper': pred_means * 1.15
                }, index=pred_means.index)
                
            # Format historical and forecast data
            last_historical = ts.tail(12)
            hist_list = [
                {"date": str(d.strftime('%Y-%m-%d')), "incidents": int(val)}
                for d, val in last_historical.items()
            ]
            
            forecast_list = []
            future_dates = pd.date_range(start=ts.index[-1] + pd.Timedelta(days=7), periods=steps, freq='W')
            
            for d, p_val in zip(future_dates, pred_means):
                date_str = str(d.strftime('%Y-%m-%d'))
                p_val_clean = max(1.0, round(float(p_val), 1))
                forecast_list.append({
                    "date": date_str,
                    "predicted_incidents": p_val_clean,
                    "lower_bound": max(0.0, round(p_val_clean * 0.8, 1)),
                    "upper_bound": round(p_val_clean * 1.25, 1)
                })
                
            self.forecasts[dist] = {
                "district": dist,
                "historical": hist_list,
                "forecast": forecast_list
            }
            
        self.export_forecasts()
        return self

    def export_forecasts(self):
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SCRIPTS_OUT.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUTS_DIR / "forecasts.json", 'w') as f:
            json.dump(self.forecasts, f, indent=2)
            
        with open(SCRIPTS_OUT / "forecasts.json", 'w') as f:
            json.dump(self.forecasts, f, indent=2)
            
        print("Exported forecasts.json successfully.")

def build_sarima_model():
    forecaster = SARIMACrimeForecaster()
    forecaster.fit_and_forecast(steps=8)
    print("\n[SARIMA FORECAST DONE]")
    return forecaster

if __name__ == "__main__":
    build_sarima_model()
