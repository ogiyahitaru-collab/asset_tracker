import requests
import time
import random
import json
import datetime

URL_LIST_FILE = "urls.txt"
OUTPUT_FILE = "../output/news.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

session = requests.Session()
session.headers.update(HEADERS)

def fetch(url):
    try:
        print(f"▶️ 取得開始: {url}")
        res = session.get(url, timeout=10)
        res.raise_for_status()
        return res.text
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTPエラー: {e}")
    except Exception as e:
        print(f"❌ その他エラー: {e}")
    return None

def crawl():
    try:
        with open(URL_LIST_FILE, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ URLリストが見つかりません。")
        return

    results = []

    for i, url in enumerate(urls, start=1):
        print(f"\n--- [{i}/{len(urls)}] {url}")
        for attempt in range(1, 4):
            html = fetch(url)
            if html:
                results.append({
                    "url": url,
                    "fetched_at": datetime.datetime.now().isoformat(),
                    "content_snippet": html[:200]
                })
                break
            else:
                wait = random.randint(10, 30)
                print(f"⏳ リトライまで待機 {wait}s (attempt {attempt})")
                time.sleep(wait)
        else:
            print(f"❌ 最終失敗: {url}")
            results.append({
                "url": url,
                "fetched_at": datetime.datetime.now().isoformat(),
                "content_snippet": None
            })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 完了：{OUTPUT_FILE} に保存しました")

if __name__ == "__main__":
    crawl()
