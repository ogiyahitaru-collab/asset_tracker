import re, json
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta

DEFAULT_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/127.0.0.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}
REQUEST_TIMEOUT = 12
RETRY_STATUS = {502,503,504}

def _strip_amp(url: str) -> str:
    from urllib.parse import urljoin
    parsed = urlparse(url)
    path = re.sub(r'/amp/?$', '/', parsed.path)
    path = re.sub(r'/amp(/|$)', r'/', path)
    q = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in {"outputtype","amp"}]
    new_query = urlencode(q, doseq=True)
    normalized = urlunparse(parsed._replace(path=path, query=new_query))
    normalized = re.sub(r'(?<!:)//+', '/', normalized.replace(':/', '://'))
    return normalized

def _extract_canonical(html: str, base_url: str) -> str | None:
    try:
        soup = BeautifulSoup(html, "html.parser")
        link = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
        if link and link.get("href"): return link["href"].strip()
    except Exception: pass
    return None

def _http_get(url: str, headers: dict | None = None) -> requests.Response:
    hdrs = DEFAULT_HEADERS | (headers or {})
    last_exc = None
    for _ in range(3):
        try:
            resp = requests.get(url, headers=hdrs, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            if resp.status_code in RETRY_STATUS: continue
            return resp
        except requests.RequestException as e:
            last_exc = e
    if last_exc: raise last_exc
    return resp  # type: ignore

def fetch_article_html_with_fallback(url: str) -> tuple[str|None, str|None]:
    tried = set(); candidates = [url]
    for cur in list(candidates):
        if not cur or cur in tried: continue
        tried.add(cur)
        resp = _http_get(cur)
        if resp.status_code == 404 or (resp.ok and len(resp.text) < 1000):
            stripped = _strip_amp(cur)
            if stripped and stripped != cur and stripped not in tried:
                candidates.append(stripped); continue
        else:
            canonical = _extract_canonical(resp.text, cur)
            if canonical:
                canonical = requests.compat.urljoin(cur, canonical)
                if canonical not in tried:
                    can_resp = _http_get(canonical)
                    if can_resp.ok and len(can_resp.text) > len(resp.text):
                        return can_resp.text, can_resp.url
            return resp.text, resp.url
    return None, None

def _cleanup_para(t:str)->str:
    t = re.sub(r"\s+", " ", t).strip()
    if any(x in t for x in ("Our Standards","Thomson Reuters","Sign up","All quotes delayed","© 20","Reporting by","Editing by","opens new tab")):
        return ""
    return t

def _extract_published_at(soup: BeautifulSoup, url:str):
    # meta
    meta = soup.find("meta", attrs={"property":"article:published_time"}) or \
           soup.find("meta", attrs={"name":"article:published_time"}) or \
           soup.find("meta", attrs={"itemprop":"datePublished"})
    dt_str = meta.get("content") if meta and meta.get("content") else None
    # JSON-LD
    if not dt_str:
        for s in soup.find_all("script", attrs={"type":"application/ld+json"}):
            try:
                data = json.loads(s.string or "")
                cand = [data] if isinstance(data, dict) else (data if isinstance(data, list) else [])
                for d in cand:
                    if isinstance(d, dict) and d.get("datePublished"):
                        dt_str = d["datePublished"]; break
                if dt_str: break
            except Exception: continue
    dt = None
    if dt_str:
        try: dt = datetime.fromisoformat(dt_str.replace("Z","+00:00"))
        except Exception: dt = None
    if dt is None:
        if "jp.reuters.com" in url: dt = datetime.now(timezone(timedelta(hours=9)))
        else: dt = datetime.now(timezone.utc)
    return dt

def scrape_single_article(url: str) -> dict:
    html, final_url = fetch_article_html_with_fallback(url)
    if not html: raise RuntimeError(f"Failed to fetch article: {url}")
    soup = BeautifulSoup(html, "html.parser")

    # title
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else None
    if not title:
        og = soup.find("meta", attrs={"property":"og:title"})
        title = og.get("content").strip() if og and og.get("content") else "No Title"

    # paragraphs
    paragraphs = []
    for p in soup.find_all("p", attrs={"data-testid": True}):
        txt = _cleanup_para(p.get_text(" ", strip=True));  paragraphs.append(txt) if txt else None
    if not paragraphs:
        for p in soup.select("p.text__text"):
            txt = _cleanup_para(p.get_text(" ", strip=True)); paragraphs.append(txt) if txt else None
    if not paragraphs:
        for p in soup.find_all("p"):
            txt = _cleanup_para(p.get_text(" ", strip=True)); paragraphs.append(txt) if txt else None

    body = "\n".join([x for x in paragraphs if x])
    published_at = _extract_published_at(soup, final_url or url)

    return {
        "url": final_url or url,
        "final_url": final_url or url,
        "title": title,
        "text": body,
        "published_at": published_at.isoformat(),
    }
