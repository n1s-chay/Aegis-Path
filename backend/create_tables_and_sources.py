from app import app
from models.models_news import db, ArticleSource

sources = [
    {
        "name": "Times of India - Bangalore",
        "base_url": "https://timesofindia.indiatimes.com/city/bangalore",
        "rss_url": "https://timesofindia.indiatimes.com/rssfeeds/-2128838597.cms"
    },
    {
        "name": "Deccan Herald - Bangalore",
        "base_url": "https://www.deccanherald.com/city/bengaluru",
        "rss_url": "https://www.deccanherald.com/rss/city/bengaluru"
    },
    {
        "name": "Bangalore Mirror",
        "base_url": "https://bangaloremirror.indiatimes.com/bangalore",
        "rss_url": "https://bangaloremirror.indiatimes.com/rssfeeds/3928802.cms"
    },
    {
        "name": "The Hindu - Bangalore",
        "base_url": "https://www.thehindu.com/news/cities/bangalore/",
        "rss_url": "https://www.thehindu.com/news/cities/bangalore/feeder/default.rss"
    },
    {
        "name": "News18 - Bangalore",
        "base_url": "https://www.news18.com/city/bangalore/",
        "rss_url": "https://www.news18.com/rss/city/bangalore.xml"
    }
]

with app.app_context():
    db.create_all()
    for src in sources:
        if not ArticleSource.query.filter_by(name=src["name"]).first():
            db.session.add(ArticleSource(**src))
    db.session.commit()
    print("DB tables created and sample ArticleSource entries added.")
