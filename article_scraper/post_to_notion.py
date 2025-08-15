import os, json
from datetime import datetime
try:
    import requests
except Exception as e:
    raise RuntimeError("requests が未導入です（Docker内で pip install されます）")
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID  = os.getenv("NOTION_DATABASE_ID") or os.getenv("DATABASE_ID")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}" if NOTION_TOKEN else "",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
def _blk(text):
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":str(text)}}]}}
def _payload(title, url, published_at, tags, summary, background, key_points, actions):
    props = {
        "Name": {"title": [{"text": {"content": title or "No Title"}}]},
        "URL": {"url": url or None},
        "Published": {"date": {"start": (published_at or datetime.utcnow().isoformat()+"Z")}},
    }
    if tags: props["Tags"] = {"multi_select": [{"name": t} for t in tags if t]}
    children = []
    if summary:    children += [{"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Summary"}}]}}, _blk(summary)]
    if background: children += [{"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Background"}}]}}, _blk(background)]
    if key_points: children += [{"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Key Points"}}]}}, *[_blk(f"- {kp}") for kp in key_points]]
    if actions:    children += [{"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Actions"}}]}}, *[_blk(f"- {ac}") for ac in actions]]
    return {"parent":{"database_id": DATABASE_ID}, "properties": props, "children": children}
def post_to_notion(title, url, published_at, tags, summary, background, key_points, actions):
    if not NOTION_TOKEN or not DATABASE_ID:
        os.makedirs("output", exist_ok=True)
        with open("output/notion_fallback.jsonl","a",encoding="utf-8") as f:
            f.write(json.dumps({
                "title": title, "url": url, "published_at": published_at, "tags": tags,
                "summary": summary, "background": background, "key_points": key_points, "actions": actions,
                "_note": "NOTION_TOKEN or DATABASE_ID missing. Saved locally instead."
            }, ensure_ascii=False)+"\n")
        return {"id": None, "status": "LOCAL_FALLBACK"}
    payload = _payload(title, url, published_at, tags, summary, background, key_points, actions)
    import requests
    r = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, data=json.dumps(payload))
    if r.status_code >= 300:
        raise RuntimeError(f"Notion API Error {r.status_code}: {r.text}")
    return r.json()
