import requests
from dotenv import load_dotenv
import os

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
