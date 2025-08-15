import requests
from bs4 import BeautifulSoup

def scrape_reuters_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print("❌ Failed to fetch article")
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    paragraphs = soup.find_all("p")

    content = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            content.append(text)

    return "\n".join(content[:10])  # 最初の10段落だけ取得（短くするため）

if __name__ == "__main__":
    # 例として、ロイター記事URLを貼ってください
    url = input("📰 記事URLを入力してください: ")
    article = scrape_reuters_article(url)
    if article:
        print("✅ 抽出成功：")
        print(article)
