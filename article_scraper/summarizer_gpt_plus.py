import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_summarize_plus(text, lang="ja"):
    prompt = f"""
以下のニュース記事について、以下の3項目に分けて要点をそれぞれ2〜3文で出力してください：

①【背景】
②【要点】
③【行動示唆】

出力は{lang}で。ですます調でなくてもOKです。
---
{text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはプロのビジネス分析者です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

def summarize_articles(articles):
    results = []
    for i, article in enumerate(articles, 1):
        print(f"🧠 GPT補足付き要約中: {i}/{len(articles)}")
        content = article.get("content") or article.get("summary") or ""
        full_summary = gpt_summarize_plus(content)
        results.append({
            "title": article.get("title", f"Untitled {i}"),
            "url": article.get("url"),
            "summary_ja": full_summary,
            "published_at": datetime.now().isoformat(),
            "tags": ["補足要約", "GPT"]
        })
    return results
