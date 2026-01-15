# Decentralized P2P Clinic Network

A peer-to-peer anonymous data sharing system for decentralized clinics with ARIMA forecasting, differential privacy, and real-time visualization.

## 🏗️ System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Clinic     │     │  Clinic     │     │  Clinic     │
│  Node 1     │     │  Node 2     │     │  Node 3     │
│  (8001)     │     │  (8002)     │     │  (8003)     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │   Anonymous Data with Differential Privacy
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Aggregator  │
                    │   (8000)    │
                    │  + ARIMA    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   REST API  │
                    │     +       │
                    │   React UI  │
                    └─────────────┘
```

## ✨ Features

- **P2P Architecture**: Direct node-to-node communication with HTTP/WebSocket support
- **Differential Privacy**: Laplace noise injection for data anonymization
- **SHA-256 Hashing**: Data integrity verification without revealing content
- **ARIMA Forecasting**: Time-series prediction for patient volumes and risk scores
- **Real-time Visualization**: Plotly charts with interactive dashboards
- **Geographic Mapping**: OpenStreetMap integration (simulated for prototype)
- **RESTful API**: Complete FastAPI backend with async support

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ (for React frontend)
- pip (Python package manager)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 2. File Structure

Create the following files in your project directory:

```
clinic-network/
├── aggregator_server.py      # Aggregator with ARIMA
├── clinic_node.py             # Clinic node implementation
├── run_system.py              # System launcher
├── test_api.py                # API testing suite
├── requirements.txt           # Python dependencies
└── frontend/
    └── Dashboard.jsx          # React dashboard component
```

### 3. Launch the System

```bash
# Start all services (aggregator + 3 nodes)
python run_system.py
```

This will:
- Start the aggregator on port 8000
- Start clinic nodes on ports 8001, 8002, 8003
- Generate sample patient data
- Display service URLs and status

### 4. Run Tests

In a separate terminal:

```bash
# Test all API endpoints
python test_api.py
```

## 🔌 API Endpoints

### Aggregator (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/receive_data` | POST | Receive anonymous data from nodes |
| `/stats` | GET | Get aggregated statistics |
| `/forecast/{metric}?periods=7` | GET | Get ARIMA forecast |
| `/map_data` | GET | Get geographic distribution |
| `/health` | GET | Health check |

### Clinic Nodes (Ports 8001-8003)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/patient_record` | POST | Add patient symptom record |
| `/stats` | GET | Get node statistics |
| `/sync` | POST | Manually sync with aggregator |

## 📊 Using the API

### Add Patient Record

```bash
curl -X POST http://localhost:8001/patient_record \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": ["fever", "cough"],
    "severity": 7
  }'
```

### Get Aggregated Stats

```bash
curl http://localhost:8000/stats
```

### Get Patient Volume Forecast

```bash
curl http://localhost:8000/forecast/patient_count?periods=7
```

### Get Risk Score Forecast

```bash
curl http://localhost:8000/forecast/avg_risk_score?periods=7
```

## 🎨 Frontend Setup

### React Integration

1. Create a React app:
```bash
npx create-react-app clinic-dashboard
cd clinic-dashboard
```

2. Install dependencies:
```bash
npm install recharts lucide-react
```

3. Copy the Dashboard component to `src/Dashboard.jsx`

4. Update `src/App.js`:
```javascript
import Dashboard from './Dashboard';

function App() {
  return <Dashboard />;
}

export default App;
```

5. Start the development server:
```bash
npm start
```

The dashboard will be available at `http://localhost:3000`

### Standalone HTML (Alternative)

For testing without React setup, you can access the aggregator API directly:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Clinic Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
</head>
<body>
    <div id="stats"></div>
    <div id="chart"></div>
    
    <script>
        // Fetch and display data
        fetch('http://localhost:8000/stats')
            .then(r => r.json())
            .then(data => {
                document.getElementById('stats').innerHTML = 
                    `<h2>Patients: ${data.total_patients}</h2>`;
            });
    </script>
</body>
</html>
```

## 🔐 Privacy & Security

### Differential Privacy

Each clinic node applies differential privacy before sending data:

```python
# Laplace noise is added to numerical values
epsilon = 0.5  # Privacy budget
sensitivity = 1.0
noise = np.random.laplace(0, sensitivity / epsilon)
noisy_value = original_value + noise
```

### Data Anonymization

- No personally identifiable information (PII) is stored
- Data is hashed using SHA-256 for integrity
- Nodes cannot see each other's raw data
- Only aggregated statistics are available

### Communication Security

For production deployment, add:
- HTTPS/TLS encryption
- API authentication (JWT tokens)
- Rate limiting
- Input validation

## 📈 ARIMA Forecasting

The system uses ARIMA(1,1,1) for time-series forecasting:

- **AR (1)**: Autoregressive component
- **I (1)**: Differencing for stationarity
- **MA (1)**: Moving average component

Forecasts include:
- Point predictions
- Confidence intervals (upper/lower bounds)
- 7-day default forecast period

## 🗺️ Geographic Visualization

The prototype uses simulated coordinates:

- **Node 1**: Chandigarh (30.73°N, 76.78°E)
- **Node 2**: Delhi (28.70°N, 77.10°E)
- **Node 3**: Mumbai (19.08°N, 72.88°E)

For production, integrate with:
- OpenStreetMap (Leaflet.js)
- Google Maps API
- Mapbox

## 🧪 Testing

### Manual Testing

```bash
# Add test data to node 1
curl -X POST http://localhost:8001/patient_record \
  -H "Content-Type: application/json" \
  -d '{"symptoms": ["fever", "cough"], "severity": 8}'

# Check aggregator received it
curl http://localhost:8000/stats

# Get forecast
curl http://localhost:8000/forecast/patient_count
```

### Automated Testing

```bash
python test_api.py
```

Tests include:
- Node patient record creation
- Statistics aggregation
- ARIMA forecasting
- Differential privacy verification
- Map data generation

## 🔧 Configuration

### Node Locations

Edit `clinic_node.py` to change node coordinates:

```python
node_configs = {
    "node1": {"lat": 30.7333, "lon": 76.7794, "port": 8001},
    "node2": {"lat": 28.7041, "lon": 77.1025, "port": 8002},
    "node3": {"lat": 19.0760, "lon": 72.8777, "port": 8003},
}
```

### Privacy Budget

Adjust epsilon in `clinic_node.py`:

```python
epsilon = 0.5  # Lower = more privacy, less accuracy
```

### ARIMA Parameters

Modify in `aggregator_server.py`:

```python
model = ARIMA(time_series, order=(1, 1, 1))  # (p, d, q)
```

## 📝 Data Flow

1. **Patient Visit**: Clinic records symptoms and severity
2. **Risk Calculation**: Node calculates risk score locally
3. **Privacy Application**: Differential privacy adds noise
4. **Hashing**: Data is hashed for verification
5. **Transmission**: Anonymous data sent to aggregator
6. **Aggregation**: Aggregator combines data from all nodes
7. **Forecasting**: ARIMA models predict future trends
8. **Visualization**: Dashboard displays real-time insights

## 🚧 Production Considerations

For production deployment:

1. **Database**: Add PostgreSQL/MongoDB for persistence
2. **Authentication**: Implement OAuth2/JWT
3. **Monitoring**: Add Prometheus + Grafana
4. **Logging**: Structured logging with ELK stack
5. **Containerization**: Docker + Kubernetes
6. **Load Balancing**: Nginx or cloud load balancer
7. **CORS**: Configure properly for your domain
8. **Rate Limiting**: Prevent API abuse
9. **Backup**: Automated data backups
10. **Encryption**: End-to-end encryption for data in transit

## 🐛 Troubleshooting

### Nodes not connecting to aggregator

```bash
# Check if aggregator is running
curl http://localhost:8000/health

# Check node status
curl http://localhost:8001/stats
```

### ARIMA forecast errors

- Ensure at least 10 data points exist
- System generates synthetic data if insufficient real data
- Check logs for specific ARIMA fitting errors

### CORS issues

Frontend and backend on different ports may cause CORS issues. The code includes CORS middleware, but verify:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📚 Dependencies

- **FastAPI**: Modern async web framework
- **Uvicorn**: ASGI server
- **NumPy**: Numerical computing
- **Statsmodels**: ARIMA implementation
- **Pydantic**: Data validation
- **HTTPX**: Async HTTP client
- **Recharts**: React charting library
- **Lucide React**: Icon library

## 🤝 Contributing

To extend the system:

1. Add new privacy mechanisms (homomorphic encryption, secure MPC)
2. Implement WebSocket for real-time updates
3. Add more forecasting models (LSTM, Prophet)
4. Integrate actual OpenStreetMap
5. Add authentication and user management
6. Implement data persistence layer

## 📄 License

This is a prototype for educational purposes. Add appropriate license for production use.

## 🎯 Next Steps

1. **Run the system**: `python run_system.py`
2. **Test the API**: `python test_api.py`
3. **View dashboard**: Open React app at `http://localhost:3000`
4. **Add custom data**: Use curl or Postman to POST patient records
5. **Explore forecasts**: Check `/forecast` endpoints for predictions

---

**Built with**: FastAPI • React • ARIMA • Differential Privacy • OpenStreetMap