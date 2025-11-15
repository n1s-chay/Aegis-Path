from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import sqlite3
from geopy.distance import geodesic

app = Flask(__name__)
CORS(app)

def get_all_incidents():
    try:
        conn = sqlite3.connect('incidents.db')
        c = conn.cursor()
        c.execute('SELECT lat, lng, description FROM incidents')
        rows = c.fetchall()
        conn.close()
        return [{'lat': r[0], 'lng': r[1], 'description': r[2]} for r in rows]
    except Exception as e:
        app.logger.error(f"DB error: {e}")
        return []

def route_intersects_incidents(route_coords, incidents, threshold_m=200):
    for point in route_coords:
        for inc in incidents:
            if geodesic((point[1], point[0]), (inc['lat'], inc['lng'])).meters < threshold_m:
                return True
    return False

def validate_coord(coord):
    if not isinstance(coord, dict):
        return False
    if 'lat' not in coord or 'lng' not in coord:
        return False
    try:
        lat = float(coord['lat'])
        lng = float(coord['lng'])
        # Optional: add lat/lng range checks here
        return True
    except (ValueError, TypeError):
        return False

@app.route('/')
def index():
    return jsonify({"message": "Welcome to AegisPath backend!"})

@app.route('/api/safe-route', methods=['POST'])
def safe_route():
    data = request.json
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    start = data.get('start')
    end = data.get('end')

    if not validate_coord(start) or not validate_coord(end):
        return jsonify({"error": "Invalid or missing start/end coordinates"}), 400

    incidents = get_all_incidents()
    routes = get_routes_from_osrm(start, end)

    if not routes:
        return jsonify({"error": "No routes found from routing engine"}), 404

    safest_route = None
    for route in routes:
        if not route_intersects_incidents(route['geometry']['coordinates'], incidents):
            safest_route = route
            break
    if safest_route is None:
        safest_route = routes[0]

    return jsonify({"routes": [safest_route]})

def get_routes_from_osrm(start, end):
    base_url = "http://router.project-osrm.org/route/v1/driving/"
    coords = f"{start['lng']},{start['lat']};{end['lng']},{end['lat']}"
    params = {
        "alternatives": "true",
        "overview": "full",
        "geometries": "geojson"
    }
    try:
        url = base_url + coords
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        routes = data.get('routes', [])
        result = []
        for route in routes:
            result.append({
                "geometry": route["geometry"],
                "duration": route["duration"],
                "distance": route["distance"]
            })
        return result
    except requests.RequestException as e:
        app.logger.error(f"OSRM request failed: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True)
