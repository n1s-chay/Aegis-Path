from flask import Flask, request, jsonify
import requests, hashlib, json, sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
DB_PATH = "incidents.db"

def fetch_article_html(url, timeout=12):
    headers = {"User-Agent": "AegisPath-Scraper/1.0 (+your-email@example.com)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    article_tag = soup.find("article") or soup.find("div", {"class":"article-body"}) or soup
    text = article_tag.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[:5000])

def compute_content_hash(title, text):
    txt = (title or "") + "\n" + (text or "")
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()

def geocode_place(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{place_name}, Bangalore, Karnataka, India", "format":"json", "limit":1}
    headers = {"User-Agent":"AegisPath-Geocoder/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=8)
    if r.status_code == 200 and r.json():
        d = r.json()[0]
        return {"lat": float(d["lat"]), "lng": float(d["lon"]), "display_name": d.get("display_name")}
    return None

def call_llm_extract(article_text, title, url, published_at):
    # Replace with your actual Gemini/OpenAI endpoint and key
    url_api = "AIzaSyCgRE-Hppkq4uNoTMBhhtDEKmNdDZl5N9I"
    prompt = f"""ARTICLE_TITLE: {title}\nARTICLE_URL: {url}\nPUBLISHED_AT: {published_at}\n\nARTICLE_TEXT:\n{article_text}\n\n---\nYou are an assistant that extracts crime incidents from a news article. Input: the article text and metadata (title, url, published_at). Return a JSON object (only JSON; no extra commentary) with the key 'incidents': an array of objects. Each object must have: description, incident_date, incident_time, location_mentions, approximate_coordinates, inferred_location, tags, severity. If multiple incidents are described, return them separately. Only output valid JSON. Be conservative: if you are not sure about coordinates, return null for lat/lng but provide location_mentions."""
    payload = {
        "contents":[{"parts":[{"text":prompt}]}],
        "generationConfig": {"maxOutputTokens": 1500, "temperature":0}
    }
    resp = requests.post(url_api, json=payload, headers={"Content-Type":"application/json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts",[{}])[0].get("text","")
    try:
        parsed = json.loads(raw_text)
    except Exception:
        import re
        m = re.search(r'(\{[\s\S]*\})', raw_text)
        parsed = json.loads(m.group(1)) if m else None
    return {"raw_text": raw_text, "parsed": parsed, "raw_response": data}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        title TEXT,
        text TEXT,
        raw_html TEXT,
        content_hash TEXT,
        published_at TEXT,
        scraped_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id INTEGER,
        description TEXT,
        incident_date TEXT,
        incident_time TEXT,
        location_name TEXT,
        latitude REAL,
        longitude REAL,
        location_confidence REAL,
        tags TEXT,
        severity TEXT,
        llm_raw TEXT,
        inserted_at TEXT,
        FOREIGN KEY(article_id) REFERENCES articles(id)
    )''')
    conn.commit()
    conn.close()

@app.route("/api/ingest/article", methods=["POST"])
def ingest_article():
    data = request.get_json() or {}
    url = data.get("url")
    if not url:
        return jsonify({"success": False, "error": "url required"}), 400
    html = fetch_article_html(url)
    text = extract_text_from_html(html)
    title = (BeautifulSoup(html, "html.parser").title.string or "")[:500]
    content_hash = compute_content_hash(title, text)
    published_at = data.get("published_at")
    scraped_at = datetime.utcnow().isoformat()
    # Save article
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM articles WHERE content_hash=?", (content_hash,))
    row = c.fetchone()
    if row:
        article_id = row[0]
        created = False
    else:
        c.execute("INSERT INTO articles (url, title, text, raw_html, content_hash, published_at, scraped_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (url, title, text, html, content_hash, published_at, scraped_at))
        article_id = c.lastrowid
        created = True
    conn.commit()
    # LLM extraction
    lli = call_llm_extract(text, title, url, published_at)
    if not lli or not lli["parsed"]:
        conn.close()
        return jsonify({"success": False, "error": "LLM parse failed", "raw": lli.get("raw_text")}), 500
    # Save incidents
    for inc in lli["parsed"].get("incidents", []):
        lat, lng, conf = None, None, None
        if inc.get("inferred_location"):
            geo = geocode_place(inc["inferred_location"])
            if geo:
                lat, lng, conf = geo["lat"], geo["lng"], 0.8
        c.execute('''INSERT INTO incidents (article_id, description, incident_date, incident_time, location_name, latitude, longitude, location_confidence, tags, severity, llm_raw, inserted_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (article_id, inc.get("description"), inc.get("incident_date"), inc.get("incident_time"),
                   inc.get("inferred_location"), lat, lng, conf,
                   ",".join(inc.get("tags", [])), inc.get("severity"),
                   json.dumps(inc), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "article_id": article_id, "created": created}), 201

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
