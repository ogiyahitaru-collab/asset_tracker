FROM python:3.11-slim

# 基本パッケージ
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Chromeパス指定
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 必要なPythonモジュール
RUN pip install selenium

WORKDIR /app
COPY scrape_article_selenium.py /app/

CMD ["python", "scrape_article_selenium.py"]
