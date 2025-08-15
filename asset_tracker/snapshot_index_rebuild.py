import os
import json
import re

SNAPSHOT_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"
META_FILE = os.path.join(SNAPSHOT_DIR, "snapshots_index.json")

def rebuild_index():
    all_entries = []
    for filename in os.listdir(SNAPSHOT_DIR):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(SNAPSHOT_DIR, filename)

        # ファイル名例: 2025-08-15_資産管理＋知的資産統合システム構築.md
        date_part, title_part = filename.split("_", 1)
        title = title_part.replace(".md", "")

        tags = []
        tldr = ""

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("- タグ:"):
                    tags = re.findall(r"#\S+", line)
                elif line.startswith("- 要約(TL;DR):"):
                    tldr = line.replace("- 要約(TL;DR):", "").strip()

        all_entries.append({
            "date": date_part,
            "title": title,
            "tags": tags,
            "tldr": tldr,
            "file": filename
        })

    # JSON保存
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(all_entries)} 件のスナップショットをインデックス化しました。")
    print(f"📄 {META_FILE}")

if __name__ == "__main__":
    rebuild_index()
