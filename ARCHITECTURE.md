# Aegis-Path Architecture Documentation

## System Overview

Aegis-Path is a women safety application that uses smart surveillance and machine learning to suggest the safest paths between two locations. The system integrates multiple data sources to provide comprehensive safety analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            index.html (Web Interface)                │   │
│  │  - Map visualization                                 │   │
│  │  - Path selection                                    │   │
│  │  - Safety scores display                            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                       API Layer                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              app.py (Flask Server)                   │   │
│  │  - /api/path/safe                                    │   │
│  │  - /api/path/alternatives                            │   │
│  │  - /api/safety/location                              │   │
│  │  - /api/camera/analyze                               │   │
│  │  - /api/incidents                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Camera     │ │   Safety     │ │   Incident   │
│   Analyzer   │ │   Engine     │ │   Manager    │
│              │ │              │ │              │
│ OpenCV-based │ │ Combines all │ │ Police       │
│ analysis:    │ │ safety       │ │ reports      │
│ - Lighting   │ │ factors      │ │ database     │
│ - Crowding   │ └──────────────┘ └──────────────┘
└──────────────┘
        │
        ↓
┌──────────────┐
│  PathFinder  │
│              │
│ Calculates   │
│ safe routes  │
│ using safety │
│ scores       │
└──────────────┘
```

## Component Details

### 1. Frontend (index.html)
- **Purpose**: User interface for path finding
- **Technology**: HTML, CSS, JavaScript
- **Features**:
  - Interactive coordinate input
  - Path visualization
  - Safety score display
  - Alternative route comparison

### 2. API Layer (app.py)
- **Purpose**: REST API server
- **Technology**: Flask, Flask-CORS
- **Key Endpoints**:
  - `POST /api/path/safe`: Find safest path
  - `POST /api/path/alternatives`: Find multiple paths
  - `POST /api/safety/location`: Check location safety
  - `POST /api/camera/analyze`: Analyze camera feed
  - `GET/POST /api/incidents`: Manage incidents

### 3. Camera Analyzer (camera_analyzer.py)
- **Purpose**: Analyze camera feeds for safety metrics
- **Technology**: OpenCV, NumPy
- **Analysis**:
  - **Lighting Detection**: 
    - Calculates mean brightness
    - Measures contrast (standard deviation)
    - Scores: 0-100 (higher = better lit)
  - **Crowd Density Detection**:
    - Uses Haar Cascade for face detection
    - Calculates people per frame area
    - Scores: 0-100 (higher = more crowded)

### 4. Incident Manager (incident_manager.py)
- **Purpose**: Store and analyze police incident reports
- **Data Structure**:
  ```python
  {
    "incident_id": str,
    "location": (lat, lng),
    "incident_type": str,
    "severity": int (1-5),
    "timestamp": datetime
  }
  ```
- **Features**:
  - Proximity search with radius
  - Time-based filtering
  - Weighted safety scoring

### 5. Safety Engine (safety_engine.py)
- **Purpose**: Combine all safety factors
- **Algorithm**:
  ```
  Safety Score = (Incident Score × 0.3) +
                 (Lighting Score × 0.4) +
                 (Crowd Safety × 0.3)
  ```
- **Output**: Comprehensive safety rating (0-100)

### 6. PathFinder (pathfinder.py)
- **Purpose**: Find optimal safe routes
- **Algorithm**:
  1. Generate candidate paths
  2. Divide paths into segments
  3. Calculate safety for each segment
  4. Aggregate segment scores
  5. Rank paths by safety
- **Features**:
  - Multiple alternative paths
  - Distance calculation
  - Safety threshold filtering

## Data Flow

### Finding a Safe Path

```
User Input (Start, End)
       ↓
    API Server
       ↓
   PathFinder
       ↓
[Generate Waypoints]
       ↓
   Safety Engine ←─┬─ Camera Analyzer
       ↓           └─ Incident Manager
[Calculate Scores]
       ↓
   [Rank Paths]
       ↓
  Return to User
```

### Safety Score Calculation

```
Location (lat, lng)
       ↓
   ┌───┴───┐
   ↓       ↓
Incident  Camera
Manager   Analyzer
   ↓       ↓
[Score]  [Score]
   └───┬───┘
       ↓
 Safety Engine
       ↓
[Weighted Sum]
       ↓
Overall Safety Score
```

## Configuration

All configurable parameters are in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MIN_LIGHTING_SCORE` | 40 | Minimum acceptable lighting (0-100) |
| `MAX_CROWD_DENSITY` | 80 | Maximum acceptable crowd density (0-100) |
| `INCIDENT_WEIGHT` | 0.3 | Weight for incident history in safety score |
| `LIGHTING_WEIGHT` | 0.4 | Weight for lighting conditions |
| `CROWD_WEIGHT` | 0.3 | Weight for crowd density |
| `SAFETY_THRESHOLD` | 60 | Minimum safety score for a path |
| `MAX_ALTERNATIVE_PATHS` | 3 | Number of alternative paths to generate |

## Safety Scoring Algorithm

### Incident Score
- Based on past incidents within radius
- Factors:
  - **Recency**: Recent incidents weighted higher
  - **Severity**: 1-5 scale
  - **Proximity**: Distance from location
- Formula: `100 - (weighted_incidents / 5) × 100`

### Lighting Score
- Based on camera image analysis
- Factors:
  - **Brightness**: Mean pixel intensity
  - **Contrast**: Standard deviation of pixels
- Formula: `(brightness_score × 0.7) + (contrast_score × 0.3)`

### Crowd Safety Score
- Inverted crowd density (lower density = safer)
- Based on people count in camera frame
- Formula: `100 - crowd_density_score`

### Overall Safety Score
```python
overall_safety = (
    incident_score * 0.3 +
    lighting_score * 0.4 +
    crowd_safety_score * 0.3
)
```

## Database Schema

### Incidents (incidents.json)
```json
[
  {
    "incident_id": "INC-YYYYMMDDHHMMSS",
    "location": {
      "lat": 12.9716,
      "lng": 77.5946
    },
    "incident_type": "theft|harassment|assault|...",
    "severity": 1-5,
    "timestamp": "ISO-8601 datetime"
  }
]
```

## API Response Examples

### Safe Path Response
```json
{
  "success": true,
  "path": {
    "waypoints": [[lat1, lng1], [lat2, lng2], ...],
    "safety_score": 75.5,
    "is_safe": true,
    "distance_km": 5.2,
    "segments": [...]
  }
}
```

### Location Safety Response
```json
{
  "success": true,
  "location": {"lat": 12.9716, "lng": 77.5946},
  "safety": {
    "overall_safety": 75.5,
    "incident_score": 85.0,
    "lighting_score": 70.0,
    "crowd_density": 40.0,
    "crowd_safety_score": 60.0
  }
}
```

## Performance Considerations

1. **Camera Analysis**: 
   - Processes single frame per request
   - ~100-200ms per analysis
   - Can be cached for repeated queries

2. **Incident Queries**:
   - In-memory storage for fast access
   - O(n) search complexity
   - Consider database for large datasets

3. **Path Calculation**:
   - Simplified waypoint generation
   - ~50-100ms per path
   - Linear complexity with waypoints

## Security Considerations

1. **Input Validation**: All coordinates validated
2. **CORS**: Configured for cross-origin requests
3. **No Authentication**: Add auth for production
4. **Rate Limiting**: Not implemented (add for production)
5. **Data Privacy**: Incident data should be anonymized

## Future Enhancements

1. **Real-time GPS tracking**
2. **Mobile apps (iOS/Android)**
3. **Live camera feed integration**
4. **ML-based incident prediction**
5. **Integration with Google Maps / OpenStreetMap**
6. **Emergency SOS button**
7. **User community reporting**
8. **Real-time traffic integration**
9. **Weather-based safety adjustments**
10. **Historical route analysis**

## Deployment

### Development
```bash
python3 app.py
# Or use the startup script
./start.sh
```

### Production
- Use production WSGI server (gunicorn, uWSGI)
- Set up reverse proxy (nginx)
- Configure SSL/TLS
- Set up proper database
- Implement authentication
- Enable monitoring and logging

## Testing

Run the test suite:
```bash
python3 test_aegis.py
```

Tests cover:
- Incident management
- Camera analysis
- Safety engine
- Path finding
- API endpoints (manual testing)

## Dependencies

- **Flask**: Web framework
- **Flask-CORS**: CORS support
- **OpenCV**: Image analysis
- **NumPy**: Numerical operations
- **Requests**: HTTP client (future use)

## License

MIT License - See LICENSE file for details
