#!/usr/bin/env python3
import os
import json
from datetime import datetime

INDEX_FILE = "/volume1/docker/_shared_master_data/conversation_snapshots/_snapshots_index.json"

def print_snapshot(entry):
    print("📝", entry.get("date", "????-??-??"), "-", entry.get("title", "No Title"))
    print("    📁", entry.get("project", "No Project"))
    print("    🏷️", entry.get("tags", ""))
    print("    ✏️", entry.get("tldr", ""))
    print("-" * 60)

def main(limit=5):
    if not os.path.exists(INDEX_FILE):
        print("❌ インデックスファイルが存在しません:", INDEX_FILE)
        return

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("⚠️ JSON読み込みエラー:", e)
        return

    print(f"📋 スナップショット一覧（最新{limit}件）")
    print("=" * 60)

    count = 0
    for entry in data:
        print_snapshot(entry)
        count += 1
        if count >= limit:
            break

if __name__ == "__main__":
    import sys
    arg = sys.argv[1:] 
    limit = int(arg[0]) if arg else 5
    main(limit)
