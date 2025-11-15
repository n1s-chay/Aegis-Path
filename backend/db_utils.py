from models.models_news import NewspaperArticle, ExtractedIncident, ArticleSource, db
from news_fetcher import fetch_article_html, extract_text_from_html, compute_content_hash
from ml_utils import call_llm_extract
from datetime import datetime
from incident_extractor import geocode_place
import json

# Database utility functions for articles, incidents, sources

def store_article(article_data):
    """Store a scraped article in the database, extract incidents, geocode locations, and save them."""
    url = article_data.get('url')
    if not url:
        raise ValueError("Missing article URL")
    # Fetch and extract article
    html = fetch_article_html(url)
    text = extract_text_from_html(html)
    title = article_data.get('title')
    author = article_data.get('author')
    published_at = article_data.get('published_at')
    content_hash = compute_content_hash(title, text)
    # Deduplication: check if article exists
    existing = NewspaperArticle.query.filter_by(content_hash=content_hash).first()
    if existing:
        return existing.id
    # Create and store article
    article = NewspaperArticle(
        url=url,
        title=title,
        author=author,
        published_at=published_at,
        raw_html=html,
        text=text,
        content_hash=content_hash,
        scraped_at=datetime.utcnow()
    )
    db.session.add(article)
    db.session.flush()  # Get article.id before commit
    # LLM extraction
    llm_result = call_llm_extract(text, title, url, published_at)
    if llm_result and llm_result.get('parsed'):
        for inc in llm_result['parsed'].get('incidents', []):
            lat, lng, confidence = None, None, None
            if inc.get('inferred_location'):
                geo = geocode_place(inc['inferred_location'])
                if geo:
                    lat = geo['lat']
                    lng = geo['lng']
                    confidence = 0.8
            incident = ExtractedIncident(
                article_id=article.id,
                description=inc.get('description'),
                incident_date=inc.get('incident_date'),
                incident_time=inc.get('incident_time'),
                location_name=inc.get('inferred_location'),
                latitude=lat,
                longitude=lng,
                location_confidence=confidence,
                location_source='llm',
                tags=','.join(inc.get('tags', [])),
                severity=inc.get('severity'),
                llm_raw=str(llm_result['raw_text']),
                inserted_at=datetime.utcnow(),
                provenance_url=url,
                provenance_source=title
            )
            db.session.add(incident)
    db.session.commit()
    return article.id


def get_articles(page=1, page_size=20):
    """Fetch a paginated list of articles."""
    pass


def get_article_by_id(article_id):
    """Fetch a single article by its ID."""
    pass


def store_incident(incident_data):
    """Store an incident in the database."""
    pass


def get_incidents(start_date=None, end_date=None, min_lat=None, max_lat=None, tag=None, severity=None):
    """Fetch incidents filtered by query params."""
    pass


def get_incident_by_id(incident_id):
    """Fetch a single incident by its ID."""
    pass


def get_sources():
    """Fetch all configured news sources."""
    pass


def save_article_and_incidents(url, title, text, html, source_name=None, published_at=None):
    h = compute_content_hash(title, text)
    existing = NewspaperArticle.query.filter_by(content_hash=h).first()
    if existing:
        return existing, False
    # create article
    art = NewspaperArticle(url=url, title=title, raw_html=html, text=text, content_hash=h, published_at=published_at)
    if source_name:
        src = ArticleSource.query.filter_by(name=source_name).first()
        if src:
            art.source_id = src.id
    db.session.add(art)
    db.session.commit()
    return art, True


def save_extracted_incident(article, incident_obj, llm_raw):
    # incident_obj matches LLM schema
    for inc in incident_obj.get("incidents", []):
        # If LLM returned coordinates, prefer them else geocode inferred_location
        coords = inc.get("approximate_coordinates", [])
        lat = None; lng = None; conf = None
        if coords:
            c = coords[0]
            lat = c.get("lat"); lng = c.get("lng"); conf = c.get("confidence", None)
        if not lat and inc.get("inferred_location"):
            g = geocode_place(inc["inferred_location"])
            if g:
                lat, lng, conf = g["lat"], g["lng"], 0.7
        ei = ExtractedIncident(
            article_id = article.id,
            description = inc.get("description"),
            incident_date = inc.get("incident_date"),
            incident_time = inc.get("incident_time"),
            location_name = inc.get("inferred_location"),
            latitude = lat,
            longitude = lng,
            location_confidence = conf,
            tags = ",".join(inc.get("tags",[])) if inc.get("tags") else None,
            severity = inc.get("severity"),
            llm_raw = json.dumps(incident_obj)
        )
        db.session.add(ei)
    db.session.commit()