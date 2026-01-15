import uvicorn
from fastapi import FastAPI, BackgroundTasks
import requests
import numpy as np
import hashlib
import json
import datetime
from pydantic import BaseModel
from typing import List

# Configuration
AGGREGATOR_URL = "http://localhost:8000/receive_data"

class PatientRecord(BaseModel):
    symptoms: List[str]
    severity: int  # 1-10


# Differential Privacy Settings
EPSILON = 0.5  # Privacy budget

app = FastAPI()

# Node specific config (set via args in real app, hardcoded here for demo logic)
NODE_CONFIG = {
    "node_id": "unknown",
    "port": 0,
    "location": {"lat": 0.0, "lon": 0.0}
}

def apply_differential_privacy(value: float, sensitivity: float = 1.0):
    """Add Laplace Noise for Differential Privacy"""
    scale = sensitivity / EPSILON
    noise = np.random.laplace(0, scale)
    return value + noise

def send_to_aggregator(record: dict):
    try:
        requests.post(AGGREGATOR_URL, json=record)
        print(f"[{NODE_CONFIG['node_id']}] Data sent securely.")
    except Exception as e:
        print(f"[{NODE_CONFIG['node_id']}] Failed to connect to aggregator: {e}")

@app.post("/patient_record")
async def add_patient(patient: PatientRecord, background_tasks: BackgroundTasks):
    
    # 1. Calculate Risk Score (Local Logic)
    risk_score = patient.severity * 1.5 # Simple logic
    
    # 2. Anonymization: SHA-256 Hash of data
    data_string = json.dumps(patient.dict(), sort_keys=True)
    data_hash = hashlib.sha256(data_string.encode()).hexdigest()
    
    # 3. Privacy: Apply Differential Privacy to numerical values
    noisy_risk = apply_differential_privacy(risk_score)
    
    # 4. Prepare Payload
    payload = {
        "node_id": NODE_CONFIG["node_id"],
        "timestamp": datetime.datetime.now().isoformat(),
        "encrypted_patient_hash": data_hash,
        "noisy_risk_score": noisy_risk,
        "symptom_vector": [1 if "fever" in patient.symptoms else 0], # Simplified
        "location": NODE_CONFIG["location"]
    }
    
    # 5. Send Async
    background_tasks.add_task(send_to_aggregator, payload)
    
    return {"status": "processed", "privacy_mode": "active"}

# Use a factory function to run different nodes
def start_node(node_id, port, location):
    NODE_CONFIG["node_id"] = node_id
    NODE_CONFIG["port"] = port
    NODE_CONFIG["location"] = location
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Default fallback
    start_node("node1", 8001, {"lat": 30.7333, "lon": 76.7794})