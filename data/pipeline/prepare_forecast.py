import pandas as pd

def extract_forecast_series(df: pd.DataFrame, freq='W') -> pd.DataFrame:
    """
    Extracts time-series features for SARIMA forecasting.
    - Aggregates by District and CrimeHead.
    - Resamples to given frequency (default Weekly).
    """
    required_cols = ['CrimeRegisteredDate', 'DistrictID', 'CrimeHeadID']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns for forecast features: {missing}")

    df_ts = df[required_cols].copy()
    df_ts['CrimeRegisteredDate'] = pd.to_datetime(df_ts['CrimeRegisteredDate'])
    
    # Set date as index
    df_ts = df_ts.set_index('CrimeRegisteredDate')
    
    # Create a count column
    df_ts['CrimeCount'] = 1
    
    # Group by District and CrimeHead, then resample
    # To do this efficiently in pandas:
    # 1. groupby District and CrimeHead
    # 2. resample
    # 3. sum the count
    
    # Reset index to do groupby on DistrictID, CrimeHeadID, and a Grouper for freq
    df_ts = df_ts.reset_index()
    
    aggregated = df_ts.groupby([
        'DistrictID', 
        'CrimeHeadID', 
        pd.Grouper(key='CrimeRegisteredDate', freq=freq)
    ])['CrimeCount'].sum().reset_index()

    print(f"[PREPARE_FORECAST] Generated {len(aggregated)} time-series data points at frequency '{freq}'.")
    return aggregated
