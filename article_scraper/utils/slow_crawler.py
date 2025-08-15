import os, time, json, random, pathlib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ===== 基本設定 =====
MIN_DELAY = 20       # 最小待機秒（各リクエスト間）
MAX_DELAY = 45       # 最大待機秒（各リクエスト間）
HARD_BACKOFF_4XX = (120, 300)  # 4xx系の時にまとめて待つ秒（min,max）
MAX_RETRIES = 3
TIMEOUT = 30

USER_AGENTS = [
    # PCブラウザっぽいUAを数種ランダムに
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
]

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Connection": "close",
}

COMMON_SELECTORS = [
    # よくある本文の入れ物（上から順番に試す）
    "article",                         # 汎用
    "[data-testid='Body']",
    "div.article-body", "div.ArticleBody",
    "div.story-content", "div.paywall-article", "div#article-body",
    "div[itemprop='articleBody']",
    "section#content", "main#content",
    ".post-content", ".entry-content", ".c-article__body",
]

# ===== Notion（任意） =====
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DB = os.getenv("NOTION_DATABASE_ID")
use_notion = bool(NOTION_TOKEN and NOTION_DB)
if use_notion:
    try:
        from notion_client import Client as NotionClient
        notion = NotionClient(auth=NOTION_TOKEN)
    except Exception:
        use_notion = False

def safe_sleep(t):
    # 秒数を見えるログ
    print(f"⏳ wait {int(t)}s …")
    time.sleep(t)

def fetch_html(url):
    session = requests.Session()
    headers = HEADERS_BASE.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)

    last_exc = None
    for attempt in range(1, MAX_RETRIES+1):
        try:
            resp = session.get(url, headers=headers, timeout=TIMEOUT)
            status = resp.status_code

            # 正常
            if 200 <= status < 300 and "text/html" in resp.headers.get("Content-Type", ""):
                return resp.text

            # 429/403: 強めバックオフ
            if status in (403, 429):
                backoff = random.uniform(*HARD_BACKOFF_4XX)
                print(f"⚠ {status} on {url} -> hard backoff {int(backoff)}s")
                safe_sleep(backoff)
            else:
                # 4xx/5xxその他 → 軽い指数バックオフ
                backoff = min(60, 2 ** attempt * 3 + random.uniform(0, 3))
                print(f"⚠ status {status} (attempt {attempt}) -> backoff {int(backoff)}s")
                safe_sleep(backoff)

        except requests.RequestException as e:
            last_exc = e
            backoff = min(60, 2 ** attempt * 3 + random.uniform(0, 3))
            print(f"⚠ error {e} (attempt {attempt}) -> backoff {int(backoff)}s")
            safe_sleep(backoff)

    raise RuntimeError(f"Failed to fetch: {url} ({last_exc})")

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    # タイトル（fallbackあり）
    title = (
        (soup.title.string.strip() if soup.title and soup.title.string else None)
        or (soup.find("meta", property="og:title") or {}).get("content")
        or ""
    )

    # 本文候補を順に探索
    body_text = ""
    for css in COMMON_SELECTORS:
        node = soup.select_one(css)
        if node and node.get_text(strip=True):
            # 過剰を削る
            paragraphs = [p.get_text(" ", strip=True) for p in node.find_all(["p","li"])]
            if not paragraphs:
                paragraphs = [node.get_text(" ", strip=True)]
            body_text = "\n".join(paragraphs).strip()
            if body_text:
                break

    # 何も取れなければ空返し
    return title, body_text

def post_to_notion(title, url, summary):
    if not use_notion:
        return
    try:
        notion.pages.create(
            parent={"database_id": NOTION_DB},
            properties={
                "title": {"title": [{"text": {"content": title or "(no title)"}}]},
                "URL": {"url": url},
                "summary_ja": {"rich_text": [{"text": {"content": summary[:1900]}}]},
            },
        )
        print("🟢 Notion 登録 OK")
    except Exception as e:
        print(f"🟠 Notion 登録失敗: {e}")

def main():
    urls_path = pathlib.Path("urls.txt")
    urls = [line.strip() for line in urls_path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")]
    out_dir = pathlib.Path("out"); out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "news.jsonl"

    print(f"🔁 {len(urls)}本をゆっくり巡回します（{MIN_DELAY}-{MAX_DELAY}s間隔 + バックオフ）")

    for idx, url in enumerate(urls, 1):
        print(f"\n——— [{idx}/{len(urls)}] {url}")
        # ドメイン単位での一般的な礼儀的ウェイト
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        safe_sleep(delay)

        try:
            html = fetch_html(url)
            title, body = extract_text(html)

            if not body:
                print("❌ 本文が見つかりませんでした（ページが高度に動的 or 制限中の可能性）")
                # デバッグ用にHTML保存
                dbg = out_dir / f"page_source_{idx}.html"
                dbg.write_text(html, encoding="utf-8", errors="ignore")
                print(f"🧩 デバッグHTML保存: {dbg}")
            else:
                preview = body[:500].replace("\n", " ")
                print(f"🟢 抽出OK: {title[:80]}")
                print(f"   先頭500字: {preview}")

            record = {
                "url": url,
                "title": title,
                "body": body,
                "fetched_at": int(time.time()),
            }
            with out_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

            # 任意: Notion
            if body:
                post_to_notion(title, url, body)

        except Exception as e:
            print(f"🔴 失敗: {e}")

    print(f"\n✅ 完了: {out_file} に追記しました")
    print("   （次回は urls.txt を更新して同じスクリプトをもう一度実行するだけ）")

if __name__ == "__main__":
    main()
