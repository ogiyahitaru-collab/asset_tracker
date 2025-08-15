import os, json, argparse, time, re
from datetime import datetime, timezone, timedelta
import requests, feedparser

from utils.scraper import scrape_single_article
from utils.notion.post_to_notion import post_to_notion

# summarizer は任意（あれば使う）
try:
    from utils.summarizer_stub import summarize as ai_summarize
except Exception:
    ai_summarize = None

SENT_LOG_PATH = "output/sent_log.json"

# ====== タグ推定 ======
INDUSTRY_RULES = [
    (r"神戸製鋼|神戸鋼|Kobe Steel|Kobelco", "鉄鋼"),
    (r"JFE|日本製鉄|Nippon Steel|製鉄|粗鋼", "鉄鋼"),
    (r"石油|原油|ガス|エネルギー|LNG|再生可能|再エネ|太陽光|風力", "エネルギー"),
    (r"半導体|チップ|ファウンドリ|前工程|後工程", "半導体"),
    (r"化学|樹脂|塩ビ|ポリ|ケミカル", "化学"),
    (r"物流|海運|コンテナ|運賃", "輸送"),
]

TYPE_RULES = [
    (r"減産|生産調整|稼働率|停止解除", "生産"),
    (r"減産|生産調整|稼働率|停止解除", "生産"),
    (r"決算|業績|利益|営業益|純利益|通期見通し|ガイダンス|下方修正|上方修正", "決算"),
    (r"投資|新工場|設備投資|増産|ライン新設|資本支出|capex", "設備投資"),
    (r"買収|売却|M&A|資本提携|子会社化|合併", "M&A"),
    (r"事故|火災|爆発|不祥事|データ改ざん|品質問題|リコール", "事故・不祥事"),
    (r"規制|関税|関税リスク|制裁|輸出管理|反ダンピング|環境規制|炭素税|CBAM", "規制・政策"),
    (r"新製品|新素材|発表|披露|供給開始|受注", "新製品/受注"),
]

IMPACT_RULES = [
    (r"下方修正|停止|停止へ|操業停止|爆発|大幅下落|大幅増税|制裁強化|関税(引き上げ|強化)", "高"),
    (r"上方修正|増産|新工場|大型投資|大型受注|合弁設立|大型M&A", "高"),
    (r"調査開始|検討|方針|一部報道|観測", "中"),
]

def infer_category(rules, text):
    for pat, label in rules:
        if re.search(pat, text, re.IGNORECASE):
            return label
    return None

def infer_tags(title, body, keyword=""):
    base = " ".join([title or "", keyword or "", (body or "")[:2000]])
    industry = infer_category(INDUSTRY_RULES, base) or "未分類"
    typ      = infer_category(TYPE_RULES,      base) or "その他"
    impact   = infer_category(IMPACT_RULES,    base) or "中"
    # 「選択」に入れる合成タグ（Selectは1値のみ）
    select_value = f"業界:{industry}｜タイプ:{typ}｜影響度:{impact}"
    return select_value, {"industry": industry, "type": typ, "impact": impact}

# ====== ユーティリティ ======
def load_sent_log():
    if os.path.exists(SENT_LOG_PATH):
        try:
            with open(SENT_LOG_PATH, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_sent_log(urls:set):
    os.makedirs(os.path.dirname(SENT_LOG_PATH), exist_ok=True)
    with open(SENT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(list(urls)), f, ensure_ascii=False, indent=2)

def jst_today():
    return datetime.now(timezone(timedelta(hours=9))).date().isoformat()

def to_ymd(iso_like:str|None) -> str:
    if not iso_like:
        return jst_today()
    try:
        iso_like = iso_like.replace("Z","+00:00")
        dt = datetime.fromisoformat(iso_like)
        return dt.astimezone(timezone(timedelta(hours=9))).date().isoformat()
    except Exception:
        return jst_today()

def summarize_text(title:str, body:str) -> str:
    body = (body or "").strip()
    if ai_summarize and len(body) >= 40:
        try:
            return ai_summarize(body)
        except Exception:
            pass
    lead = (body.split("\n")[0] if body else title) or "要約なし"
    return (lead[:200] + ("…" if len(lead)>200 else ""))

def resolve_bing_apiclick(url:str) -> str:
    try:
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=12, allow_redirects=True)
        return resp.url
    except Exception:
        return url

def iter_bing_news_urls(keyword:str, limit:int):
    q = requests.utils.quote(keyword)
    rss = f"https://www.bing.com/news/search?q={q}+site:reuters.com&format=rss"
    feed = feedparser.parse(rss)
    seen = set()
    for e in feed.entries:
        if len(seen) >= limit: break
        u = e.link
        if "sitemap" in u.lower(): continue
        u = resolve_bing_apiclick(u)
        if "reuters.com" not in u: continue
        if u in seen: continue
        seen.add(u)
        yield u

# ====== メイン処理 ======
def process_url(url:str, sent:set, keyword:str=""):
    if url in sent:
        print(f"⏭️ 既送信スキップ: {url}")
        return False

    print(f"📄 Processing: {url}")
    art = scrape_single_article(url)  # {url/final_url, title, text, published_at?}
    final_url = art.get("final_url") or art.get("url") or url
    title = art.get("title") or "No Title"
    text  = art.get("text")  or ""
    pub   = to_ymd(art.get("published_at"))

    # サマリ＆タグ
    summary = summarize_text(title, text)
    select_value, tag_detail = infer_tags(title, text, keyword)

    # Notion登録（DB: title / URL / summary_ja / 日付 / 選択）
    ok = post_to_notion(
        title=title,
        url=final_url,
        summary=f"{summary}\n\n[自動タグ] 業界:{tag_detail['industry']}｜タイプ:{tag_detail['type']}｜影響度:{tag_detail['impact']}",
        date_str=pub,
        tag_name=select_value
    )
    if ok:
        sent.add(final_url)
        save_sent_log(sent)
    return ok

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="単一URLを処理")
    parser.add_argument("--keyword", help="Bing News RSSで検索して処理")
    parser.add_argument("--limit", type=int, default=5, help="取得件数（keyword時）")
    args = parser.parse_args()

    sent = load_sent_log()

    if args.url:
        process_url(args.url, sent)
        return

    if args.keyword:
        count = 0
        for u in iter_bing_news_urls(args.keyword, args.limit):
            process_url(u, sent, keyword=args.keyword)
            count += 1
            time.sleep(1.0)
        if count == 0:
            print("❌ RSSからURLを取得できませんでした")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
