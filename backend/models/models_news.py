from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ArticleSource(db.Model):
    __tablename__ = "article_sources"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)        # e.g., Times of India - Bangalore
    base_url = db.Column(db.String(500), nullable=True)
    rss_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NewspaperArticle(db.Model):
    __tablename__ = "newspaper_articles"
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("article_sources.id", ondelete="SET NULL"), nullable=True)
    url = db.Column(db.String(1000), unique=True, nullable=False, index=True)
    title = db.Column(db.String(800))
    author = db.Column(db.String(200))
    published_at = db.Column(db.DateTime, nullable=True, index=True)
    raw_html = db.Column(db.Text, nullable=True)
    text = db.Column(db.Text, nullable=True)
    content_hash = db.Column(db.String(64), index=True)  # fingerprint for dedupe
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)

    # one-to-many: multiple extracted incidents per article
    incidents = db.relationship("ExtractedIncident", backref="article", lazy=True, cascade="all, delete-orphan")

class ExtractedIncident(db.Model):
    __tablename__ = "extracted_incidents"
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("newspaper_articles.id", ondelete="CASCADE"), nullable=False, index=True)

    # extraction fields
    description = db.Column(db.Text, nullable=True)        # short excerpt/summary of the event
    incident_date = db.Column(db.Date, nullable=True, index=True)
    incident_time = db.Column(db.String(50), nullable=True)

    # location fields (LLM or geocode)
    location_name = db.Column(db.String(300), nullable=True, index=True)
    latitude = db.Column(db.Float, nullable=True, index=True)
    longitude = db.Column(db.Float, nullable=True, index=True)
    location_confidence = db.Column(db.Float, nullable=True)  # 0-1 score from LLM or heuristics
    location_source = db.Column(db.String(30), default="llm")  # 'llm'|'geocode'|'geotag'|'police'

    # classification / metadata
    tags = db.Column(db.String(400), nullable=True)    # csv tags like "assault,theft"
    severity = db.Column(db.String(50), nullable=True) # low/medium/high or police-level
    llm_raw = db.Column(db.Text, nullable=True)        # raw LLM JSON response for auditing
    inserted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    provenance_url = db.Column(db.String(1000), nullable=True)
    provenance_source = db.Column(db.String(150), nullable=True)
