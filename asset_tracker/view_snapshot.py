#!/usr/bin/env python3
import os
import sys
from pathlib import Path

SNAPSHOT_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"

def list_snapshots():
    print("📁 スナップショット一覧:")
    for f in sorted(os.listdir(SNAPSHOT_DIR), reverse=True):
        if f.endswith(".md"):
            print("  -", f)

def view_snapshot(filename):
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    if not os.path.exists(filepath):
        print(f"❌ ファイルが見つかりません: {filepath}")
        list_snapshots()
        return
    print(f"📄 {filename}")
    print("=" * 60)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                print("\n🟥", line.strip("# ").strip())
            elif line.startswith("## "):
                print("\n🟦", line.strip("# ").strip())
            elif line.startswith("### "):
                print("🔹", line.strip("# ").strip())
            elif line.strip() == "":
                print()
            else:
                print("   ", line.strip())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗ファイル名を指定してください（例: 2025-08-15_タイトル.md）")
        list_snapshots()
        sys.exit(1)

    fname = sys.argv[1]
    view_snapshot(fname)
