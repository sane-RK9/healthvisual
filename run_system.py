import subprocess
import time
import sys
import signal
import os

processes = []

def signal_handler(sig, frame):
    """Cleanup on exit"""
    print("\n\nShutting down all services...")
    for p in processes:
        p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_aggregator():
    """Start the aggregator server"""
    print("Starting Aggregator Server on port 8000...")
    p = subprocess.Popen([sys.executable, "aggregator_server.py"])
    processes.append(p)
    return p

def start_clinic_node(node_id, port):
    """Start a clinic node"""
    print(f"Starting {node_id} on port {port}...")
    p = subprocess.Popen([sys.executable, "clinic_node.py", node_id])
    processes.append(p)
    return p

def generate_sample_data():
    """Generate sample patient data for demo"""
    import requests
    import random
    import time
    
    symptom_sets = [
        ["cough", "fever"],
        ["headache", "fatigue"],
        ["fever", "difficulty breathing", "chest pain"],
        ["sore throat", "runny nose"],
        ["nausea", "dizziness"],
        ["body aches", "fever"],
        ["confusion", "chest pain"],
    ]
    
    node_ports = [8001, 8002, 8003]
    
    print("\nGenerating sample patient data...")
    print("=" * 60)
    
    for i in range(20):
        node_port = random.choice(node_ports)
        symptoms = random.choice(symptom_sets)
        severity = random.randint(1, 10)
        
        data = {
            "symptoms": symptoms,
            "severity": severity
        }
        
        try:
            response = requests.post(
                f"http://localhost:{node_port}/patient_record",
                json=data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Node {node_port}: Added patient | Risk: {result['risk_score']:.2f} | Symptoms: {', '.join(symptoms)}")
            else:
                print(f"✗ Node {node_port}: Failed to add patient data")
                
        except Exception as e:
            print(f"✗ Error connecting to node {node_port}: {str(e)}")
        
        time.sleep(0.5)
    
    print("=" * 60)
    print("Sample data generation complete!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Decentralized Clinic Network - System Launcher")
    print("=" * 60)
    print()
    
    # Start aggregator
    start_aggregator()
    time.sleep(3)
    
    # Start clinic nodes
    node_configs = [
        ("node1", 8001),  # Chandigarh
        ("node2", 8002),  # Delhi
        ("node3", 8003),  # Mumbai
    ]
    
    for node_id, port in node_configs:
        start_clinic_node(node_id, port)
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("All services started successfully!")
    print("=" * 60)
    print()
    print("🌐 Services:")
    print("   • Aggregator API: http://localhost:8000")
    print("   • Clinic Node 1:  http://localhost:8001")
    print("   • Clinic Node 2:  http://localhost:8002")
    print("   • Clinic Node 3:  http://localhost:8003")
    print()
    print("📊 API Endpoints:")
    print("   • Stats:     GET  http://localhost:8000/stats")
    print("   • Forecast:  GET  http://localhost:8000/forecast/patient_count")
    print("   • Map Data:  GET  http://localhost:8000/map_data")
    print()
    print("🔧 Frontend:")
    print("   • Copy the React component into your React app")
    print("   • Or use the HTML version for standalone testing")
    print()
    
    # Wait a bit for services to stabilize
    time.sleep(3)
    
    # Generate sample data
    try:
        generate_sample_data()
    except Exception as e:
        print(f"Warning: Could not generate sample data: {e}")
    
    print("\n📈 System Status:")
    try:
        import requests
        health = requests.get("http://localhost:8000/health", timeout=5).json()
        print(f"   • Aggregator: ✓ Healthy ({health['total_data_points']} data points)")
    except:
        print("   • Aggregator: ⚠ Check connection")
    
    for node_id, port in node_configs:
        try:
            import requests
            stats = requests.get(f"http://localhost:{port}/stats", timeout=5).json()
            print(f"   • {node_id.capitalize()}: ✓ Active ({stats['total_records']} records)")
        except:
            print(f"   • {node_id.capitalize()}: ⚠ Check connection")
    
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop all services")
    print("=" * 60)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)