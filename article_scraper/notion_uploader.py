from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=(Path(__file__).resolve().parent/".env"), override=True)
from dotenv import load_dotenv
load_dotenv(override=True)
import requests
import os
from datetime import datetime

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def create_notion_page(title, summary_ja, url):
    new_page = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            },
            "summary_ja": {
                "rich_text": [{"text": {"content": summary_ja}}]
            },
            "URL": {
                "url": url
            },
            "選択": {
                "select": {"name": "重要"}
            },
            "日付": {
                "date": {"start": datetime.now().isoformat()}
            }
        }
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        },
        json=new_page
    )

    if response.status_code == 200:
        print("✅ Notionに正常に保存されました")
    else:
        print(f"❌ Notion保存失敗: {response.status_code} - {response.text}")

# --- 実行テスト用 ---
if __name__ == "__main__":
    create_notion_page(
        title="テスト記事",
        summary_ja="これはテスト要約です",
        url="https://example.com"
    )
