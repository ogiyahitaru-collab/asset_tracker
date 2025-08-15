#!/usr/bin/env python3
import os
import sys
from pathlib import Path

SNAPSHOT_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"

def search_snapshots(keyword):
    found = []
    for fname in sorted(os.listdir(SNAPSHOT_DIR)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(SNAPSHOT_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                matches = [line.strip() for line in lines if keyword in line]
                if matches:
                    found.append((fname, matches))
        except Exception as e:
            print(f"⚠️ 読み取りエラー: {fname} - {e}")

    if not found:
        print(f"❌ キーワード「{keyword}」を含むスナップショットは見つかりませんでした。")
        return

    print(f"🔍 検索結果（キーワード: {keyword}）")
    print("=" * 60)
    for fname, matches in found:
        print(f"📝 {fname}")
        for match in matches:
            print(f"    🔹 {match}")
        print("-" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗検索キーワードを指定してください（例: python3 snapshot_search.py 成功）")
        sys.exit(1)

    keyword = sys.argv[1]
    search_snapshots(keyword)
