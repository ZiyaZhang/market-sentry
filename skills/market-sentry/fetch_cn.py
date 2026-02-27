#!/usr/bin/env python3
"""
fetch_cn.py — Fetch all CN_A market data for a given stock code.
Outputs a single JSON file the agent reads to build the narrative brief.

Usage:
    python3 fetch_cn.py 688306
    python3 fetch_cn.py 688306 /custom/output/dir

Output: {baseDir}/data/fetched/{code}.json
"""
import json, os, re, ssl, sys, time
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import URLError

CODE = sys.argv[1] if len(sys.argv) > 1 else None
if not CODE:
    print("Usage: python3 fetch_cn.py <stock_code> [output_dir]", file=sys.stderr)
    sys.exit(1)

OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "fetched")
os.makedirs(OUTDIR, exist_ok=True)

SECID = f"1.{CODE}" if CODE[0] in ("6",) else f"0.{CODE}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "*/*",
}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch(url, headers=None, timeout=20, retries=2):
    hdrs = headers or HEADERS
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=hdrs)
            with urlopen(req, timeout=timeout, context=CTX) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            return json.dumps({"_error": str(e), "_url": url})
    return json.dumps({"_error": "exhausted retries", "_url": url})


errors = []

# ── 1) K-line (OHLCV, amount, turnover) ──
raw = fetch(f"https://push2his.eastmoney.com/api/qt/stock/kline/get"
            f"?secid={SECID}&klt=101&fqt=1&end=20500101&lmt=5"
            f"&fields1=f1,f2,f3,f4,f5,f6,f7"
            f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61")
kline = None
kline_list = []
try:
    d = json.loads(raw)
    if "_error" in d:
        errors.append(f"kline: {d['_error']}")
    else:
        for line in d.get("data", {}).get("klines", []):
            p = line.split(",")
            kline_list.append(dict(
                date=p[0], open=float(p[1]), close=float(p[2]),
                high=float(p[3]), low=float(p[4]),
                volume=int(p[5]), amount=float(p[6]),
                amplitude_pct=float(p[7]), change_pct=float(p[8]),
                change_amount=float(p[9]), turnover_pct=float(p[10]),
            ))
        if kline_list:
            kline = kline_list[-1]
except Exception as e:
    errors.append(f"kline parse: {e}")

# ── 2) Real-time snapshot (price, f50 量比, f137/f193 fallback flow) ──
raw = fetch(f"https://push2.eastmoney.com/api/qt/stock/get"
            f"?secid={SECID}"
            f"&fields=f57,f58,f43,f170,f44,f45,f46,f47,f48,f50,f168,f137,f193,f86")
snapshot = None
try:
    d = json.loads(raw)
    if "_error" in d:
        errors.append(f"snapshot: {d['_error']}")
    else:
        dd = d.get("data", {})
        f43 = dd.get("f43", 0) or 0
        f170 = dd.get("f170", 0) or 0
        f50 = dd.get("f50", 0) or 0
        snapshot = dict(
            code=dd.get("f57", CODE),
            name=dd.get("f58", ""),
            price=f43 / 100 if isinstance(f43, int) and f43 > 1000 else f43,
            change_pct=f170 / 100 if isinstance(f170, int) and abs(f170) > 100 else f170,
            vol_ratio=round(f50 / 100, 2) if isinstance(f50, int) and f50 > 10 else f50,
            high=dd.get("f44"), low=dd.get("f45"), open=dd.get("f46"),
            f137=dd.get("f137"), f193=dd.get("f193"),
        )
except Exception as e:
    errors.append(f"snapshot parse: {e}")

# ── 3) Fund flow (fflow) — PRIMARY source for 主力净流入 ──
raw = fetch(f"https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
            f"?secid={SECID}&klt=101&lmt=3"
            f"&fields1=f1,f2,f3,f7"
            f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58")
fflow = None
fflow_history = []
try:
    d = json.loads(raw)
    if "_error" in d:
        errors.append(f"fflow: {d['_error']}")
    else:
        for line in d.get("data", {}).get("klines", []):
            p = line.split(",")
            main_net = float(p[1])
            entry = dict(
                date=p[0],
                main_net_yuan=main_net,
                main_net_wan=round(abs(main_net) / 10000, 2),
                direction="净流入" if main_net >= 0 else "净流出",
            )
            fflow_history.append(entry)
        if fflow_history:
            fflow = fflow_history[-1]
            if kline and kline["amount"] > 0:
                fflow["ratio_pct"] = round(abs(fflow["main_net_yuan"]) / kline["amount"] * 100, 2)
except Exception as e:
    errors.append(f"fflow parse: {e}")

# ── 4) News + announcements (eastmoney search API) ──
search_param = json.dumps({
    "uid": "", "keyword": CODE,
    "type": ["cmsArticleWebOld"],
    "client": "web", "clientType": "web", "clientVersion": "curr",
    "param": {"cmsArticleWebOld": {
        "searchScope": "default", "sort": "default",
        "pageIndex": 1, "pageSize": 10,
    }},
}, ensure_ascii=False)
raw = fetch(
    f"https://search-api-web.eastmoney.com/search/jsonp"
    f"?cb=jQuery&param={quote(search_param)}",
    headers={**HEADERS, "Referer": "https://so.eastmoney.com/"},
)
news = []
event_keywords = [
    "股东会", "临时股东会", "募投", "关联交易", "债券", "科创债",
    "发行", "投资", "战略投资", "分红", "业绩", "年报", "季报",
    "人形机器人", "募集", "对外投资", "收购", "增持", "减持",
    "定增", "配股", "回购", "重组", "限售股", "解禁",
]
try:
    m = re.search(r"jQuery\((.*)\)", raw)
    if m:
        sd = json.loads(m.group(1))
        articles = sd.get("result", {}).get("cmsArticleWebOld", {})
        if isinstance(articles, dict):
            articles = articles.get("list", [])
        for a in (articles or [])[:20]:
            if isinstance(a, dict):
                title = re.sub(r"<[^>]+>", "", a.get("title", ""))
                date = (a.get("date", "") or "")[:10]
                url = a.get("url", "")
                relevant = any(kw in title for kw in event_keywords)
                news.append(dict(title=title, date=date, url=url, relevant=relevant))
    elif "_error" in raw:
        errors.append(f"news: {json.loads(raw).get('_error','unknown')}")
except Exception as e:
    errors.append(f"news parse: {e}")

# ── 5) Sector boards (top 50 industry boards) ──
raw = fetch("https://push2.eastmoney.com/api/qt/clist/get"
            "?fs=m:90+t:2&fields=f2,f3,f12,f14&fid=f3&pn=1&pz=50&po=1")
boards = []
try:
    d = json.loads(raw)
    if "_error" in d:
        errors.append(f"boards: {d['_error']}")
    else:
        diff = d.get("data", {}).get("diff", {})
        items = diff.values() if isinstance(diff, dict) else (diff or [])
        for v in items:
            if isinstance(v, dict):
                f3 = v.get("f3", 0) or 0
                boards.append(dict(
                    name=v.get("f14", ""),
                    change_pct=round(f3 / 100, 2) if isinstance(f3, int) and abs(f3) > 100 else f3,
                    code=v.get("f12", ""),
                ))
except Exception as e:
    errors.append(f"boards parse: {e}")

# ── Assemble ──
output = {
    "code": CODE,
    "secid": SECID,
    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "kline": kline,
    "kline_history": kline_list,
    "snapshot": snapshot,
    "fflow": fflow,
    "fflow_history": fflow_history,
    "news_all": news,
    "news_relevant": [n for n in news if n.get("relevant")],
    "boards_top20": boards[:20],
    "errors": errors,
    "status": {
        "kline": "ok" if kline else "failed",
        "snapshot": "ok" if snapshot and snapshot.get("price") else "empty",
        "fflow": "ok" if fflow else "failed",
        "news": f"ok ({len(news)} articles)" if news else "empty",
        "boards": f"ok ({len(boards)} boards)" if boards else "failed",
    },
}

outfile = os.path.join(OUTDIR, f"{CODE}.json")
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Saved: {outfile}")
print(f"Status: {json.dumps(output['status'], ensure_ascii=False)}")
if errors:
    print(f"Errors: {errors}")
