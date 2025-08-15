import feedparser

RSS_URL = "https://www.nikkei.com/rss/newstopics/main.xml"

def fetch_latest_news(limit=5):
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries[:limit]

    news_list = []
    for entry in entries:
        news_list.append({
            "title": entry.title,
            "url": entry.link,
            "published": entry.published
        })
    return news_list

if __name__ == "__main__":
    news = fetch_latest_news()
    for i, article in enumerate(news, 1):
        print(f"[{i}] {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Published: {article['published']}")
        print("-" * 60)
