import os, re, textwrap
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SYS = "あなたは日本語のビジネス要約アシスタントです。重要数字・固有名詞・時刻を保持し、事実のみ簡潔に。"
PROMPT = """以下のニュース本文を日本語で要約してください。出力は厳守:
# 見出し（20～36文字）
# 箇条書き3行（各70字以内、因果や影響を1つ入れる）
本文:
{body}
"""

def _cleanup(t:str)->str:
    t = re.sub(r"\s+", " ", t).strip()
    # 免責・署名等のノイズ除去
    junk = ("Our Standards","Thomson Reuters","Sign up","All quotes delayed","© 20","Reporting by","Editing by")
    for j in junk:
        t = t.replace(j," ")
    return t

def _extractive(body:str)->str:
    body = _cleanup(body)
    sents = re.split(r"(?:。|\.|\?|！|!)+\s*", body)
    sents = [s for s in sents if len(s)>10][:6]
    head = (sents[0][:34] if sents else "ニュース要約")
    bullets = []
    for s in sents[1:4]:
        s2 = s.strip()
        if s2: bullets.append("・"+s2[:66])
    while len(bullets)<3: bullets.append("・情報不足のため省略")
    return head+"\n"+"\n".join(bullets[:3])

def summarize(text:str)->str:
    body = _cleanup(text or "")
    if not body or len(body)<40:
        return "ニュース要約\n・本文が取得できませんでした\n・後で再試行してください\n・"
    if not OPENAI_API_KEY:
        return _extractive(body)
    try:
        # OpenAI responses (minimal client)
        import requests, json
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"}
        payload = {
          "model":"gpt-4o-mini",
          "messages":[
            {"role":"system","content":SYS},
            {"role":"user","content":PROMPT.format(body=body[:12000])}
          ],
          "temperature":0.2,
        }
        r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=20)
        if r.ok:
            out = r.json()["choices"][0]["message"]["content"].strip()
            # ガード: 長すぎる/形式崩れ時は抽出型へ
            if (out.count("\n")<2) or (len(out)>1200):
                return _extractive(body)
            return out
        return _extractive(body)
    except Exception:
        return _extractive(body)
