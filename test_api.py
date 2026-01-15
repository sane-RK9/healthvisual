import requests
import json
import random
import time

def test_system():
    print("🧪 Starting System Test...")
    
    # 1. Simulate Patient Visits across nodes
    symptoms_list = [["fever"], ["cough", "fever"], ["headache"]]
    
    for i in range(5):
        node_port = random.choice([8001, 8002, 8003])
        payload = {
            "symptoms": random.choice(symptoms_list),
            "severity": random.randint(1, 10)
        }
        try:
            r = requests.post(f"http://localhost:{node_port}/patient_record", json=payload)
            print(f"Sent patient to Node {node_port}: {r.status_code}")
        except:
            print(f"Node {node_port} not reachable")
            
    time.sleep(2) # Wait for async processing
    
    # 2. Check Aggregator Stats
    r = requests.get("http://localhost:8000/stats")
    stats = r.json()
    print(f"\n📊 Network Stats: {json.dumps(stats, indent=2)}")
    
    # 3. Check Forecasting
    print("\n🔮 Fetching ARIMA Forecast...")
    r = requests.get("http://localhost:8000/forecast/patient_count")
    if r.status_code == 200:
        forecast = r.json()
        print("Forecast generated successfully.")
        print(f"Prediction next day: {forecast['forecast'][0]['value']}")
    else:
        print(f"Forecast failed: {r.text}")

if __name__ == "__main__":
    test_system()