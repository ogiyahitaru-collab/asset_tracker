import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 自動インストール
chromedriver_autoinstaller.install()

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

print("📰 記事URLを入力してください:")
url = input().strip()

try:
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)

    paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p")
    text = "\n".join([p.text for p in paragraphs if p.text.strip() != ""])

    if text:
        print("✅ 取得成功！記事内容：\n")
        print(text[:1000] + " ...\n\n（省略）")
    else:
        print("❌ 本文が見つかりませんでした")

except Exception as e:
    print(f"❌ エラー: {e}")

finally:
    driver.quit()
