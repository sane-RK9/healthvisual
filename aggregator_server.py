from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings('ignore')

app = FastAPI(title="Clinic Data Aggregator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NodeData(BaseModel):
    patient_count: float
    avg_risk_score: float
    location: Dict[str, float]
    timestamp: str
    data_hash: str

class Aggregator:
    def __init__(self):
        self.node_data = []  # Store all received data
        self.time_series_data = defaultdict(list)  # For ARIMA modeling
        
    def add_node_data(self, data: NodeData):
        """Store anonymous node data"""
        data_dict = data.dict()
        self.node_data.append(data_dict)
        
        # Update time series for ARIMA
        date_key = datetime.fromisoformat(data.timestamp).date().isoformat()
        self.time_series_data[date_key].append({
            "patient_count": data.patient_count,
            "avg_risk_score": data.avg_risk_score
        })
        
        return {"status": "received", "data_points": len(self.node_data)}
    
    def get_aggregated_stats(self) -> Dict:
        """Get current aggregated statistics"""
        if not self.node_data:
            return {"total_nodes": 0, "message": "No data available"}
        
        recent_data = [d for d in self.node_data 
                      if datetime.fromisoformat(d["timestamp"]) > datetime.now() - timedelta(hours=24)]
        
        if not recent_data:
            return {"message": "No recent data"}
        
        total_patients = sum(d["patient_count"] for d in recent_data)
        avg_risk = np.mean([d["avg_risk_score"] for d in recent_data])
        
        # Group by location
        location_data = []
        location_groups = defaultdict(list)
        
        for d in recent_data:
            loc_key = f"{d['location']['lat']:.2f},{d['location']['lon']:.2f}"
            location_groups[loc_key].append(d)
        
        for loc_key, records in location_groups.items():
            lat, lon = map(float, loc_key.split(','))
            location_data.append({
                "lat": lat,
                "lon": lon,
                "patient_count": sum(r["patient_count"] for r in records),
                "avg_risk_score": np.mean([r["avg_risk_score"] for r in records]),
                "data_points": len(records)
            })
        
        return {
            "total_patients": total_patients,
            "average_risk_score": avg_risk,
            "active_locations": len(location_data),
            "location_data": location_data,
            "last_update": recent_data[-1]["timestamp"]
        }
    
    def prepare_time_series(self, metric: str = "patient_count") -> List[float]:
        """Prepare time series data for ARIMA"""
        if not self.time_series_data:
            return []
        
        # Sort by date and aggregate
        sorted_dates = sorted(self.time_series_data.keys())
        values = []
        
        for date in sorted_dates:
            day_data = self.time_series_data[date]
            if metric == "patient_count":
                values.append(sum(d["patient_count"] for d in day_data))
            elif metric == "avg_risk_score":
                values.append(np.mean([d["avg_risk_score"] for d in day_data]))
        
        return values
    
    def arima_forecast(self, metric: str = "patient_count", periods: int = 7) -> Dict:
        """Perform ARIMA forecasting"""
        try:
            time_series = self.prepare_time_series(metric)
            
            if len(time_series) < 10:
                # Generate synthetic historical data for demo
                base_value = 50 if metric == "patient_count" else 0.3
                time_series = [base_value + np.random.normal(0, base_value * 0.2) 
                              for _ in range(30)]
                time_series.extend(self.prepare_time_series(metric))
            
            # Fit ARIMA model
            model = ARIMA(time_series, order=(1, 1, 1))
            fitted_model = model.fit()
            
            # Forecast
            forecast = fitted_model.forecast(steps=periods)
            
            # Get confidence intervals
            forecast_result = fitted_model.get_forecast(steps=periods)
            conf_int = forecast_result.conf_int()
            
            return {
                "metric": metric,
                "historical_data": time_series[-14:],  # Last 2 weeks
                "forecast": forecast.tolist(),
                "confidence_lower": conf_int.iloc[:, 0].tolist(),
                "confidence_upper": conf_int.iloc[:, 1].tolist(),
                "forecast_dates": [(datetime.now() + timedelta(days=i+1)).isoformat() 
                                  for i in range(periods)]
            }
        except Exception as e:
            return {"error": str(e), "message": "ARIMA forecast failed"}
    
    def get_map_data(self) -> List[Dict]:
        """Get data formatted for map visualization"""
        stats = self.get_aggregated_stats()
        if "location_data" not in stats:
            return []
        
        return stats["location_data"]

# Global aggregator instance
aggregator = Aggregator()

@app.post("/receive_data")
async def receive_node_data(data: NodeData):
    """Receive anonymous data from clinic nodes"""
    result = aggregator.add_node_data(data)
    return result

@app.get("/stats")
async def get_statistics():
    """Get aggregated statistics"""
    return aggregator.get_aggregated_stats()

@app.get("/forecast/{metric}")
async def get_forecast(metric: str, periods: int = 7):
    """Get ARIMA forecast for specified metric"""
    if metric not in ["patient_count", "avg_risk_score"]:
        raise HTTPException(400, "Invalid metric. Use 'patient_count' or 'avg_risk_score'")
    
    return aggregator.arima_forecast(metric, periods)

@app.get("/map_data")
async def get_map_data():
    """Get data for map visualization"""
    return aggregator.get_map_data()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_data_points": len(aggregator.node_data),
        "time_series_days": len(aggregator.time_series_data)
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting Aggregator Server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)