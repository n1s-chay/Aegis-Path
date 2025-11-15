from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import sqlite3
from geopy.distance import geodesic
from .db_utils import insert_incident, query_incidents, initialize_db
from models.models_news import db
from news_fetcher import fetch_article_html, extract_text_from_html
from bs4 import BeautifulSoup
from .ml_utils import call_llm_extract
from ingest import ingest_bp  # Import the ingest blueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db.init_app(app)
app.register_blueprint(ingest_bp)  # Register the ingest blueprint

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
    start_name = data.get('start')
    end_name = data.get('end')
    start_coords = geocode_address(start_name)
    end_coords = geocode_address(end_name)
    if not start_coords or not end_coords:
        return jsonify({"error": "Location not found"}), 400

    routes = get_routes_from_osrm(
        {'lat': start_coords[0], 'lng': start_coords[1]},
        {'lat': end_coords[0], 'lng': end_coords[1]}
    )
    if not routes:
        return jsonify({"error": "No route found"}), 404

    coords_lnglat = routes[0]["geometry"]["coordinates"]
    return jsonify({"route": coords_lnglat})


@app.route('/api/incidents')
def get_incidents_route():
    incidents = get_all_incidents()
    return jsonify(incidents)

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
        # The following line gets the 'routes' from OSRM response, but FALLS BACK to []
        routes = data.get('routes', [])
        result = []
        for route in routes:
            coords_lnglat = route["geometry"]["coordinates"]  # [lng, lat]
            coords_latlng = [[lat, lng] for lng, lat in coords_lnglat]
            result.append({
                "geometry": {"coordinates": coords_latlng},
                "duration": route["duration"],
                "distance": route["distance"]
            })
        return result
    except requests.RequestException as e:
        app.logger.error(f"OSRM request failed: {e}")
        return []


# --- Ingest Endpoints ---
@app.route('/api/ingest/fetch-rss', methods=['POST'])
def ingest_rss():
    data = request.json
    source_id = data.get('source_id')
    # TODO: Fetch RSS items, ingest each
    return jsonify({'message': 'RSS items ingested'}), 201

@app.route('/api/ingest/bulk', methods=['POST'])
def ingest_bulk():
    data = request.json
    urls = data.get('urls', [])
    # TODO: Ingest each URL
    return jsonify({'message': f'Bulk ingested {len(urls)} URLs'}), 201

# --- Incident Endpoints ---
@app.route('/api/incidents', methods=['GET'])
def api_get_incidents():
    args = request.args
    incidents = get_incidents(
        start_date=args.get('start_date'),
        end_date=args.get('end_date'),
        min_lat=args.get('min_lat'),
        max_lat=args.get('max_lat'),
        tag=args.get('tag'),
        severity=args.get('severity')
    )
    return jsonify(incidents)

@app.route('/api/incidents/<int:incident_id>', methods=['GET'])
def api_get_incident_detail(incident_id):
    incident = get_incident_by_id(incident_id)
    # TODO: Add source url + llm_raw if auth
    return jsonify(incident)

# --- Article Endpoints ---
@app.route('/api/articles', methods=['GET'])
def api_get_articles():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    articles = get_articles(page, page_size)
    return jsonify(articles)

# --- Sources Endpoint ---
@app.route('/api/sources', methods=['GET'])
def api_get_sources():
    sources = get_sources()
    return jsonify(sources)

# --- LLM Extract Endpoint ---
@app.route('/api/llm/extract', methods=['POST'])
def llm_extract():
    data = request.json
    text = data.get('text')
    # TODO: Run LLM extraction and return JSON
    llm_result = {}  # Fill with LLM output
    return jsonify(llm_result)

@app.route("/api/ingest/article", methods=["POST"])
def ingest_article():
    data = request.get_json() or {}
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "url required"}), 400
    html = fetch_article_html(url)
    text = extract_text_from_html(html)
    title = (BeautifulSoup(html, "html.parser").title.string or "")[:500]
    article, created = save_article_and_incidents(url, title, text, html, published_at=data.get("published_at"))
    # call llm
    lli = call_llm_extract(text, title, url, data.get("published_at"))
    if not lli:
        return jsonify({"success": False, "error": "LLM not configured"}), 500
    parsed = lli["parsed"]
    if parsed:
        save_extracted_incident(article, parsed, lli["raw_response"])
        return jsonify({"success": True, "article_id": article.id, "created": created}), 201
    else:
        return jsonify({"success": False, "error": "LLM parse failed", "raw": lli["raw_text"]}), 500

if __name__ == '__main__':
    app.run(debug=True)
