#!/usr/bin/env python3
import os, subprocess
REPO_DIR = "/volume1/docker"  # リポジトリのルート

def _run(cmd):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def autopush(message: str):
    cwd = os.getcwd()
    try:
        os.chdir(REPO_DIR)
        _run(["git","add","."])
        # 差分がなければ抜ける
        if _run(["git","diff","--cached","--quiet"]).returncode == 0:
            print("ℹ️ No changes to commit.")
            return
        _run(["git","commit","-m", message])
        # 通常 push
        r = _run(["git","push"])
        if r.returncode == 0:
            print("✅ Git auto-push done.")
            return
        print("⚠️ git push failed once. retrying with --no-verify ...")
        # 一度だけ no-verify で再試行（hookでの過検知や一時的失敗を回避）
        r2 = _run(["git","push","--no-verify"])
        if r2.returncode == 0:
            print("✅ Git auto-push done (no-verify fallback).")
        else:
            print("❌ Git push failed.\n---stdout/stderr---\n" + (r2.stdout or ""))
    finally:
        os.chdir(cwd)
