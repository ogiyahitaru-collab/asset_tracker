#!/usr/bin/env python3
import os
import sys
import shutil
from datetime import datetime

SNAPSHOT_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"
BACKUP_DIR = os.path.join(SNAPSHOT_DIR, "_deleted")

def delete_snapshot(filename):
    path = os.path.join(SNAPSHOT_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ ファイルが存在しません: {path}")
        print("\n📁 現在のスナップショット一覧:")
        for f in sorted(os.listdir(SNAPSHOT_DIR)):
            if f.endswith(".md"):
                print("  -", f)
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"{timestamp}_{filename}")

    shutil.move(path, backup_path)
    print(f"🗑️ スナップショットを削除（バックアップ済）: {filename}")
    print(f"📁 バックアップ先: {backup_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❗削除したいファイル名を指定してください（例: snapshot_delete.py 2025-08-15_タイトル.md）")
        sys.exit(1)

    filename = sys.argv[1]
    delete_snapshot(filename)
