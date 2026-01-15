from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
import hashlib
import json
import httpx
import asyncio
from datetime import datetime, timedelta
import uvicorn

class SymptomRecord(BaseModel):
    symptoms: List[str]
    severity: int  # 1-10
    timestamp: Optional[str] = None

class ClinicNode:
    def __init__(self, node_id: str, location: Dict[str, float], port: int):
        self.node_id = node_id
        self.location = location  # {"lat": ..., "lon": ...}
        self.port = port
        self.patient_records = []
        self.aggregator_url = "http://localhost:8000"
        
    def add_patient_record(self, record: SymptomRecord):
        """Add patient record with timestamp"""
        if not record.timestamp:
            record.timestamp = datetime.now().isoformat()
        
        risk_score = self.calculate_risk_score(record)
        
        self.patient_records.append({
            "symptoms": record.symptoms,
            "severity": record.severity,
            "risk_score": risk_score,
            "timestamp": record.timestamp
        })
        
        return risk_score
    
    def calculate_risk_score(self, record: SymptomRecord) -> float:
        """Calculate risk score based on symptoms and severity"""
        high_risk_symptoms = ["fever", "difficulty breathing", "chest pain", "confusion"]
        
        risk = record.severity / 10.0
        
        # Increase risk for high-risk symptoms
        for symptom in record.symptoms:
            if any(hrs in symptom.lower() for hrs in high_risk_symptoms):
                risk += 0.2
        
        return min(risk, 1.0)
    
    def apply_differential_privacy(self, data: Dict) -> Dict:
        """Apply differential privacy with Laplace noise"""
        epsilon = 0.5  # Privacy budget
        sensitivity = 1.0
        
        # Add Laplace noise to numerical values
        noisy_data = data.copy()
        if "patient_count" in data:
            noise = np.random.laplace(0, sensitivity / epsilon)
            noisy_data["patient_count"] = max(0, data["patient_count"] + noise)
        
        if "avg_risk_score" in data:
            noise = np.random.laplace(0, sensitivity / epsilon)
            noisy_data["avg_risk_score"] = np.clip(data["avg_risk_score"] + noise, 0, 1)
        
        return noisy_data
    
    def hash_node_data(self, data: Dict) -> str:
        """Create hash of node data for anonymization"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def get_aggregated_data(self) -> Dict:
        """Prepare anonymized data for aggregator"""
        if not self.patient_records:
            return None
        
        # Calculate statistics
        recent_records = [r for r in self.patient_records 
                         if datetime.fromisoformat(r["timestamp"]) > datetime.now() - timedelta(days=7)]
        
        if not recent_records:
            return None
        
        data = {
            "patient_count": len(recent_records),
            "avg_risk_score": np.mean([r["risk_score"] for r in recent_records]),
            "location": self.location,
            "timestamp": datetime.now().isoformat()
        }
        
        # Apply differential privacy
        noisy_data = self.apply_differential_privacy(data)
        
        # Add hash for verification (not for identification)
        noisy_data["data_hash"] = self.hash_node_data(data)
        
        return noisy_data
    
    async def send_to_aggregator(self):
        """Send anonymized data to aggregator"""
        data = self.get_aggregated_data()
        if not data:
            return {"status": "no_data"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.aggregator_url}/receive_data",
                    json=data,
                    timeout=10.0
                )
                return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Create FastAPI app factory
def create_node_app(node_id: str, location: Dict[str, float], port: int):
    app = FastAPI(title=f"Clinic Node {node_id}")
    node = ClinicNode(node_id, location, port)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.post("/patient_record")
    async def add_patient_record(record: SymptomRecord):
        """Add new patient symptom record"""
        risk_score = node.add_patient_record(record)
        
        # Send updated data to aggregator
        result = await node.send_to_aggregator()
        
        return {
            "status": "success",
            "risk_score": risk_score,
            "aggregator_response": result
        }
    
    @app.get("/stats")
    async def get_stats():
        """Get local node statistics"""
        return {
            "node_id": node.node_id,
            "total_records": len(node.patient_records),
            "location": node.location
        }
    
    @app.post("/sync")
    async def sync_with_aggregator():
        """Manually sync data with aggregator"""
        result = await node.send_to_aggregator()
        return result
    
    return app, node

# Example: Run individual node
if __name__ == "__main__":
    import sys
    
    # Node configuration from command line or defaults
    node_configs = {
        "node1": {"lat": 30.7333, "lon": 76.7794, "port": 8001},  # Chandigarh
        "node2": {"lat": 28.7041, "lon": 77.1025, "port": 8002},  # Delhi
        "node3": {"lat": 19.0760, "lon": 72.8777, "port": 8003},  # Mumbai
    }
    
    node_id = sys.argv[1] if len(sys.argv) > 1 else "node1"
    config = node_configs[node_id]
    
    app, _ = create_node_app(node_id, {"lat": config["lat"], "lon": config["lon"]}, config["port"])
    
    print(f"Starting {node_id} on port {config['port']}")
    uvicorn.run(app, host="0.0.0.0", port=config["port"])