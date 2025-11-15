from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to AegisPath backend!"})

@app.route('/api/safe-route', methods=['POST'])
def safe_route():
    data = request.json
    start = data.get('start') 
    end = data.get('end')
    
    routes = get_routes_from_osrm(start, end)
    scored_routes = []
    
    for route in routes:
        score = 80 + (20 * (1 if route["distance"] < 3000 else 0))  # example: higher score if shorter than 3km
        scored_routes.append({
            "geometry": route["geometry"],
            "safety_score": round(score, 1),
            "eta": int(route["duration"])  # seconds
        })
    
    return jsonify({"routes": scored_routes})

def get_routes_from_osrm(start, end):
    # OSRM Demo server URL
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coords = f"{start['lng']},{start['lat']};{end['lng']},{end['lat']}"
    params = {
        "alternatives": "true",
        "overview": "full",
        "geometries": "geojson"
    }
    url = base_url + coords
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return []
    
    data = response.json()
    routes = data.get('routes', [])
    
    # Extract relevant route info
    result = []
    for route in routes:
        result.append({
            "geometry": route["geometry"],
            "duration": route["duration"],
            "distance": route["distance"]
        })
    return result

if __name__ == '__main__':
    app.run(debug=True)
