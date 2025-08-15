#!/usr/bin/env python3

import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# .envファイルの読み込み
load_dotenv()

# APIキーを読み込んでクライアント初期化
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize(text):
    prompt = f"Summarize the following English news article in 2 short sentences:\n\n{text}" 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def main():
    input_path = "../output/news.json"
    output_path = "../output/summary.json"

    # JSON読み込み
    with open(input_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    summarized = []
    for article in articles:
        summary_en = summarize(article["content_snippet"])
        summarized.append({
            "title": article["title"],
            "link": article.get("link", "リンク不明"),
            "summary_en": summary_en
        })

    # JSON保存
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summarized, f, indent=2, ensure_ascii=False)

    print(f"✅ 要約完了：{output_path} に保存しました")

if __name__ == "__main__":
    main()
