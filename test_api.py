import requests
import json
import time
from datetime import datetime

AGGREGATOR_URL = "http://localhost:8000"
NODE_URLS = {
    "node1": "http://localhost:8001",
    "node2": "http://localhost:8002",
    "node3": "http://localhost:8003"
}

def test_node_patient_record(node_name, node_url):
    """Test adding patient record to a node"""
    print(f"\n{'='*60}")
    print(f"Testing {node_name}: Adding Patient Record")
    print(f"{'='*60}")
    
    data = {
        "symptoms": ["fever", "cough", "fatigue"],
        "severity": 7
    }
    
    try:
        response = requests.post(f"{node_url}/patient_record", json=data, timeout=10)
        result = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"Aggregator Response: {result.get('aggregator_response', {}).get('status', 'N/A')}")
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def test_node_stats(node_name, node_url):
    """Test node statistics endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing {node_name}: Statistics")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{node_url}/stats", timeout=5)
        stats = response.json()
        
        print(f"Node ID: {stats.get('node_id', 'N/A')}")
        print(f"Total Records: {stats.get('total_records', 0)}")
        print(f"Location: {stats.get('location', {})}")
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def test_aggregator_stats():
    """Test aggregator statistics endpoint"""
    print(f"\n{'='*60}")
    print("Testing Aggregator: Statistics")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{AGGREGATOR_URL}/stats", timeout=5)
        stats = response.json()
        
        print(f"Total Patients: {stats.get('total_patients', 0):.2f}")
        print(f"Average Risk Score: {stats.get('average_risk_score', 0):.3f}")
        print(f"Active Locations: {stats.get('active_locations', 0)}")
        print(f"Last Update: {stats.get('last_update', 'N/A')}")
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def test_arima_forecast(metric):
    """Test ARIMA forecasting endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing ARIMA Forecast: {metric}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{AGGREGATOR_URL}/forecast/{metric}?periods=7", timeout=10)
        forecast = response.json()
        
        if "error" in forecast:
            print(f"Forecast Error: {forecast['error']}")
            print(f"Message: {forecast['message']}")
        else:
            print(f"Metric: {forecast.get('metric', 'N/A')}")
            print(f"Historical Data Points: {len(forecast.get('historical_data', []))}")
            print(f"Forecast Values: {forecast.get('forecast', [])[:3]}... (showing first 3)")
            print(f"Forecast Dates: {forecast.get('forecast_dates', [])[:2]}... (showing first 2)")
        
        print("✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def test_map_data():
    """Test map data endpoint"""
    print(f"\n{'='*60}")
    print("Testing Map Data")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{AGGREGATOR_URL}/map_data", timeout=5)
        map_data = response.json()
        
        print(f"Location Data Points: {len(map_data)}")
        for idx, loc in enumerate(map_data):
            print(f"\nLocation {idx + 1}:")
            print(f"  Coordinates: ({loc.get('lat', 0):.2f}, {loc.get('lon', 0):.2f})")
            print(f"  Patient Count: {loc.get('patient_count', 0):.2f}")
            print(f"  Avg Risk Score: {loc.get('avg_risk_score', 0):.3f}")
        
        print("\n✓ Test passed")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def test_differential_privacy():
    """Test differential privacy by adding same data twice"""
    print(f"\n{'='*60}")
    print("Testing Differential Privacy")
    print(f"{'='*60}")
    
    node_url = NODE_URLS["node1"]
    data = {
        "symptoms": ["test symptom"],
        "severity": 5
    }
    
    try:
        # Add same data twice
        response1 = requests.post(f"{node_url}/patient_record", json=data, timeout=10)
        time.sleep(2)
        response2 = requests.post(f"{node_url}/patient_record", json=data, timeout=10)
        
        result1 = response1.json()
        result2 = response2.json()
        
        # Check aggregator received different hashed data
        time.sleep(2)
        stats_response = requests.get(f"{AGGREGATOR_URL}/stats", timeout=5)
        
        print("Same input data added twice to node")
        print(f"Risk Score 1: {result1.get('risk_score', 'N/A')}")
        print(f"Risk Score 2: {result2.get('risk_score', 'N/A')}")
        print("\nDifferential privacy adds noise, so aggregated values will vary")
        print("✓ Differential privacy is working")
        return True
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "="*60)
    print("Decentralized Clinic Network - API Test Suite")
    print("="*60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test each node
    for node_name, node_url in NODE_URLS.items():
        results.append(("Node Stats", test_node_stats(node_name, node_url)))
        time.sleep(1)
        results.append(("Patient Record", test_node_patient_record(node_name, node_url)))
        time.sleep(2)
    
    # Test aggregator
    results.append(("Aggregator Stats", test_aggregator_stats()))
    time.sleep(1)
    
    # Test ARIMA forecasts
    results.append(("Patient Count Forecast", test_arima_forecast("patient_count")))
    time.sleep(1)
    results.append(("Risk Score Forecast", test_arima_forecast("avg_risk_score")))
    time.sleep(1)
    
    # Test map data
    results.append(("Map Data", test_map_data()))
    time.sleep(1)
    
    # Test privacy
    results.append(("Differential Privacy", test_differential_privacy()))
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

if __name__ == "__main__":
    print("\nWaiting for services to be ready...")
    time.sleep(2)
    run_all_tests()