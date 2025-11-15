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
    
def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "YourApp/1.0"}
    r = requests.get(url, params=params, headers=headers)
    data = r.json()
    # Return (lat, lng) as float if found
    if data:
        return float(data[0]['lat']), float(data[0]['lon'])
    else:
        return None

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

@app.route('/api/route', methods=['POST'])
def get_route():
    data = request.json
    start_name = data['start']
    end_name = data['end']
    start_coords = geocode_address(start_name)
    end_coords = geocode_address(end_name)
    if not start_coords or not end_coords:
        return jsonify({"error": "Location not found"}), 400
    routes = get_routes_from_osrm(
        {'lat': start_coords[0], 'lng': start_coords[1]},
        {'lat': end_coords[0], 'lng': end_coords[1]})
    if not routes:
        return jsonify({"error": "No route found"}), 404
    # Return only the first route's coordinates
    return jsonify({"route": routes[0]["geometry"]["coordinates"]})

@app.route('/api/incidents')
def get_incidents_route():
    incidents = get_all_incidents()
    return jsonify(incidents)

def get_routes_from_osrm(start, end):
    # existing code...
    result = []
    for route in routes:
        coords_lnglat = route["geometry"]["coordinates"]  # list of [lng, lat]
        coords_latlng = [[lat, lng] for lng, lat in coords_lnglat]  # convert for frontend
        result.append({
            "geometry": {
                "coordinates": coords_latlng
            },
            "duration": route["duration"],
            "distance": route["distance"]
        })
    return result

if __name__ == '__main__':
    app.run(debug=True)
