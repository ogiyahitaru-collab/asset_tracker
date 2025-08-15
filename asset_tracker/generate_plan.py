import json
from datetime import datetime
import os

# 共通マスターディレクトリ
MASTER_DIR = "/volume1/docker/_shared_master_data"
ASSETS_MASTER_FILE = os.path.join(MASTER_DIR, "assets_master.json")
PROFILE_MASTER_FILE = os.path.join(MASTER_DIR, "profile_master.json")
KNOWLEDGE_ASSETS_FILE = os.path.join(MASTER_DIR, "knowledge_assets.json")
PLAN_FILE = "plan.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def sum_knowledge_assets(knowledge_assets):
    total_value = 0
    for category in knowledge_assets.values():
        for item in category:
            total_value += item.get("value", 0)
    return total_value

def generate_plan():
    assets_master = load_json(ASSETS_MASTER_FILE)
    profile_master = load_json(PROFILE_MASTER_FILE)
    knowledge_assets = load_json(KNOWLEDGE_ASSETS_FILE)

    target_year = profile_master["goals"]["target_year"]
    target_amount = profile_master["goals"]["target_assets"]

    milestones = profile_master["goals"].get("milestones", [
        {"year": target_year - 6, "event": "子ども進学", "cost": 3000000},
        {"year": target_year, "event": "住宅購入", "cost": 40000000}
    ])

    knowledge_total = sum_knowledge_assets(knowledge_assets)

    plan = {
        "target_year": target_year,
        "target_amount": target_amount,
        "milestones": milestones,
        "expected_return": 0.04,
        "current_assets": {
            "cash": sum(a["amount"] for a in assets_master.get("cash", {}).values()),
            "stocks": {code: data["quantity"] for code, data in assets_master.get("stocks", {}).items()},
            "funds": {name: data["amount"] for name, data in assets_master.get("funds", {}).items()},
            "bonds": {name: data["amount"] for name, data in assets_master.get("bonds", {}).items()},
            "knowledge_assets": knowledge_total
        }
    }

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print(f"✅ {PLAN_FILE} を生成しました ({datetime.now().date()})")
    print(f"📚 知的資産合計: {knowledge_total:,} 円")

if __name__ == "__main__":
    generate_plan()
