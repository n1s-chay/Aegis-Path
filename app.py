"""
Aegis-Path API Server
Provides REST API for safe path finding
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from config import Config
from pathfinder import PathFinder
from camera_analyzer import CameraAnalyzer
from incident_manager import IncidentManager, IncidentReport
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize components
path_finder = PathFinder(Config())
camera_analyzer = CameraAnalyzer()
incident_manager = IncidentManager()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Aegis-Path'}), 200


@app.route('/api/path/safe', methods=['POST'])
def find_safe_path():
    """
    Find safest path between two points
    
    Request body:
    {
        "start": {"lat": 12.9716, "lng": 77.5946},
        "end": {"lat": 12.9352, "lng": 77.6245}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({'error': 'Missing start or end location'}), 400
        
        start = (data['start']['lat'], data['start']['lng'])
        end = (data['end']['lat'], data['end']['lng'])
        
        # Find safe path
        path = path_finder.find_safe_path(start, end)
        
        return jsonify({
            'success': True,
            'path': path
        }), 200
    
    except Exception as e:
        logger.error(f"Error finding safe path: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/path/alternatives', methods=['POST'])
def find_alternative_paths():
    """
    Find multiple alternative paths
    
    Request body:
    {
        "start": {"lat": 12.9716, "lng": 77.5946},
        "end": {"lat": 12.9352, "lng": 77.6245},
        "num_alternatives": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'start' not in data or 'end' not in data:
            return jsonify({'error': 'Missing start or end location'}), 400
        
        start = (data['start']['lat'], data['start']['lng'])
        end = (data['end']['lat'], data['end']['lng'])
        num_alternatives = data.get('num_alternatives', 3)
        
        # Find alternative paths
        paths = path_finder.find_alternative_paths(start, end, num_alternatives)
        
        return jsonify({
            'success': True,
            'paths': paths
        }), 200
    
    except Exception as e:
        logger.error(f"Error finding alternative paths: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/safety/location', methods=['POST'])
def check_location_safety():
    """
    Check safety score for a specific location
    
    Request body:
    {
        "location": {"lat": 12.9716, "lng": 77.5946}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'location' not in data:
            return jsonify({'error': 'Missing location'}), 400
        
        location = (data['location']['lat'], data['location']['lng'])
        
        # Calculate safety
        safety_data = path_finder.safety_engine.calculate_location_safety(location)
        
        return jsonify({
            'success': True,
            'location': data['location'],
            'safety': safety_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error checking location safety: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/camera/analyze', methods=['POST'])
def analyze_camera():
    """
    Analyze camera feed or image
    
    Request body:
    {
        "image_path": "/path/to/image.jpg"
    }
    or
    {
        "camera_url": "http://camera-feed-url"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Missing request body'}), 400
        
        if 'image_path' in data:
            analysis = camera_analyzer.analyze_image_file(data['image_path'])
        elif 'camera_url' in data:
            analysis = camera_analyzer.analyze_camera_feed(data['camera_url'])
        else:
            return jsonify({'error': 'Missing image_path or camera_url'}), 400
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    
    except Exception as e:
        logger.error(f"Error analyzing camera: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """
    Get incidents near a location
    
    Query params:
    - lat: latitude
    - lng: longitude
    - radius: radius in km (default: 1.0)
    """
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', type=float, default=1.0)
        
        if lat is None or lng is None:
            return jsonify({'error': 'Missing lat or lng parameter'}), 400
        
        location = (lat, lng)
        incidents = incident_manager.get_incidents_near_location(location, radius)
        
        return jsonify({
            'success': True,
            'incidents': [inc.to_dict() for inc in incidents]
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting incidents: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/incidents', methods=['POST'])
def add_incident():
    """
    Add a new incident report
    
    Request body:
    {
        "location": {"lat": 12.9716, "lng": 77.5946},
        "incident_type": "theft",
        "severity": 3,
        "timestamp": "2025-11-15T10:30:00"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'location' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Generate incident ID
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        location = (data['location']['lat'], data['location']['lng'])
        incident_type = data.get('incident_type', 'unknown')
        severity = data.get('severity', 3)
        
        # Parse timestamp
        timestamp_str = data.get('timestamp')
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str)
        else:
            timestamp = datetime.now()
        
        # Create and add incident
        incident = IncidentReport(
            incident_id=incident_id,
            location=location,
            incident_type=incident_type,
            severity=severity,
            timestamp=timestamp
        )
        
        incident_manager.add_incident(incident)
        
        return jsonify({
            'success': True,
            'incident': incident.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error adding incident: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        'service': 'Aegis-Path API',
        'version': '1.0.0',
        'description': 'Women safety app with smart surveillance for safe path suggestions',
        'endpoints': {
            'GET /health': 'Health check',
            'POST /api/path/safe': 'Find safest path between two points',
            'POST /api/path/alternatives': 'Find multiple alternative paths',
            'POST /api/safety/location': 'Check safety score for a location',
            'POST /api/camera/analyze': 'Analyze camera feed or image',
            'GET /api/incidents': 'Get incidents near a location',
            'POST /api/incidents': 'Add a new incident report'
        }
    }), 200


if __name__ == '__main__':
    logger.info("Starting Aegis-Path API Server")
    app.run(
        host=app.config['API_HOST'],
        port=app.config['API_PORT'],
        debug=app.config['DEBUG']
    )
