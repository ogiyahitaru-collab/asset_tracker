import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import datetime
import json

RSS_FEED_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"
OUTPUT_FILE = "../output/news.json"

def fetch_rss():
    response = requests.get(RSS_FEED_URL)
    response.raise_for_status()
    return response.content

def parse_rss(xml_data):
    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    articles = []
    for item in items[:5]:
        title = item.find("title").text
        link = item.find("link").text
        articles.append({"title": title, "url": link})
    return articles

def fetch_article_content(url):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.select("main p")
        content = "\n".join([p.get_text() for p in paragraphs])
        return content.strip()
    except Exception as e:
        print(f"❌ Error fetching article: {e}")
        return None

def save_to_json(data):
    now = datetime.datetime.now().isoformat()
    for entry in data:
        entry["fetched_at"] = now
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 保存完了: {OUTPUT_FILE}")

def main():
    print("🌐 BBC RSSを取得中...")
    xml_data = fetch_rss()
    articles = parse_rss(xml_data)
    results = []
    for i, article in enumerate(articles, 1):
        print(f"\n--- [{i}/{len(articles)}] {article['title']}")
        content = fetch_article_content(article["url"])
        results.append({
            "title": article["title"],
            "url": article["url"],
            "content_snippet": content[:200] if content else None
        })
    save_to_json(results)

if __name__ == "__main__":
    main()
