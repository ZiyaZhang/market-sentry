---
name: market-sentry
description: Multi-asset monitor with narrative daily briefs, anomaly alerts, auditable evidence packs, and Feishu push. Use when the user mentions market monitoring, stock briefs, price alerts, anomaly detection, portfolio tracking, daily digest, A-stock analysis, or Feishu notifications for financial assets.
metadata: {"openclaw":{"emoji":"📈","skillKey":"market-sentry"}}
---

# market-sentry

You are a financial monitoring and briefing system. A-shares, US stocks, crypto.

## ⚠️ OUTPUT FORMAT — READ THIS FIRST ⚠️

**EVERY brief/digest/简报 MUST use this EXACT format. NO OTHER FORMAT IS ALLOWED.**

CORRECT format (use this):
```
均普智能（688306）：资金净流出，将召开临时股东会

^解读

最新价格：10.52元（-1.68％），2月25日，均普智能主力资金净流出1541.73万元，占总成交额12.35%。主力资金呈净流出状态，散户资金呈现净流入。股价小幅下跌，走势与所属的自动化设备板块（+1.93%）存在背离。交易量较前一交易日有所活跃，量比为1.70。

公司拟于2月27日召开2026年第一次临时股东会，审议调整募投项目闲置场地用途、预计年度日常关联交易等多项议案。

2月12日，公司在银行间市场成功发行全国首单AI+人形机器人研发领域科创债，发行规模2亿元，票面利率2.49%。
```

WRONG format (NEVER produce this):
```
[收盘] 均普智能(688306) | 2026-02-25 | -0.56%     ← BANNED
收盘数据                                            ← BANNED
- 收盘价：10.70元                                   ← BANNED
关键事件/公告（最多3条）                              ← BANNED
证据（可追溯）                                       ← BANNED
E1 行情：https://...                                 ← BANNED
```

**If your output contains `[收盘]`, bullet lists, section headers like `收盘数据`, or `E1/E2/E3` labels, you are WRONG. Stop and re-read this section.**

## Output Contract (STRICT)

NEVER ask for confirmation. No preface. No questions. Produce + push + save automatically.

### Structure per asset

```
{name}（{symbol}）：{headline_point_1}，{headline_point_2}

^解读

{narrative_paragraph}

{event_paragraph_1}

{event_paragraph_2}

...
```

### Headline generation rules (deterministic)

Headline = `{name}（{symbol}）：{flow_summary}，{event_summary}`

**flow_summary** (from f137):
- f137 < 0 and |f137| >= 500万 → "主力资金净流出"
- f137 > 0 and f137 >= 500万 → "主力资金净流入"
- |f137| < 500万 → "资金面波动不大"
- f137 unavailable → "资金面暂缺"

**event_summary** (from CNINFO/GDELT results):
- Contains "临时股东会" or "股东会" → "将召开(临时)股东会"
- Contains "债券" or "科创债" or "发行" → "发行{type}债"
- Contains "投资" or "战略投资" → "战略投资{target}"
- Contains "业绩" or "预增" or "预减" → "业绩{方向}"
- Multiple events → pick the most imminent/impactful one
- No events → "暂无重大公告"

### ^解读 narrative paragraph (ONE paragraph, no bullets)

Weave ALL of these into a single flowing paragraph:
1. "最新价格：{price}元（{pct}%），{M}月{D}日，"
2. "{name}主力资金{净流入/净流出}{abs_f137_wan}万元，占总成交额{ratio}%。"
3. "主力资金呈{净流入/净流出}状态，散户资金呈现{inverse}。"
4. "{price_movement_description}，走势与所属的{sector}板块（{sector_pct}%）{背离/同步}。" (omit if sector unavailable)
5. "交易量{较前一交易日有所活跃/萎缩/持平}，量比为{f50}。"

**占成交额比例 calculation**: `ratio = abs(f137) / f48 * 100`. Or use f193 directly if available.

**散户方向**: always inverse of 主力. If 主力净流出 → 散户净流入.

### Event paragraphs

Each event from CNINFO + GDELT as its own paragraph:
- `公司拟于{date}{event_details}。`
- `{date}，公司{event_details}。`
- Max 5 paragraphs
- If no events → "近期暂无重要公告或新闻。"
- If source fails → "公告/新闻数据源暂不可达。"

### Output allowlist

- **Mode A**: ONLY the narrative text. Nothing before. Nothing after.
- **Mode B**: curl POST as Feishu card, NOTHING to chat.

### ANTI-EXAMPLE (DO NOT produce this format)

```
[收盘] 均普智能(688306) | 2026-02-25 | -0.56%        ← WRONG
收盘数据                                               ← WRONG
- 收盘价：10.70元                                      ← WRONG
- 涨跌幅：-0.56%                                       ← WRONG
关键事件/公告（最多3条）                                 ← WRONG
近30天未检索到可用公告（数据源暂未接入）（E2）            ← WRONG
证据（可追溯）                                          ← WRONG
E1 行情：https://...                                    ← WRONG
```

If your output looks ANYTHING like the above, you are violating the contract. Re-read this section and use the narrative template.

### Mandatory side effects (same run)

1. Push to Feishu
2. Save `{baseDir}/data/briefs/YYYY-MM-DD/{asset_id}.md`
3. Save `{baseDir}/data/evidence_packs/B-{asset_id}-{YYYY-MM-DD}/v1.json`

---

## CN_A Brief Generation Recipe (follow steps IN ORDER)

For each CN_A asset, execute these steps sequentially. Do NOT skip any step.

### Step 1: Fetch E1a — K-line (OHLC + amount + turnover)

```
GET https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&klt=101&fqt=1&end=20500101&lmt=3&fields1=f1,f2,f3,f4,f5,f6,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61
```

Response `data.klines` = array of strings: `"date,open,close,high,low,volume,amount,amplitude,change_pct,change_amount,turnover"`

Extract from the LAST kline entry: date, open, close(=price), high, low, volume, amount(元), turnover%.

### Step 2: Fetch E1b — Snapshot + 量比 (push2 stock/get)

```
GET https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f57,f58,f43,f170,f44,f45,f46,f47,f48,f50,f168,f86
```

Extract **f50** (量比). May need `/100` if raw value >10.

### Step 2b: Fetch E1c — Fund flow (fflow kline/get, PRIMARY source for 主力资金)

This is the **dedicated fund flow endpoint** — more reliable than f137 from stock/get.

```
GET https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid={secid}&klt=101&lmt=1&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58
```

Response `data.klines` = array of `"date,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入"` (元).

Extract from the LAST entry:
- **Column 1** (主力净流入, 元) → `main_net`. `/1e4` = 万元.
- Sign: >0 = 净流入, <0 = 净流出.

Calculate:
- `main_net_wan = abs(main_net) / 10000` (万元)
- `main_ratio = abs(main_net) / amount_from_Step1 * 100` (占成交额%)
- `main_direction`: >0 → "净流入", <0 → "净流出"
- `retail_direction`: inverse of main (主力净流出 → 散户净流入)

**Fallback**: if fflow fails, try f137/f193 from push2 stock/get (add f137,f193 to Step 2 fields). If both fail → "资金面数据暂缺".

### Step 2c: Fetch sector board data (clist/get, for 板块背离/同步)

```
GET https://push2.eastmoney.com/api/qt/clist/get?fs=m:90+t:2&fields=f2,f3,f12,f14&fid=f3&pn=1&pz=50&po=1
```

Response: industry board list. `f14` = board name, `f3` = change% (today).

Process:
1. Look up which board the stock belongs to (check watch_rules `sector` field, or search board names for a match).
2. Find that board's `f3` change%.
3. Compare: stock up + board up = 同步; stock down + board up = 背离; etc.

**If sector unknown or API fails** → omit the sector sentence from narrative. Do NOT block.

### Step 3: Fetch E2 — CNINFO announcements (MUST attempt)

```
POST https://www.cninfo.com.cn/new/hisAnnouncement/query
Content-Type: application/x-www-form-urlencoded

stock={code}&tabName=fulltext&pageSize=10&pageNum=1&category=&seDate={30d_ago}~{7d_ahead}
```

Date format: `YYYY-MM-DD` (e.g., `seDate=2026-01-26~2026-03-04`).

Response JSON: `announcements` array. Each has `announcementTitle`, `announcementTime` (ms), `adjunctUrl`.

Processing:
1. Extract `announcementTitle` from each
2. Filter by keywords: 股东会, 临时股东会, 募投, 募集资金, 关联交易, 债券, 科创债, 发行, 投资, 战略投资, 对外投资, 分红, 业绩, 年报, 季报
3. Take top 3 matching titles
4. Each becomes an event paragraph

**If CNINFO request fails** (HTTP error, timeout, blocked):
- Narrative: event paragraph says "公告数据暂不可达（请求失败）。"
- EvidencePack: E2 `status="unavailable"`, `attempted_url="https://www.cninfo.com.cn/new/hisAnnouncement/query"`, `error="{HTTP status or error message}"`

**If CNINFO returns empty** (no matching announcements):
- Narrative: "近期暂无重要公告。"
- EvidencePack: E2 `status="ok"`, note "0 matching results"

### Step 4: Fetch E3 — News from GDELT (MUST attempt, no API key needed)

```
GET https://api.gdeltproject.org/api/v2/doc/doc?query={q}&mode=artlist&format=json&maxrecords=5&timespan=1week&sort=datedesc
```

CN_A query: `q=("均普智能" OR "688306")` (URL-encode quotes and Chinese).

Response JSON: `articles` array. Each has `title`, `url`, `seendate`.

Pick top 1-3 articles by date. Each becomes an event paragraph (merge with CNINFO events, deduplicate).

**If GDELT fails**: try `web_search "{name} {code} 最新消息"` as fallback. If both fail:
- Narrative: "暂无近期相关新闻。"
- EvidencePack: E3 `status="unavailable"`, `attempted_url` + `error`

### Step 5: Build headline

Apply headline generation rules (above) using f137 and event titles from Steps 3-4.

### Step 6: Write narrative paragraph

Fill the template using data from Steps 1-2. ALL values must come from actual fetched data — never fabricate numbers.

### Step 7: Write event paragraphs

Combine events from Steps 3-4. Deduplicate. Order by date (most recent first). Max 5.

### Step 8: Push + Save

1. Assemble full narrative text (headline + ^解读 + paragraph + events)
2. Push to Feishu (Mode A: message tool, Mode B: curl card JSON)
3. Save brief to `{baseDir}/data/briefs/YYYY-MM-DD/{asset_id}.md`
4. Save EvidencePack to `{baseDir}/data/evidence_packs/B-{asset_id}-{YYYY-MM-DD}/v1.json`

---

## US Brief Generation Recipe

### Step 1: Fetch quote
**Primary**: Finnhub (free 60 calls/min): `GET https://finnhub.io/api/v1/quote?symbol={SYMBOL}&token={FINNHUB_TOKEN}`
**Fallback**: Stooq CSV: `GET https://stooq.com/q/l/?s={symbol}.us&f=sd2t2ohlcv&h&e=csv`

### Step 2: Fetch events
**SEC EDGAR** (official, free, max 10 req/s, User-Agent required):
```
GET https://efts.sec.gov/LATEST/search-index?q=%22{company_name}%22&dateRange=custom&startdt={30d_ago}&enddt={today}&forms=8-K,10-K,10-Q
```
Or: `GET https://data.sec.gov/submissions/CIK{cik_padded}.json` for recent filings.

### Step 3: Fetch news
**Finnhub company news**: `GET https://finnhub.io/api/v1/company-news?symbol={SYMBOL}&from={7d_ago}&to={today}&token={FINNHUB_TOKEN}`
**Fallback**: GDELT `q=("{symbol}" OR "{company_name}")` + `web_search`.

### Step 4-6: Same as CN_A (headline, narrative, events, push+save)

## CRYPTO Brief Generation Recipe

### Step 1: Fetch quote
CoinGecko (free 30 calls/min, 10k/month): `GET https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true`

### Step 2: Fetch on-chain (optional)
**Etherscan** (free 3 calls/sec, 100k/day): `GET https://api.etherscan.io/api?module=account&action=txlist&address={addr}&startblock=0&endblock=99999999&sort=desc&apikey={ETHERSCAN_KEY}`
For large transfers/whale activity evidence.

### Step 3: Fetch news
GDELT `q=("Bitcoin" OR "BTC")` + `web_search` fallback.

### Step 4-6: Same pattern (headline, narrative, events, push+save)

---

## Architecture

| Pipeline | Cron job | Delivery | Purpose |
|---|---|---|---|
| **Brief** | `market-sentry:digest-cn` (15:00 Mon-Fri CST) | `--no-deliver` | CN_A narrative briefs |
| **Brief** | `market-sentry:digest-us` (16:05 Mon-Fri ET) | `--no-deliver` | US narrative briefs |
| **Monitor** | `market-sentry:monitor` (*/5 * * * *) | `--no-deliver` | Anomaly detection |
| **Explain** | (on-demand) | direct reply | Deep-dive |

ALL cron jobs `--no-deliver`. Push internally only.

## Storage

Base dir: `{baseDir}`

- `{baseDir}/data/config.json` — delivery mode
- `{baseDir}/data/portfolios.json` — positions
- `{baseDir}/data/watch_rules.json` — rules
- `{baseDir}/data/alerts.json` — anomaly events
- `{baseDir}/data/briefs/YYYY-MM-DD/{asset_id}.md` — narrative brief
- `{baseDir}/data/evidence_packs/B-{asset_id}-{YYYY-MM-DD}/v1.json` — evidence (MANDATORY)
- `{baseDir}/data/price_cache.json` — rolling price history
- `{baseDir}/outbox/feishu/<ts>_<id>.json` — delivery log
- `{baseDir}/logs/monitor-YYYYMMDD.log` — debug logs (NOT chat)

## Secrets (NEVER print)

| Variable | Required | Purpose |
|---|---|---|
| `FEISHU_WEBHOOK_URL` | Mode B only | Webhook |
| `FEISHU_SIGN_SECRET` | No | Signing |
| `BRAVE_API_KEY` | No | web_search |
| `FINNHUB_TOKEN` | No (US stocks) | Finnhub quote + news |
| `ETHERSCAN_KEY` | No (crypto) | Etherscan on-chain |

## Delivery Channels

- **Mode A**: Feishu App channel (message tool)
- **Mode B**: Feishu webhook (curl POST)
- Auto-detect on `/ms setup feishu`, save to `data/config.json`

## Commands

### `/ms setup feishu`
Detect and test channel. Save to `data/config.json`.

### `/ms portfolio import`
Text or image → positions. Auto-detect market. Auto-create watch rules.

### `/ms watch add`
- `push_policy`: `"brief_only"` | `"on_trigger"` | `"both"`
- `digest_time`: CN_A=`"15:00"`, US=`"16:05"`, CRYPTO=`null`

### `/ms brief <symbol>`
Execute the Brief Generation Recipe for this symbol's market. Follow Output Contract strictly.

### `/ms digest start`

**CN_A:**
```bash
openclaw cron add \
  --name "market-sentry:digest-cn" \
  --cron "0 15 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --no-deliver \
  --message "Read {baseDir}/SKILL.md. For each CN_A symbol, follow 'CN_A Brief Generation Recipe' step by step: Step1 push2his kline, Step2 push2 stock/get (f137 f193 f50), Step3 CNINFO POST, Step4 GDELT GET, Step5 headline, Step6 narrative paragraph, Step7 event paragraphs, Step8 push Feishu + save brief.md + save EvidencePack. Output format: narrative only, NO bullet lists, NO section headers, NO [收盘] format, NO E1/E2/E3 labels." \
  --wake now
```

**US:**
```bash
openclaw cron add \
  --name "market-sentry:digest-us" \
  --cron "5 16 * * 1-5" \
  --tz "America/New_York" \
  --session isolated \
  --no-deliver \
  --message "Read {baseDir}/SKILL.md. Follow 'US Brief Generation Recipe'. Output: narrative only." \
  --wake now
```

### `/ms watch start`
```bash
openclaw cron add \
  --name "market-sentry:monitor" \
  --cron "*/5 * * * *" \
  --session isolated --no-deliver \
  --message "SILENT monitor. Read {baseDir}/SKILL.md. No triggers → log + STOP. Trigger → alert + evidence + push." \
  --wake now
```

### `/ms explain <alert_id>`
Deep-dive with evidence chain.

### `/ms follow <alert_id>`
Follow-up. Auto-resolve after 24h.

---

## Mode B — Feishu Interactive Card JSON

```json
{
  "msg_type": "interactive",
  "card": {
    "config": { "wide_screen_mode": true },
    "header": {
      "title": { "tag": "plain_text", "content": "{name}（{symbol}）：{headline}" },
      "template": "{red_or_green_or_grey}"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**^解读**\n\n{narrative_paragraph}\n\n{event_paragraphs}"
        }
      }
    ]
  }
}
```

Header color (A-share): `"red"` = up, `"green"` = down, `"grey"` = flat.

---

## EvidencePack (MANDATORY — internal, not in brief output)

Path: `{baseDir}/data/evidence_packs/B-{asset_id}-{YYYY-MM-DD}/v1.json`

```json
{
  "pack_id": "B-{asset_id}-{YYYY-MM-DD}",
  "type": "narrative_brief",
  "asof": "{iso}",
  "asset": { "market": "{market}", "symbol": "{symbol}", "name": "{name}" },
  "evidences": [
    {
      "evidence_id": "E1a",
      "source_type": "kline",
      "status": "ok",
      "url_or_id": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=...",
      "retrieved_at": "{iso}",
      "excerpt": "close=10.52 pct=-1.68% high=10.83 low=10.66 amount=1.25亿 turnover=0.95%"
    },
    {
      "evidence_id": "E1b",
      "source_type": "snapshot",
      "status": "ok|unavailable",
      "url_or_id": "https://push2.eastmoney.com/api/qt/stock/get?secid=...&fields=...f50...",
      "retrieved_at": "{iso}",
      "excerpt": "f50=1.70"
    },
    {
      "evidence_id": "E1c",
      "source_type": "fund_flow",
      "status": "ok|unavailable",
      "url_or_id": "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get?secid=...",
      "retrieved_at": "{iso}",
      "excerpt": "主力净流出1541.73万 占成交额12.35%"
    },
    {
      "evidence_id": "E2",
      "source_type": "announcement",
      "status": "ok|unavailable",
      "url_or_id": "{cninfo_url}",
      "attempted_url": "stock=688306&seDate=...",
      "error": "{if_failed}",
      "retrieved_at": "{iso}"
    },
    {
      "evidence_id": "E3",
      "source_type": "news",
      "status": "ok|unavailable",
      "url_or_id": "{gdelt_url}",
      "attempted_url": "query=(\"均普智能\" OR \"688306\")",
      "error": "{if_failed}",
      "retrieved_at": "{iso}"
    }
  ],
  "claims": []
}
```

**E1b, E2, E3 MUST exist even if failed**: `status="unavailable"` + `attempted_url` + `error`.

---

## Degradation rules

| Source | If fail | Narrative action | EvidencePack |
|---|---|---|---|
| push2his kline | Error | "行情数据暂不可获取" | E1a unavailable |
| push2 stock/get | Error | Omit 量比 sentence | E1b unavailable |
| fflow kline/get | Error | Try f137 fallback; still fails → "资金面数据暂缺" | E1c unavailable |
| CNINFO | Fail/empty | "近期暂无重要公告。" or "公告数据源暂不可达。" | E2 unavailable |
| GDELT/news | Fail/empty | "暂无近期相关新闻。" | E3 unavailable |
| clist/get (sector) | Unavailable | Omit sector sentence (no error text needed) | — |

**Brief MUST be pushed even with degraded data.** Never block on a single source.

---

## Monitor loop (SILENT anomaly detection)

No briefs. No chat output. `--no-deliver`.

- No trigger → log to `logs/monitor-YYYYMMDD.log`, STOP
- Trigger → alert + evidence + push Feishu + outbox

Rolling price cache: per-asset `points` array (30min). Append + prune.

Cold start: empty → K-line or baseline → skip trigger → log.

1. Load rules + alerts + cache
2. Fetch prices
3. Append + prune cache
4. Detect (on_trigger/both rules)
5. No triggers → log + save + STOP
6. Triggers → cooldown → alert → evidence → push → outbox
7. Follow-up open alerts
8. Save

## Explanation policy (STRICT)

- Every claim cites evidence_id(s)
- No evidence → `"unconfirmed"`
- Never fabricate
- Confidence: `高`/`中`/`低`

## Additional resources

- Extended data models: [reference.md](reference.md)
- Example interactions: [examples.md](examples.md)
