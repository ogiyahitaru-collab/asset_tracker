#!/usr/bin/env python3
import os, subprocess
REPO_DIR = "/volume1/docker"  # リポジトリのルート

def autopush(message: str):
    try:
        cwd = os.getcwd()
        os.chdir(REPO_DIR)
        subprocess.run(["git","add","."], check=True)
        # 何も変更ない場合はコミットしない
        changed = subprocess.run(["git","diff","--cached","--quiet"])
        if changed.returncode != 0:
            subprocess.run(["git","commit","-m", message], check=True)
            subprocess.run(["git","push"], check=True)
            print("✅ Git auto-push done.")
        else:
            print("ℹ️ No changes to commit.")
    finally:
        os.chdir(cwd)
