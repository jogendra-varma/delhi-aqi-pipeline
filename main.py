import os
import sys
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

def extract_live_api_data():
    """Fetches real historical and daily air quality metrics for Delhi via Open-Meteo."""
    # Fetch data for yesterday to ensure full 24-hour reading sets are finalized in the archive
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "start_date": yesterday,
        "end_date": yesterday,
        "hourly": "pm2_5,temperature_2m,wind_speed_10m",
        "timezone": "Asia/Kolkata"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"API Extraction Failed with status code: {response.status_code}")
        sys.exit(1)
        
    data = response.json()
    hourly_data = data["hourly"]
    
    # Create DataFrame from raw hourly API streams
    df_hourly = pd.DataFrame({
        "timestamp": pd.to_datetime(hourly_data["time"]),
        "pm25": hourly_data["pm2_5"],
        "temp": hourly_data["temperature_2m"],
        "wind": hourly_data["wind_speed_10m"]
    })
    
    # Aggregate 24 hourly rows into 1 summarized daily record (Data Engineering best practice)
    df_daily = df_hourly.groupby(df_hourly["timestamp"].dt.date).agg({
        "pm25": "mean",
        "temp": "mean",
        "wind": "mean"
    }).reset_index()
    
    df_daily = df_daily.rename(columns={
        "timestamp": "record_date",
        "pm25": "raw_pm25",
        "temp": "temperature_c",
        "wind": "wind_speed_kms"
    })
    
    return df_daily

def calculate_cpcb_aqi(pm25):
    """Piecewise linear interpolation formula for Indian CPCB AQI standards."""
    if pd.isna(pm25) or pm25 < 0: return None, "Unknown"
    if pm25 <= 30: return int(((50 - 0) / (30 - 0)) * (pm25 - 0) + 0), "Good"
    elif pm25 <= 60: return int(((100 - 51) / (60 - 30)) * (pm25 - 30) + 51), "Satisfactory"
    elif pm25 <= 90: return int(((200 - 101) / (90 - 60)) * (pm25 - 60) + 101), "Moderate"
    elif pm25 <= 120: return int(((300 - 201) / (120 - 90)) * (pm25 - 90) + 201), "Poor"
    elif pm25 <= 250: return int(((400 - 301) / (250 - 120)) * (pm25 - 120) + 301), "Very Poor"
    else:
        aqi_val = int(((500 - 401) / (500 - 250)) * (pm25 - 250) + 401)
        return min(500, aqi_val), "Severe"

def main():
    # Fetch the secret token safely from the GitHub runner environment memory
    db_url = os.environ.get("NEON_DATABASE_URL")
    if not db_url:
        print("CRITICAL ERROR: Environment variable NEON_DATABASE_URL is missing!")
        sys.exit(1)
        
    engine = create_engine(db_url)
    
    print("Extracting live weather and pollution metrics from Open-Meteo...")
    clean_df = extract_live_api_data()
    
    # Transform using statutory guidelines
    clean_df['pm25_cleaned'] = clean_df['raw_pm25'].astype(float)
    clean_df[['calculated_aqi', 'aqi_bucket']] = clean_df['pm25_cleaned'].apply(lambda x: pd.Series(calculate_cpcb_aqi(x)))
    clean_df['is_covid_lockdown'] = 0
    clean_df['is_odd_even_active'] = 0
    
    clean_df = clean_df.drop(columns=['raw_pm25'])
    
    print("Initiating idempotent transactional database updates to Neon...")
    with engine.begin() as conn:
        for _, row in clean_df.iterrows():
            conn.execute(text("""
                INSERT INTO silver_pollution_master (
                    record_date, pm25_cleaned, calculated_aqi, aqi_bucket, 
                    is_covid_lockdown, is_odd_even_active, temperature_c, wind_speed_kms
                ) 
                VALUES (:record_date, :pm25_cleaned, :calculated_aqi, :aqi_bucket, 
                        :is_covid_lockdown, :is_odd_even_active, :temperature_c, :wind_speed_kms)
                ON CONFLICT (record_date) DO UPDATE SET 
                    pm25_cleaned = EXCLUDED.pm25_cleaned,
                    calculated_aqi = EXCLUDED.calculated_aqi,
                    aqi_bucket = EXCLUDED.aqi_bucket,
                    temperature_c = EXCLUDED.temperature_c,
                    wind_speed_kms = EXCLUDED.wind_speed_kms;
            """), row.to_dict())
            
    print("🚀 Pipeline run successful! Warehouse states synchronized seamlessly.")

if __name__ == "__main__":
    main()
