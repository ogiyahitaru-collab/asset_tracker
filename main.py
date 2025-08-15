import os
import json
import requests
import feedparser
from datetime import datetime
from notion_client import Client
from openai import OpenAI
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_API_KEY")
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# クライアント初期化
notion = Client(auth=NOTION_TOKEN)
openai = OpenAI(api_key=OPENAI_API_KEY)

# 設定読み込み
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def fetch_articles(rss_url, max_items):
    feed = feedparser.parse(rss_url)
    return feed.entries[:max_items]

def summarize(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": "以下の英文記事を日本語で3行程度に要約してください。"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"要約エラー: {e}")
        return "（要約失敗）"

def post_to_notion(article, summary, source_name):
    try:
        notion.pages.create(
            parent={"database_id": NOTION_DB_ID},
            properties={
                "title": {
                    "title": [{"text": {"content": article["title"]}}]
                },
                "summary_ja": {
                    "rich_text": [{"text": {"content": summary}}]
                },
                "url": {
                    "url": article["link"]
                },
                "source": {
                    "select": {"name": source_name}
                },
                "date": {
                    "date": {"start": datetime.now().isoformat()}
                }
            }
        )
        print(f"✅ 登録完了: {article['title']}")
    except Exception as e:
        print(f"❌ Notion投稿エラー: {e}")

def main():
    for source in config["sources"]:
        articles = fetch_articles(source["rss"], config.get("max_articles_per_source", 5))
        for a in articles:
            text = a.get("title", "") + "\n\n" + a.get("summary", "")
            summary = summarize(text) if source["lang"] == "en" else a.get("summary", "")
            post_to_notion(a, summary, source["name"])

if __name__ == "__main__":
    main()
