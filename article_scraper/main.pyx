import os
import sys
import json
import argparse
import pandas as pd

# 相対パスモジュール読み込み用
sys.path.append("./article_scraper")

from scraper import scrape_articles
from summarizer import summarize_articles
from utils.notion import post_to_notion

# ログファイルのパス
SENT_LOG_PATH = "output/sent_log.json"

def load_sent_log():
    if os.path.exists(SENT_LOG_PATH):
        with open(SENT_LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_sent_log(sent_articles):
    with open(SENT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(sent_articles, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="送信する最大件数")
    args = parser.parse_args()

    print("🔍 記事を取得中...")
    articles = scrape_articles()

    # 送信済みURLのフィルター
    sent_log = load_sent_log()
    new_articles = [a for a in articles if a.get("url") and a["url"] not in sent_log]

    if args.limit:
        new_articles = new_articles[:args.limit]

    if not new_articles:
        print("⏭️ 新しい記事はありません。終了します。")
        return

    print("✍️ 要約生成中...")
    summaries = summarize_articles(new_articles)

    os.makedirs("output", exist_ok=True)

    # JSON保存
    with open("output/summary.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    # CSV保存
    df = pd.DataFrame(summaries)
    df.to_csv("output/summary.csv", encoding="utf-8", index=False)

    print("📤 Notionに送信中...")
    post_to_notion.main()

    # ログ更新
    sent_log += [a["url"] for a in new_articles]
    save_sent_log(sent_log)

    print("✅ 全処理完了")

if __name__ == "__main__":
    main()
