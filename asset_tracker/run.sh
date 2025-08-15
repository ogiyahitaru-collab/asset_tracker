#!/bin/bash
# 1. plan.jsonを最新マスターから生成
python3 generate_plan.py

# 2. 株価更新（Dockerでyfinance実行）
sudo docker run --rm \
    -v $(pwd):/app \
    -w /app \
    python:3.11-slim bash -c "pip install -q yfinance && python update_prices.py"

# 3. 資産計算 & ログ保存
python3 main.py --plan plan.json --prices prices.json
