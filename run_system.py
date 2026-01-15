import multiprocessing
import time
import os
import sys

# Define node configurations
nodes = [
    ("node1", 8001, {"lat": 30.7333, "lon": 76.7794}), # Chandigarh
    ("node2", 8002, {"lat": 28.7041, "lon": 77.1025}), # Delhi
    ("node3", 8003, {"lat": 19.0760, "lon": 72.8777}), # Mumbai
]

def run_aggregator():
    os.system("python aggregator_server.py")

def run_node(node_id, port, location):
    # We pass args via environment variables or modified command for simplicity
    # Here we import the function and run it directly in a process
    from clinic_node import start_node
    start_node(node_id, port, location)

if __name__ == "__main__":
    print("🚀 Initializing Decentralized Clinic Network...")
    
    processes = []
    
    # Start Aggregator
    p_agg = multiprocessing.Process(target=run_aggregator)
    p_agg.start()
    processes.append(p_agg)
    print("✅ Aggregator running on http://localhost:8000")
    
    time.sleep(2) # Wait for aggregator
    
    # Start Nodes
    for n_id, port, loc in nodes:
        p = multiprocessing.Process(target=run_node, args=(n_id, port, loc))
        p.start()
        processes.append(p)
        print(f"✅ {n_id} running on http://localhost:{port}")

    print("\nSystem is live! Press Ctrl+C to stop.")
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down network...")
        for p in processes:
            p.terminate()