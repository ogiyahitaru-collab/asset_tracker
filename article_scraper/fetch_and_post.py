#!/usr/bin/env python3
import os, sys, json, requests, feedparser
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if not NOTION_TOKEN or not DATABASE_ID:
    print("❌ NOTION_TOKEN または DATABASE_ID が設定されていません。.envを確認してください。")
    sys.exit(1)

def get_article_content(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    pub_time_meta = soup.find("meta", {"property": "article:published_time"})
    if pub_time_meta:
        utc_time = datetime.fromisoformat(pub_time_meta["content"].replace("Z", "+00:00"))
        jst_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    else:
        jst_time = datetime.now(timezone(timedelta(hours=9)))
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    return "\n".join(paragraphs), jst_time

def summarize_text(text):
    prompt = f"次の文章を短く要約してください（日本語と英語の両方）:\n{text[:3000]}"
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message["content"]
    except Exception as e:
        return f"要約失敗: {e}"

def post_to_notion(title, url, summary, pub_time, tags):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "タイトル": {"title": [{"text": {"content": title}}]},
            "URL": {"url": url},
            "公開日時": {"date": {"start": pub_time.isoformat()}},
            "要約": {"rich_text": [{"text": {"content": summary}}]},
            "タグ": {"multi_select": [{"name": t} for t in tags]}
        }
    }
    res = requests.post("https://api.notion.com/v1/pages", headers=headers, data=json.dumps(data))
    if res.status_code != 200:
        print(f"❌ Notion登録失敗: {res.text}")
    else:
        print(f"✅ Notion登録完了: {title}")

def main():
    if len(sys.argv) < 2:
        print("使い方: python3 fetch_and_post.py <検索キーワード>")
        sys.exit(1)
    keyword = sys.argv[1]
    encoded_kw = requests.utils.quote(keyword)
    rss_url = f"https://www.bing.com/news/search?q={encoded_kw}+site:reuters.com&format=rss"
    feed = feedparser.parse(rss_url)
    for e in feed.entries[:5]:
        print(f"📰 {e.title}")
        text, pub_time = get_article_content(e.link)
        summary = summarize_text(text)
        tags = []
        if "神戸製鋼" in keyword:
            tags.append("神戸製鋼所")
        if "JFE" in text:
            tags.append("JFE")
        tags.append("鉄鋼")
        post_to_notion(e.title, e.link, summary, pub_time, tags)

if __name__ == "__main__":
    main()
