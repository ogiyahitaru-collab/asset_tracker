import openai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt_summarize(text, lang="ja"):
    prompt = f"""
以下はニュース記事です。これをビジネスパーソン向けに3〜4文で要約してください。
出力は{lang}で簡潔かつ自然な文章にしてください。

---
{text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "あなたはプロのニュース要約者です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

def summarize_articles(articles):
    results = []
    for i, article in enumerate(articles, 1):
        print(f"🧠 GPT要約中: {i}/{len(articles)}")
        content = article.get("content") or article.get("summary") or ""
        summary = gpt_summarize(content)
        results.append({
            "title": article.get("title", f"Untitled {i}"),
            "url": article.get("url"),
            "summary_ja": summary,
            "published_at": datetime.now().isoformat(),
            "tags": ["GPT要約"]
        })
    return results
