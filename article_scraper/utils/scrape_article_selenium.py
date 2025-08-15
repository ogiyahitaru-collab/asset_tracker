from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys, time, os

def extract_text(driver):
    # ページ読み込みを少し待つ
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(2)

    # 候補となる領域（Reutersはレイアウトが頻繁に変わるので広めに）
    containers = [
        (By.CSS_SELECTOR, "article"),
        (By.CSS_SELECTOR, "div[role='main']"),
        (By.CSS_SELECTOR, "main"),
        (By.CSS_SELECTOR, "div[data-testid='Body']"),
        (By.CSS_SELECTOR, "div[data-testid='article-body']"),
        (By.CSS_SELECTOR, "section"),
    ]

    texts = []
    for by, sel in containers:
        try:
            elems = driver.find_elements(by, sel)
            for el in elems:
                ps = el.find_elements(By.TAG_NAME, "p")
                block = "\n".join([p.text.strip() for p in ps if p.text.strip()])
                if block:
                    texts.append(block)
            if texts:
                break
        except Exception:
            continue

    # 何も取れなかったら、ページ全体から<p>を拾う最後の手段
    if not texts:
        ps = driver.find_elements(By.TAG_NAME, "p")
        fallback = "\n".join([p.text.strip() for p in ps if p.text.strip()])
        if fallback:
            texts.append(fallback)

    return "\n\n".join(texts).strip()

def main():
    url = input("📰 記事URLを入力してください：").strip()

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,900")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        # 軽くスクロールして遅延読込を促す
        for y in (300, 900, 1500):
            driver.execute_script(f"window.scrollTo(0,{y});"); time.sleep(0.6)

        text = extract_text(driver)

        # 取得したHTMLと本文を必ず保存（ホストへ持ち出しやすいよう /app に書き出し）
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        with open("article.txt", "w", encoding="utf-8") as f:
            f.write(text or "")

        if text:
            print("\n✅ 本文抽出成功：先頭500文字プレビュー\n")
            print((text[:500] + ("…" if len(text) > 500 else "")))
        else:
            print("❌ 本文が見つかりませんでした。構造が特殊な可能性があります。")
            print("📄 取得したHTML: page_source.html を確認してください。")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
