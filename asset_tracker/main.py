import json
import argparse
from datetime import datetime
import csv
import os

LOG_FILE = "asset_log.csv"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_assets(plan, prices=None):
    # 安全資産（現金＋債券）
    safe_assets = plan["current_assets"]["cash"]

    bonds = plan["current_assets"].get("bonds", {})
    for amount in bonds.values():
        safe_assets += amount

    # リスク資産（株式＋投資信託）
    risk_assets = 0
    stocks = plan["current_assets"].get("stocks", {})
    for code, qty in stocks.items():
        price = prices.get(code, 0) if prices else 0
        risk_assets += qty * price

    funds = plan["current_assets"].get("funds", {})
    for amount in funds.values():
        risk_assets += amount

    # 知的資産（分類上は安全資産に加算）
    knowledge_assets = plan["current_assets"].get("knowledge_assets", 0)
    safe_assets += knowledge_assets

    total_assets = safe_assets + risk_assets
    return total_assets, risk_assets, safe_assets

def append_log(date, total_assets, target_amount, progress):
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "total_assets", "target_amount", "progress_percent"])
        writer.writerow([date, total_assets, target_amount, round(progress, 2)])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default="plan.json")
    parser.add_argument("--prices", default=None)
    args = parser.parse_args()

    plan = load_json(args.plan)
    prices = load_json(args.prices) if args.prices else None

    total_assets, risk_assets, safe_assets = calculate_assets(plan, prices)
    target_amount = plan["target_amount"]
    progress = total_assets / target_amount * 100
    today = datetime.now().date()

    risk_ratio = (risk_assets / total_assets) * 100 if total_assets else 0
    safe_ratio = (safe_assets / total_assets) * 100 if total_assets else 0

    # 表示
    print(f"📅 {today}")
    print(f"💰 現在の資産総額: {total_assets:,.0f} 円")
    print(f"🎯 目標金額: {target_amount:,.0f} 円")
    print(f"📈 達成率: {progress:.2f}%")
    print(f"⚖️ 資産構成比 → リスク資産: {risk_ratio:.2f}%, 安全資産: {safe_ratio:.2f}%")

    # ログ保存
    append_log(today, total_assets, target_amount, progress)

if __name__ == "__main__":
    main()
