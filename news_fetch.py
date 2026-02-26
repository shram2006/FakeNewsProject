# news_fetch.py
import requests
import random

def fetch_news(api_key, query="politics OR business OR technology OR world", max_articles=50):
    url = "https://newsapi.org/v2/everything"

    params = {
        "apiKey": api_key,
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100   # MAX allowed by NewsAPI
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("NewsAPI error:", response.text)
        return []

    data = response.json()

    articles = []
    for a in data.get("articles", []):
        if a.get("title") and a.get("url"):
            articles.append({
                "title": a["title"],
                "description": a.get("description", ""),
                "url": a["url"]
            })

    # 🔁 Shuffle every time → different news on refresh
    random.shuffle(articles)

    # Return 50 or 100 articles
    return articles[:max_articles]