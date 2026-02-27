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

# ── 2) Real-time snapshot (f50 量比, f137/f193 fund flow, name) ──
# f43/f170 are unreliable (raw int encoding varies) — use kline for price/pct instead.
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
        f50_raw = dd.get("f50", 0) or 0
        vol_ratio = round(f50_raw / 100, 2) if isinstance(f50_raw, (int, float)) else 0
        f193_raw = dd.get("f193")
        main_pct = round(f193_raw / 100, 2) if isinstance(f193_raw, (int, float)) and f193_raw else None
        snapshot = dict(
            code=dd.get("f57", CODE),
            name=dd.get("f58", ""),
            vol_ratio=vol_ratio,
            f137=dd.get("f137"),
            f193=main_pct,
            f48=dd.get("f48"),
        )
except Exception as e:
    errors.append(f"snapshot parse: {e}")

# ── 3) Fund flow (fflow) — HISTORICAL endpoint for 主力净流入 ──
# push2his (historical) returns multiple days; push2 (real-time) only returns today.
raw = fetch(f"https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
            f"?secid={SECID}&klt=101&lmt=5"
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
            ratio_from_api = float(p[6]) if len(p) > 6 else None
            entry = dict(
                date=p[0],
                main_net_yuan=main_net,
                main_net_wan=round(abs(main_net) / 10000, 2),
                direction="净流入" if main_net >= 0 else "净流出",
            )
            if ratio_from_api is not None:
                entry["ratio_pct"] = round(abs(ratio_from_api), 2)
            fflow_history.append(entry)
        if fflow_history:
            fflow = fflow_history[-1]
            if "ratio_pct" not in fflow and kline and kline["amount"] > 0:
                fflow["ratio_pct"] = round(abs(fflow["main_net_yuan"]) / kline["amount"] * 100, 2)
except Exception as e:
    errors.append(f"fflow parse: {e}")

# ── 4a) Announcements — np-anotice API (PRIMARY, most reliable) ──
today_str = time.strftime("%Y-%m-%d")
three_months_ago = time.strftime("%Y-%m-%d", time.localtime(time.time() - 90 * 86400))
raw = fetch(
    f"https://np-anotice-stock.eastmoney.com/api/security/ann"
    f"?cb=jQuery&stock_list={CODE}&page_size=10&page_index=1"
    f"&ann_type=A&begin_time={three_months_ago}&end_time={today_str}",
    headers={**HEADERS, "Referer": "https://data.eastmoney.com/"},
)
announcements = []
try:
    m_ann = re.search(r"jQuery\w*\((.*)\)\s*$", raw, re.DOTALL)
    if m_ann:
        ad = json.loads(m_ann.group(1))
        for item in ad.get("data", {}).get("list", [])[:15]:
            title = item.get("title_ch", "")
            date = (item.get("notice_date", "") or "")[:10]
            art_code = item.get("art_code", "")
            columns = [c.get("column_name", "") for c in item.get("columns", [])]
            ann_url = f"https://data.eastmoney.com/notices/detail/{CODE}/{art_code}.html" if art_code else ""
            announcements.append(dict(
                title=title, date=date, url=ann_url,
                art_code=art_code, categories=columns,
            ))
    elif "_error" in raw:
        errors.append(f"announcements: {json.loads(raw).get('_error', 'unknown')}")
except Exception as e:
    errors.append(f"announcements parse: {e}")

# ── 4b) News — eastmoney search API (SECONDARY, may be empty) ──
stock_name = snapshot.get("name", "") if snapshot else ""
search_keywords = [CODE]
if stock_name:
    search_keywords.append(stock_name)

news = []
event_keywords = [
    "股东会", "临时股东会", "募投", "关联交易", "债券", "科创债",
    "发行", "投资", "战略投资", "分红", "业绩", "年报", "季报",
    "人形机器人", "募集", "对外投资", "收购", "增持", "减持",
    "定增", "配股", "回购", "重组", "限售股", "解禁",
    "财报", "预告", "快报", "营收", "利润", "分配",
]
seen_titles = set()

for kw in search_keywords:
    search_param = json.dumps({
        "uid": "", "keyword": kw,
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
    try:
        m_news = re.search(r"jQuery\w*\((.*)\)\s*$", raw, re.DOTALL)
        if m_news:
            sd = json.loads(m_news.group(1))
            articles = sd.get("result", {}).get("cmsArticleWebOld", {})
            if isinstance(articles, dict):
                articles = articles.get("list", [])
            for a in (articles or [])[:20]:
                if isinstance(a, dict):
                    title = re.sub(r"<[^>]+>", "", a.get("title", ""))
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    date = (a.get("date", "") or "")[:10]
                    url = a.get("url", "")
                    relevant = any(ek in title for ek in event_keywords)
                    news.append(dict(title=title, date=date, url=url, relevant=relevant))
    except Exception as e:
        errors.append(f"news parse({kw}): {e}")

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
                pct = round(f3 / 100, 2) if isinstance(f3, (int, float)) else 0
                boards.append(dict(
                    name=v.get("f14", ""),
                    change_pct=pct,
                    code=v.get("f12", ""),
                ))
except Exception as e:
    errors.append(f"boards parse: {e}")

# ── Assemble ──
all_events = announcements + [n for n in news if n.get("relevant")]
output = {
    "code": CODE,
    "secid": SECID,
    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    "kline": kline,
    "kline_history": kline_list,
    "snapshot": snapshot,
    "fflow": fflow,
    "fflow_history": fflow_history,
    "announcements": announcements,
    "news_all": news,
    "news_relevant": [n for n in news if n.get("relevant")],
    "events_merged": all_events,
    "boards_top20": boards[:20],
    "errors": errors,
    "status": {
        "kline": "ok" if kline else "failed",
        "snapshot": "ok" if snapshot and snapshot.get("name") else "empty",
        "fflow": "ok" if fflow else "failed",
        "announcements": f"ok ({len(announcements)})" if announcements else "empty",
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
