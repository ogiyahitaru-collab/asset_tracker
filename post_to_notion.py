import os
from notion_client import Client
from datetime import datetime
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# Notion APIクライアント初期化
notion = Client(auth=os.getenv("NOTION_API_KEY"))
database_id = os.getenv("NOTION_DATABASE_ID")

# 登録するデータ（1件テスト用）
page_data = {
    "title": {
        "title": [
            {
                "text": {
                    "content": "テスト記事タイトル"
                }
            }
        ]
    },
    "summary_ja": {
        "rich_text": [
            {
                "text": {
                    "content": "これは要約文のテストです。"
                }
            }
        ]
    },
    "URL": {
        "url": "https://example.com/news123"
    },
    "選択": {
        "select": {
            "name": "重要"
        }
    },
    "日付": {
        "date": {
            "start": datetime.now().isoformat()
        }
    }
}

# 実行処理（Notionにページ作成）
try:
    response = notion.pages.create(
        parent={"database_id": database_id},
        properties=page_data
    )
    print("✅ Notionへ登録成功")
    print("ページURL:", response.get("url", "URL不明"))
except Exception as e:
    print("❌ 登録エラー:", e)
