import os, sys, json, re

SAVE_DIR = "/volume1/docker/_shared_master_data/conversation_snapshots"
INDEX_FILE = os.path.join(SAVE_DIR, "_snapshots_index.json")

HEADERS = {
    "project": "## 関連プロジェクト",
    "tags": "## タグ",
    "tldr": "## 要約",
    "achievement": "## 成果",
    "trigger": "## 起点となった課題",
    "summary": "## 会話要約全文",
    "structure": "## 成果構造",
    "reuse": "## 再利用ポイント",
}

INDEX_FIELDS = {"title", "project", "tags", "tldr"}  # indexに持たせるキー

def sanitize_filename(title: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", title)

def load_index():
    if not os.path.exists(INDEX_FILE):
        return []
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_entry(index, date_str):
    # date一致の先頭を返す（同日に複数ある場合は最初の1件）
    for i, e in enumerate(index):
        if e.get("date") == date_str:
            return i, e
    return None, None

def read_lines(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

def write_lines(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)

def replace_title(lines, new_title):
    # 先頭の見出し "# " を差し替え
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines[i] = f"# {new_title}\n"
            return True
    return False

def replace_section_single_line(lines, header, new_value):
    # 見出しの「次の1行」を置換（project/tags/tldr/achievement/trigger など）
    for i, line in enumerate(lines):
        if line.strip() == header:
            # 次の行が本文
            if i + 1 < len(lines):
                lines[i + 1] = f"{new_value}\n"
            else:
                lines.append(f"{new_value}\n")
            return True
    return False

def replace_section_block(lines, header, new_block):
    # headerの次行から「次の '## ' 見出し」直前までを new_block に置換（summary/structure/reuse）
    start = None
    for i, line in enumerate(lines):
        if line.strip() == header:
            start = i + 1
            break
    if start is None:
        return False

    # 終端を探す（次のセクションヘッダ）
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break

    block = (new_block.rstrip() + "\n") if new_block else ""
    new_lines = lines[:start] + [block] + lines[end:]
    # 改行を整える：ブロック直後に改行1つは維持
    if start < len(new_lines) and not new_lines[start].endswith("\n"):
        new_lines[start] = new_lines[start] + "\n"
    lines[:] = new_lines
    return True

def update_markdown(file_path, field, new_value):
    lines = read_lines(file_path)
    changed = False

    if field == "title":
        changed = replace_title(lines, new_value)
    elif field in ("project", "tags", "tldr", "achievement", "trigger"):
        header = HEADERS[field]
        changed = replace_section_single_line(lines, header, new_value)
    elif field in ("summary", "structure", "reuse"):
        header = HEADERS[field]
        changed = replace_section_block(lines, header, new_value)
    else:
        raise ValueError("不明なフィールドです")

    if changed:
        write_lines(file_path, lines)
    return changed

def main():
    if len(sys.argv) < 4:
        print("使い方: python3 update_snapshot.py <日付:YYYY-MM-DD> <フィールド名> <新しい値>")
        print("フィールド名: title / project / tags / tldr / achievement / trigger / summary / structure / reuse")
        sys.exit(1)

    date_str, field = sys.argv[1], sys.argv[2]
    new_value = " ".join(sys.argv[3:])  # スペース含む値もOK

    if not os.path.isdir(SAVE_DIR):
        print("❌ スナップショット保存ディレクトリがありません")
        sys.exit(1)

    index = load_index()
    idx, entry = find_entry(index, date_str)
    if entry is None:
        print(f"❌ インデックスで日付 {date_str} のエントリが見つかりません")
        sys.exit(1)

    # 対象MDファイルを特定
    file_name = entry.get("file")
    file_path = os.path.join(SAVE_DIR, file_name) if file_name else None
    if not file_path or not os.path.exists(file_path):
        # フォールバック：日付一致ファイルを検索
        candidates = [f for f in os.listdir(SAVE_DIR) if f.startswith(date_str) and f.endswith(".md")]
        if not candidates:
            print(f"❌ MDファイルが見つかりません（{date_str}）")
            sys.exit(1)
        file_name = candidates[0]
        file_path = os.path.join(SAVE_DIR, file_name)

    # 1) Markdownの更新
    try:
        updated = update_markdown(file_path, field, new_value)
        if not updated:
            print(f"⚠ {field} を更新できませんでした（ヘッダが見つからない可能性）")
        else:
            print(f"✅ Markdown更新: {os.path.basename(file_path)} [{field}]")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 2) index の更新（定義済みキーのみ）
    if field in INDEX_FIELDS:
        entry[field] = new_value
        # タイトル変更時はファイル名もリネームして整合性を保つ
        if field == "title":
            safe = sanitize_filename(new_value)
            new_file = f"{date_str}_{safe}.md"
            new_path = os.path.join(SAVE_DIR, new_file)
            os.rename(file_path, new_path)
            entry["file"] = new_file
            print(f"✅ ファイル名リネーム: {os.path.basename(file_path)} → {new_file}")
        save_index(index)
        print(f"✅ インデックス更新: {INDEX_FILE}")

if __name__ == "__main__":
    main()
