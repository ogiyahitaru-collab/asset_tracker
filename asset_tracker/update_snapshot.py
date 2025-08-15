#!/usr/bin/env python3
import sys, os, json, traceback
from datetime import datetime
from git_tools import autopush

SAVE_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"
INDEX_FILE = os.path.join(SAVE_DIR, "_snapshots_index.json")
ERROR_LOG_FILE = os.path.join(SAVE_DIR, "_snapshots_error.log")

# 使い方: python3 update_snapshot.py 2025-08-15 field value...
# field: title|project|tags|tldr|achievement|trigger|summary
if len(sys.argv) < 4:
    print("❌ 引数不足: python3 update_snapshot.py YYYY-MM-DD field value")
    sys.exit(1)

date_str, field = sys.argv[1:3]
value = " ".join(sys.argv[3:])
md_target = None

# 対象Markdown探索
for f in os.listdir(SAVE_DIR):
    if f.startswith(date_str+"_") and f.endswith(".md"):
        md_target = os.path.join(SAVE_DIR, f)
        break

if not md_target:
    print(f"❌ 該当Markdownが見つかりません: {date_str}_*.md")
    sys.exit(1)

# Markdownの読み込み・書換
with open(md_target, "r", encoding="utf-8") as f:
    lines = f.readlines()

def replace_block(lines, header, newtext):
    out, i = [], 0
    found = False
    while i < len(lines):
        line = lines[i]
        if line.strip() == header:
            found = True
            out.append(line)
            i += 1
            # 空行 or 次のヘッダまで置換
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            out.append(newtext + "\n\n")
        else:
            out.append(line)
            i += 1
    if not found:
        out.append(header + "\n")
        out.append(newtext + "\n\n")
    return out

mapping = {
    "project": "## プロジェクト",
    "tags": "## タグ",
    "tldr": "## TL;DR",
    "achievement": "## 成果",
    "trigger": "## 起点",
    "summary": "## 本文",
    "title": "#"
}

if field == "title":
    # 1行目タイトルを差し替え＋ファイル名も変更
    title_line = lines[0] if lines else ""
    new_title = value
    new_line = f"# {new_title} ({date_str})\n"
    if lines:
        lines[0] = new_line
    else:
        lines = [new_line, "\n"]
    # ファイル名変更
    old_name = os.path.basename(md_target)
    safe_title = new_title.replace(" ","_").replace("/","-")
    new_name = f"{date_str}_{safe_title}.md"
    new_path = os.path.join(SAVE_DIR, new_name)
    with open(new_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.remove(md_target)
    md_target = new_path
    print(f"✅ タイトル更新＆リネーム: {old_name} → {new_name}")
else:
    header = mapping.get(field)
    if not header:
        print("❌ 不明なfield: ", field)
        sys.exit(1)
    if header == "#":
        print("❌ タイトル更新は field=title を使用してください")
        sys.exit(1)
    lines = replace_block(lines, header, value)
    with open(md_target, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"✅ Markdown更新: {os.path.basename(md_target)} [{field}]")

# インデックス更新（title/filenameも反映）
try:
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        index = json.load(f)
except:
    index = []
filename = os.path.basename(md_target)
# 旧レコード排除して追加
index = [e for e in index if e.get("filename") != filename]
# タイトル抽出
with open(md_target, "r", encoding="utf-8") as f:
    first = f.readline().strip()
title = first.replace("# ","").split(" (")[0] if first.startswith("# ") else filename
entry = next((e for e in index if e.get("filename")==filename), None)
if entry: index.remove(entry)
index.insert(0, {"date": date_str, "title": title, "filename": filename})
with open(INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)
print(f"✅ インデックス更新: {INDEX_FILE}")

# Git自動push
autopush(f"docs(snapshot): {filename} {field} updated")
