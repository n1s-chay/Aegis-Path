import requests
from dotenv import load_dotenv
import os
import requests, hashlib
from bs4 import BeautifulSoup
from datetime import datetime

load_dotenv()  # Loads variables from .env

newsapi_key = os.getenv("NEWSAPI_KEY")


API_KEY = newsapi_key
BASE_URL = 'https://newsapi.org/v2/everything'

def fetch_news(query, page=1, page_size=10):
    params = {
        'apiKey': API_KEY,
        'q': query,
        'language': 'en',
        'sortBy': 'publishedAt',
        'page': page,
        'pageSize': page_size
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        articles = data.get('articles')
        return articles
    else:
        print(f"Error fetching news: {response.status_code} - {response.text}")
        return []

def fetch_article_html(url, timeout=12):
    headers = {"User-Agent": "AegisPath-Scraper/1.0 (+your-email@example.com)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.text

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    # Remove scripts and styles
    for tag in soup(["script","style","noscript"]):
        tag.decompose()
    # Typical article content containers may be <article>, <div class="content"> etc.
    article_tag = soup.find("article") or soup.find("div", {"class":"article-body"}) or soup
    text = article_tag.get_text(separator="\n")
    # clean blanks
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines[:5000])  # limit size

def compute_content_hash(title, text):
    txt = (title or "") + "\n" + (text or "")
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()

if __name__ == '__main__':
    query = 'crime OR incident OR accident'
    articles = fetch_news(query)
    for i, article in enumerate(articles):
        print(f"{i+1}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Published At: {article['publishedAt']}")
        print(f"   URL: {article['url']}")
        print(f"   Description: {article['description']}")
        print("\n")
