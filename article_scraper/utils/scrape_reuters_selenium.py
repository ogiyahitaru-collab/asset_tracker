from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

url = input("記事URLを入力してください: ")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)
driver.get(url)
time.sleep(5)  # JavaScriptが読み込まれるまで待機

html = driver.page_source
with open("page_source.html", "w", encoding="utf-8") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")
paragraphs = soup.find_all("p")
if paragraphs:
    text = "\n".join([p.get_text() for p in paragraphs])
    print(text)
else:
    print("本文が見つかりませんでした。")

driver.quit()

