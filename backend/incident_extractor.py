from openai import OpenAI
import requests
import sqlite3
import os
import json

openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

def extract_locations_from_article(article_text):
    prompt = (
        "Extract and return a JSON list of location names mentioned in "
        "this news article. Only list names of cities, neighborhoods, roads or landmarks.\n"
        f"Article: '''{article_text}'''"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    content = response.choices[0].message.content
    try:
        locations = json.loads(content)
    except json.JSONDecodeError:
        print("Warning: Could not parse JSON from LLM response, using raw text instead.")
        locations = []
    return locations

def extract_locations_from_article(article_text):
    # Mocked response for testing quota issues
    return ["MG Road, Bangalore", "Brigade Road, Bangalore"]


def geocode_location(location_name):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={location_name}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    results = r.json()
    if results:
        return float(results[0]['lat']), float(results[0]['lon'])
    return None, None

def geocode_place(place_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"{place_name}, Bangalore, Karnataka, India", "format":"json", "limit":1}
    headers = {"User-Agent":"AegisPath-Geocoder/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=8)
    if r.status_code == 200 and r.json():
        d = r.json()[0]
        return {"lat": float(d["lat"]), "lng": float(d["lon"]), "display_name": d.get("display_name")}
    return None


def create_incidents_table():
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_incident_to_db(lat, lng, description):
    conn = sqlite3.connect('incidents.db')
    c = conn.cursor()
    c.execute("INSERT INTO incidents (lat, lng, description) VALUES (?, ?, ?)", (lat, lng, description))
    conn.commit()
    conn.close()

def main():
    news_articles = [
        "Last night a robbery was reported near MG Road in Bangalore.",
        "A mugging incident occurred at Brigade Road, causing concern.",
    ]

    create_incidents_table()

    for article in news_articles:
        print(f"Extracting locations from article: {article}")
        locations = extract_locations_from_article(article)
        if not isinstance(locations, list):
            print("Warning: Extracted locations not a list, got:", locations)
            continue

        for loc in locations:
            lat, lng = geocode_location(loc)
            if lat and lng:
                print(f"Geocoded '{loc}' to ({lat}, {lng}), saving to DB.")
                add_incident_to_db(lat, lng, f"Incident near {loc}")
            else:
                print(f"Could not geocode location: {loc}")

if __name__ == "__main__":
    main()
