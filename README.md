# Aegis-Path 🛡️

A women safety application that uses smart surveillance to suggest safe paths from point A to B on a map.

## Features

- **🎥 Smart Surveillance**: Integrates with traffic cameras using OpenCV to analyze:
  - Lighting conditions (brightness and contrast)
  - Crowd density (number of people in area)
  
- **🚨 Police Incident Reports**: Considers past incidents on roads including:
  - Historical crime data
  - Incident severity and recency
  - Proximity-based safety scoring

- **🗺️ Safe Path Finding**: Intelligent pathfinding that:
  - Calculates safety scores for routes
  - Suggests multiple alternative paths
  - Provides real-time safety analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/n1s-chay/Aegis-Path.git
cd Aegis-Path
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The API server will start at `http://localhost:5000`

4. Open the web interface:
Open `index.html` in your web browser to access the user interface.

## Usage

### Web Interface

1. Open `index.html` in your browser
2. Enter starting location (latitude, longitude)
3. Enter destination (latitude, longitude)
4. Click "Find Safest Path" or "Show Alternative Paths"
5. View safety scores and recommended routes

### API Endpoints

#### Find Safe Path
```bash
POST /api/path/safe
Content-Type: application/json

{
  "start": {"lat": 12.9716, "lng": 77.5946},
  "end": {"lat": 12.9352, "lng": 77.6245}
}
```

#### Find Alternative Paths
```bash
POST /api/path/alternatives
Content-Type: application/json

{
  "start": {"lat": 12.9716, "lng": 77.5946},
  "end": {"lat": 12.9352, "lng": 77.6245},
  "num_alternatives": 3
}
```

#### Check Location Safety
```bash
POST /api/safety/location
Content-Type: application/json

{
  "location": {"lat": 12.9716, "lng": 77.5946}
}
```

#### Analyze Camera Feed
```bash
POST /api/camera/analyze
Content-Type: application/json

{
  "image_path": "/path/to/image.jpg"
}
```

#### Get Incidents Near Location
```bash
GET /api/incidents?lat=12.9716&lng=77.5946&radius=1.0
```

#### Add Incident Report
```bash
POST /api/incidents
Content-Type: application/json

{
  "location": {"lat": 12.9716, "lng": 77.5946},
  "incident_type": "theft",
  "severity": 3,
  "timestamp": "2025-11-15T10:30:00"
}
```

## Configuration

Edit `config.py` to customize:

- Safety thresholds
- Weighting factors for safety calculations
- Camera feed URLs
- API server settings

### Key Configuration Parameters

```python
MIN_LIGHTING_SCORE = 40      # Minimum acceptable lighting (0-100)
MAX_CROWD_DENSITY = 80       # Maximum acceptable crowd density (0-100)
INCIDENT_WEIGHT = 0.3        # Weight for incident history
LIGHTING_WEIGHT = 0.4        # Weight for lighting conditions
CROWD_WEIGHT = 0.3           # Weight for crowd density
SAFETY_THRESHOLD = 60        # Minimum safety score for a path
```

## Architecture

### Components

1. **Camera Analyzer** (`camera_analyzer.py`)
   - Uses OpenCV for image analysis
   - Analyzes lighting conditions
   - Detects crowd density

2. **Incident Manager** (`incident_manager.py`)
   - Stores and retrieves police reports
   - Calculates incident-based safety scores
   - Manages historical data

3. **Safety Engine** (`safety_engine.py`)
   - Combines all safety factors
   - Calculates comprehensive safety scores
   - Evaluates path segments

4. **Path Finder** (`pathfinder.py`)
   - Finds optimal safe routes
   - Generates alternative paths
   - Calculates distances

5. **API Server** (`app.py`)
   - Flask REST API
   - CORS enabled for web access
   - JSON request/response

## Safety Scoring Algorithm

The safety score (0-100) for each location is calculated as:

```
Safety Score = (Incident Score × 0.3) + (Lighting Score × 0.4) + (Crowd Safety × 0.3)
```

Where:
- **Incident Score**: Based on proximity and recency of past incidents
- **Lighting Score**: Brightness and contrast analysis from camera feeds
- **Crowd Safety**: Inverted crowd density (lower density = safer)

## Example Usage

### Python API Example

```python
from pathfinder import PathFinder

# Initialize
finder = PathFinder()

# Find safe path
start = (12.9716, 77.5946)
end = (12.9352, 77.6245)
path = finder.find_safe_path(start, end)

print(f"Safety Score: {path['safety_score']}")
print(f"Distance: {path['distance_km']} km")
print(f"Is Safe: {path['is_safe']}")
```

### JavaScript Fetch Example

```javascript
const response = await fetch('http://localhost:5000/api/path/safe', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    start: { lat: 12.9716, lng: 77.5946 },
    end: { lat: 12.9352, lng: 77.6245 }
  })
});

const data = await response.json();
console.log(data.path);
```

## Future Enhancements

- Real-time GPS integration
- Mobile application (iOS/Android)
- Live camera feed integration
- Emergency alert system
- User community reporting
- Machine learning for incident prediction
- Integration with actual road networks and maps
- Real-time traffic data integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

---

**Aegis-Path** - Making every journey safer 🛡️