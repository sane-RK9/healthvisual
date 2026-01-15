import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import datetime
import warnings

# Suppress ARIMA warnings for cleaner output
warnings.filterwarnings("ignore")

app = FastAPI(title="Clinic Aggregator & Forecaster")

# CORS setup for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (Replace with DB for production)
data_store = []

# --- Data Models ---
class ClinicData(BaseModel):
    node_id: str
    timestamp: str
    encrypted_patient_hash: str
    noisy_risk_score: float  # Differentially private
    symptom_vector: List[int]
    location: Dict[str, float]

# --- Helper: Generate Synthetic History ---
# We need history for ARIMA to work immediately upon start
def generate_synthetic_history():
    base_time = datetime.datetime.now() - datetime.timedelta(days=30)
    for i in range(30):
        current_time = base_time + datetime.timedelta(days=i)
        # Simulate a rising trend
        count = int(10 + (i * 0.5) + np.random.normal(0, 2)) 
        avg_risk = 3.0 + (i * 0.1) + np.random.normal(0, 0.5)
        
        data_store.append({
            "timestamp": current_time.isoformat(),
            "patient_count": max(0, count),
            "avg_risk": max(0, avg_risk),
            "node_id": "synthetic"
        })

generate_synthetic_history()

# --- API Endpoints ---

@app.post("/receive_data")
async def receive_data(data: ClinicData):
    """Receive anonymous data from clinic nodes"""
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "patient_count": 1, # Represents one batch/patient
        "avg_risk": data.noisy_risk_score,
        "node_id": data.node_id,
        "location": data.location
    }
    data_store.append(record)
    return {"status": "success", "hash": data.encrypted_patient_hash}

@app.get("/stats")
async def get_stats():
    """Get real-time aggregated statistics"""
    df = pd.DataFrame(data_store)
    if df.empty:
        return {"total_patients": 0, "avg_risk": 0}
    
    # Filter for last 24 hours for "Live" stats
    # For demo, we just take total
    return {
        "total_records": len(df),
        "current_avg_risk": round(df["avg_risk"].mean(), 2),
        "total_nodes_active": df["node_id"].nunique(),
        "latest_timestamp": df["timestamp"].max()
    }

@app.get("/forecast/{metric}")
async def get_forecast(metric: str, periods: int = 7):
    """
    ARIMA Forecasting Endpoint
    metric: 'patient_count' or 'avg_risk'
    """
    df = pd.DataFrame(data_store)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    
    # Resample to daily average/sum
    if metric == 'patient_count':
        daily_data = df['patient_count'].resample('D').sum().fillna(0)
    else:
        daily_data = df['avg_risk'].resample('D').mean().fillna(0)
    
    if len(daily_data) < 5:
        raise HTTPException(status_code=400, detail="Not enough data for forecasting")

    try:
        # ARIMA Model (1,1,1)
        model = ARIMA(daily_data, order=(1, 1, 1))
        model_fit = model.fit()
        
        forecast_result = model_fit.get_forecast(steps=periods)
        forecast_values = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int()

        # Format for frontend
        history = [{"date": str(k.date()), "value": v} for k, v in daily_data.tail(14).items()]
        prediction = []
        for i, val in enumerate(forecast_values):
            date = daily_data.index[-1] + datetime.timedelta(days=i+1)
            prediction.append({
                "date": str(date.date()),
                "value": round(val, 2),
                "lower_bound": round(conf_int.iloc[i, 0], 2),
                "upper_bound": round(conf_int.iloc[i, 1], 2)
            })

        return {"history": history, "forecast": prediction}
        
    except Exception as e:
        print(f"ARIMA Error: {e}")
        return {"error": str(e), "history": [], "forecast": []}

@app.get("/map_data")
async def get_map_data():
    """Get location data for heatmaps"""
    # Filter real nodes (exclude synthetic)
    real_data = [d for d in data_store if "location" in d]
    return real_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)