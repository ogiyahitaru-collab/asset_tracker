#!/usr/bin/env python3
import os
import sys
import difflib

SNAPSHOT_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"

def read_file(filename):
    path = os.path.join(SNAPSHOT_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ ファイルが存在しません: {filename}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

def diff_files(file1, file2):
    lines1 = read_file(file1)
    lines2 = read_file(file2)

    if not lines1 or not lines2:
        return

    print(f"🔍 差分比較: {file1} vs {file2}")
    print("=" * 60)
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=file1, tofile=file2,
        lineterm=""
    )
    for line in diff:
        if line.startswith("+ "):
            print(f"\033[92m{line}\033[0m", end="")  # 緑
        elif line.startswith("- "):
            print(f"\033[91m{line}\033[0m", end="")  # 赤
        else:
            print(line, end="")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❗比較対象の2ファイルを指定してください（例: snapshot_diff.py A.md B.md）")
        sys.exit(1)
    file1, file2 = sys.argv[1], sys.argv[2]
    diff_files(file1, file2)
