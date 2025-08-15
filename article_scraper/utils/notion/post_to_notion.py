import os
import requests
from datetime import datetime

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def post_to_notion(title, url, summary, date_str, tag_name="重要"):
    """記事データをNotionに登録"""
    # 日付フォーマット（YYYY-MM-DD）
    try:
        start_date = datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
    except ValueError:
        start_date = datetime.today().date().isoformat()

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "title": {
                "title": [
                    {"text": {"content": title}}
                ]
            },
            "URL": {
                "url": url
            },
            "summary_ja": {
                "rich_text": [
                    {"text": {"content": summary}}
                ]
            },
            "日付": {
                "date": {"start": start_date}
            },
            "選択": {
                "select": {"name": tag_name}
            }
        }
    }

    res = requests.post(
        "https://api.notion.com/v1/pages",
        headers=HEADERS,
        json=payload
    )

    if res.status_code == 200:
        print(f"✅ Notion登録成功: {title}")
    else:
        print(f"❌ Notion登録失敗: {res.text}")
