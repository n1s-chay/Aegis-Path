# Aegis-Path Usage Examples

This document provides practical examples of how to use the Aegis-Path API.

## Table of Contents
1. [Starting the Application](#starting-the-application)
2. [Web Interface Usage](#web-interface-usage)
3. [API Examples](#api-examples)
4. [Python Examples](#python-examples)
5. [Common Use Cases](#common-use-cases)

## Starting the Application

### Quick Start
```bash
# Install dependencies
pip install flask flask-cors opencv-python-headless numpy requests

# Start the server
python3 app.py
```

### Using the Startup Script
```bash
# Make the script executable (first time only)
chmod +x start.sh

# Run the startup script
./start.sh
```

The server will start at `http://localhost:5000`

## Web Interface Usage

1. Open `index.html` in your web browser
2. Enter starting location coordinates:
   - Latitude: e.g., 12.9716
   - Longitude: e.g., 77.5946
3. Enter destination coordinates:
   - Latitude: e.g., 12.9352
   - Longitude: e.g., 77.6245
4. Click "Find Safest Path" or "Show Alternative Paths"
5. Review the safety scores and path information

### Sample Locations (Bangalore, India)

| Location | Latitude | Longitude |
|----------|----------|-----------|
| MG Road | 12.9716 | 77.5946 |
| Koramangala | 12.9352 | 77.6245 |
| Indiranagar | 12.9784 | 77.6408 |
| Whitefield | 12.9698 | 77.7499 |

## API Examples

### 1. Health Check

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Aegis-Path"
}
```

### 2. Find Safest Path

**Request:**
```bash
curl -X POST http://localhost:5000/api/path/safe \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 12.9716, "lng": 77.5946},
    "end": {"lat": 12.9352, "lng": 77.6245}
  }'
```

**Response:**
```json
{
  "success": true,
  "path": {
    "waypoints": [
      [12.9716, 77.5946],
      [12.9625, 77.602075],
      [12.9534, 77.60955],
      [12.9443, 77.617025],
      [12.9352, 77.6245]
    ],
    "safety_score": 61.18,
    "is_safe": true,
    "distance_km": 5.18,
    "segments": [...]
  }
}
```

### 3. Find Alternative Paths

**Request:**
```bash
curl -X POST http://localhost:5000/api/path/alternatives \
  -H "Content-Type: application/json" \
  -d '{
    "start": {"lat": 12.9716, "lng": 77.5946},
    "end": {"lat": 12.9352, "lng": 77.6245},
    "num_alternatives": 3
  }'
```

**Response:**
```json
{
  "success": true,
  "paths": [
    {
      "waypoints": [...],
      "safety_score": 61.18,
      "is_safe": true,
      "distance_km": 5.18
    },
    {
      "waypoints": [...],
      "safety_score": 60.60,
      "is_safe": true,
      "distance_km": 5.25
    },
    {
      "waypoints": [...],
      "safety_score": 60.58,
      "is_safe": true,
      "distance_km": 5.21
    }
  ]
}
```

### 4. Check Location Safety

**Request:**
```bash
curl -X POST http://localhost:5000/api/safety/location \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"lat": 12.9716, "lng": 77.5946}
  }'
```

**Response:**
```json
{
  "success": true,
  "location": {"lat": 12.9716, "lng": 77.5946},
  "safety": {
    "overall_safety": 62.69,
    "incident_score": 92.28,
    "lighting_score": 50.00,
    "crowd_density": 50.00,
    "crowd_safety_score": 50.00
  }
}
```

### 5. Get Incidents Near Location

**Request:**
```bash
curl "http://localhost:5000/api/incidents?lat=12.9716&lng=77.5946&radius=2"
```

**Response:**
```json
{
  "success": true,
  "incidents": [
    {
      "incident_id": "INC-20251101120000",
      "location": {"lat": 12.9716, "lng": 77.5946},
      "incident_type": "theft",
      "severity": 2,
      "timestamp": "2025-11-01T12:00:00"
    }
  ]
}
```

### 6. Add Incident Report

**Request:**
```bash
curl -X POST http://localhost:5000/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "location": {"lat": 12.9716, "lng": 77.5946},
    "incident_type": "theft",
    "severity": 3,
    "timestamp": "2025-11-15T10:30:00"
  }'
```

**Response:**
```json
{
  "success": true,
  "incident": {
    "incident_id": "INC-20251115103000",
    "location": {"lat": 12.9716, "lng": 77.5946},
    "incident_type": "theft",
    "severity": 3,
    "timestamp": "2025-11-15T10:30:00"
  }
}
```

### 7. Analyze Camera Feed/Image

**Request:**
```bash
curl -X POST http://localhost:5000/api/camera/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.jpg"
  }'
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "lighting": 75.5,
    "crowd_density": 35.2
  }
}
```

## Python Examples

### Example 1: Find Safe Path
```python
import requests

API_BASE = 'http://localhost:5000'

# Define start and end locations
start = {"lat": 12.9716, "lng": 77.5946}
end = {"lat": 12.9352, "lng": 77.6245}

# Find safe path
response = requests.post(
    f'{API_BASE}/api/path/safe',
    json={'start': start, 'end': end}
)

data = response.json()
if data['success']:
    path = data['path']
    print(f"Safety Score: {path['safety_score']:.2f}/100")
    print(f"Distance: {path['distance_km']:.2f} km")
    print(f"Safe: {'Yes' if path['is_safe'] else 'No'}")
```

### Example 2: Check Multiple Locations
```python
import requests

API_BASE = 'http://localhost:5000'

locations = [
    {"name": "MG Road", "lat": 12.9716, "lng": 77.5946},
    {"name": "Koramangala", "lat": 12.9352, "lng": 77.6245},
    {"name": "Indiranagar", "lat": 12.9784, "lng": 77.6408}
]

for loc in locations:
    response = requests.post(
        f'{API_BASE}/api/safety/location',
        json={'location': {'lat': loc['lat'], 'lng': loc['lng']}}
    )
    
    data = response.json()
    if data['success']:
        safety = data['safety']['overall_safety']
        print(f"{loc['name']}: {safety:.2f}/100")
```

### Example 3: Using the Core Modules Directly
```python
from pathfinder import PathFinder
from safety_engine import SafetyEngine

# Initialize
finder = PathFinder()
safety_engine = SafetyEngine()

# Find safe path
start = (12.9716, 77.5946)
end = (12.9352, 77.6245)
path = finder.find_safe_path(start, end)

print(f"Safety Score: {path['safety_score']:.2f}")
print(f"Distance: {path['distance_km']:.2f} km")

# Check location safety
location = (12.9716, 77.5946)
safety = safety_engine.calculate_location_safety(location)
print(f"Overall Safety: {safety['overall_safety']:.2f}")
```

### Example 4: Analyze Camera Image
```python
from camera_analyzer import CameraAnalyzer
import cv2

analyzer = CameraAnalyzer()

# Analyze an image file
analysis = analyzer.analyze_image_file('path/to/image.jpg')
print(f"Lighting: {analysis['lighting']:.2f}/100")
print(f"Crowd Density: {analysis['crowd_density']:.2f}/100")

# Or analyze a camera frame
cap = cv2.VideoCapture(0)  # Use webcam
ret, frame = cap.read()
if ret:
    analysis = analyzer.analyze_frame(frame)
    print(f"Lighting: {analysis['lighting']:.2f}/100")
    print(f"Crowd Density: {analysis['crowd_density']:.2f}/100")
cap.release()
```

## Common Use Cases

### Use Case 1: Safe Route for Evening Walk
```python
# User wants to walk home from work in the evening
start = {"lat": 12.9716, "lng": 77.5946}  # Office
end = {"lat": 12.9352, "lng": 77.6245}    # Home

# Get multiple alternatives
response = requests.post(
    'http://localhost:5000/api/path/alternatives',
    json={'start': start, 'end': end, 'num_alternatives': 3}
)

paths = response.json()['paths']
# Choose the safest path
safest = paths[0]
print(f"Recommended path has safety score: {safest['safety_score']:.2f}")
```

### Use Case 2: Check Area Safety Before Visit
```python
# User wants to check if an area is safe before visiting
location = {"lat": 12.9716, "lng": 77.5946}

response = requests.post(
    'http://localhost:5000/api/safety/location',
    json={'location': location}
)

safety = response.json()['safety']
overall = safety['overall_safety']

if overall >= 70:
    print("✅ Area is considered safe")
elif overall >= 40:
    print("⚠️ Area has moderate safety - use caution")
else:
    print("❌ Area may be unsafe - consider alternatives")
```

### Use Case 3: Report a Safety Incident
```python
from datetime import datetime

# User wants to report a safety incident
incident = {
    "location": {"lat": 12.9716, "lng": 77.5946},
    "incident_type": "harassment",
    "severity": 4,
    "timestamp": datetime.now().isoformat()
}

response = requests.post(
    'http://localhost:5000/api/incidents',
    json=incident
)

if response.json()['success']:
    print("Incident reported successfully")
```

### Use Case 4: Real-time Safety Monitoring
```python
import time

def monitor_location_safety(lat, lng, interval=60):
    """Monitor safety of a location at regular intervals"""
    while True:
        response = requests.post(
            'http://localhost:5000/api/safety/location',
            json={'location': {'lat': lat, 'lng': lng}}
        )
        
        safety = response.json()['safety']['overall_safety']
        print(f"{datetime.now()}: Safety Score = {safety:.2f}/100")
        
        if safety < 40:
            print("⚠️ WARNING: Safety score is low!")
        
        time.sleep(interval)

# Monitor current location every minute
monitor_location_safety(12.9716, 77.5946)
```

## Error Handling

All API endpoints return error messages in the following format:

```json
{
  "error": "Description of the error"
}
```

Common errors:
- `400`: Missing or invalid parameters
- `500`: Internal server error

Example error handling in Python:
```python
response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
    if result.get('success'):
        # Handle success
        pass
    else:
        print(f"Error: {result.get('error')}")
else:
    print(f"HTTP Error: {response.status_code}")
```

## Tips and Best Practices

1. **Coordinate Precision**: Use at least 4 decimal places for accuracy
2. **Safety Threshold**: Scores above 60 are generally considered safe
3. **Multiple Paths**: Always check alternative paths for better options
4. **Regular Updates**: Keep incident database updated for accuracy
5. **Time of Day**: Consider time when evaluating safety (not yet implemented)
6. **Emergency**: In real emergency, contact local authorities immediately

## Support

For issues, questions, or contributions:
- GitHub Issues: [Create an issue](https://github.com/n1s-chay/Aegis-Path/issues)
- Email: Contact repository maintainers

---

**Stay Safe with Aegis-Path!** 🛡️
