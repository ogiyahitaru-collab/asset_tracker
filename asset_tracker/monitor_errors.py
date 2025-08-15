#!/usr/bin/env python3
import os
import json
from datetime import datetime

SNAPSHOT_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"
INDEX_FILE = os.path.join(SNAPSHOT_DIR, "_snapshots_index.json")
ERROR_LOG_FILE = os.path.join(SNAPSHOT_DIR, "_snapshots_error.log")

today_str = datetime.now().strftime("%Y-%m-%d")
LOG_FILE = f"/volume1/docker/asset_tracker/logs/monitor_{today_str}.log"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def check_index_file():
    if not os.path.exists(INDEX_FILE):
        log("❌ インデックスファイルが存在しません")
        return False

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        broken = [e for e in data if "filename" not in e]
        if broken:
            log(f"⚠️ index内に filename 欠落: {len(broken)}件 → 自動修正を提案")
            for b in broken:
                log(f"    ⛔ 修正候補: {b}")
            return False
        else:
            log(f"✅ インデックス構造チェック：OK（{len(data)}件）")
            return True
    except Exception as e:
        log(f"❌ JSON読み込みエラー: {str(e)}")
        return False

def check_error_log():
    if not os.path.exists(ERROR_LOG_FILE):
        log("✅ エラーログファイル：存在せず（正常）")
        return

    with open(ERROR_LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        recent = lines[-20:] if len(lines) > 20 else lines
        for l in recent:
            if "Error" in l or "Traceback" in l:
                log("⚠️ エラーログに新しいエラーが検出されました")
                break

def check_snapshot_files():
    md_files = [f for f in os.listdir(SNAPSHOT_DIR) if f.endswith(".md")]
    filenames = set(md_files)

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index = json.load(f)
    except:
        log("❌ index読み込み失敗（スキップ）")
        return

    for entry in index:
        fname = entry.get("filename")
        if fname and fname not in filenames:
            log(f"⚠️ インデックスにはあるが、Markdownファイルが存在しない: {fname}")

log("🔍 モニタリング開始")
check_index_file()
check_snapshot_files()
check_error_log()
log("✅ モニタリング完了")
