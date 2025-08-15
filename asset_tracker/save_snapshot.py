#!/usr/bin/env python3
import sys
import os
import json
from datetime import datetime
import traceback

SAVE_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"
INDEX_FILE = os.path.join(SAVE_DIR, "_snapshots_index.json")
ERROR_LOG_FILE = os.path.join(SAVE_DIR, "_snapshots_error.log")

# 引数確認
if len(sys.argv) < 10:
    print("❌ 引数不足: 以下の形式で実行してください")
    print("python3 save_snapshot.py タイトル プロジェクト タグ TLDR 成果 起点 本文1 本文2 本文3")
    sys.exit(1)

title, project, tags, tldr, achievement, trigger = sys.argv[1:7]
body_lines = sys.argv[7:]
body = "\n".join(body_lines)

# 日付・ファイル名作成
date_str = datetime.now().strftime("%Y-%m-%d")
safe_title = title.replace(" ", "_").replace("/", "-")
filename = f"{date_str}_{safe_title}.md"
filepath = os.path.join(SAVE_DIR, filename)

# 保存先フォルダがなければ作成
os.makedirs(SAVE_DIR, exist_ok=True)

# Markdown書き出し
with open(filepath, "w", encoding="utf-8") as f:
    f.write(f"# {title} ({date_str})\n\n")
    f.write(f"## プロジェクト\n{project}\n\n")
    f.write(f"## タグ\n{tags}\n\n")
    f.write(f"## TL;DR\n{tldr}\n\n")
    f.write(f"## 成果\n{achievement}\n\n")
    f.write(f"## 起点\n{trigger}\n\n")
    f.write(f"## 本文\n{body}\n")

print(f"✅ スナップショット保存完了: {filepath}")

# インデックス更新
try:
    index = []
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            index = json.load(f)

    index = [e for e in index if e.get("filename") != filename]

    index_entry = {
        "date": date_str,
        "title": title,
        "project": project,
        "tags": tags,
        "tldr": tldr,
        "filename": filename
    }
    index.insert(0, index_entry)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✅ インデックス更新: {INDEX_FILE}")

except Exception as e:
    print("⚠️ インデックス更新中にエラーが発生しました")
    print(str(e))
    with open(ERROR_LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Error updating index for: {filename}\n")
        log.write(traceback.format_exc())
        log.write("\n---\n")
    print(f"📝 エラーログに記録済: {ERROR_LOG_FILE}")
