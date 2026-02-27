---
name: market-sentry
description: Multi-asset monitor with narrative daily briefs, anomaly alerts, auditable evidence packs, and Feishu push. Use when the user mentions market monitoring, stock briefs, price alerts, anomaly detection, portfolio tracking, daily digest, A-stock analysis, or Feishu notifications for financial assets.
metadata: {"openclaw":{"emoji":"📈","skillKey":"market-sentry"}}
---

# market-sentry

You are a financial monitoring and briefing system. A-shares, US stocks, crypto.

## ⚠️ MANDATORY URLs — VISIT ALL OF THESE FOR EACH STOCK ⚠️

For ANY brief (single or portfolio), you MUST visit these URLs. "资金面数据暂缺" is NEVER acceptable — the data IS available at the URLs below.

### 688306 均普智能

| # | Data | URL |
|---|------|-----|
| 1 | K-line | `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.688306&klt=101&fqt=1&end=20500101&lmt=5&fields1=f1,f2,f3,f4,f5,f6,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61` |
| 2 | **资金流** | `https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid=1.688306&klt=101&lmt=5&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58` |
| 3 | 量比 | `https://push2.eastmoney.com/api/qt/stock/get?secid=1.688306&fields=f57,f58,f50` |
| 4 | 公告 | `https://np-anotice-stock.eastmoney.com/api/security/ann?cb=jQuery&stock_list=688306&page_size=10&page_index=1&ann_type=A&begin_time=2025-12-01&end_time=2026-12-31` |

### 600519 贵州茅台

| # | Data | URL |
|---|------|-----|
| 1 | K-line | `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600519&klt=101&fqt=1&end=20500101&lmt=5&fields1=f1,f2,f3,f4,f5,f6,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61` |
| 2 | **资金流** | `https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid=1.600519&klt=101&lmt=5&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58` |
| 3 | 量比 | `https://push2.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f57,f58,f50` |
| 4 | 公告 | `https://np-anotice-stock.eastmoney.com/api/security/ann?cb=jQuery&stock_list=600519&page_size=10&page_index=1&ann_type=A&begin_time=2025-12-01&end_time=2026-12-31` |

**Parsing URL #2 (资金流)**: `data.klines` → `"date,主力净流入(元),小单,中单,大单,超大单,主力净占比%,小单占比%"`. Pick entry matching your target date. Column 1 = 主力净流入(元), `/10000` = 万元. Column 6 = 占比%.

**Parsing URL #3 (量比)**: `f50` / 100 = 量比.

**Parsing URL #4 (公告)**: JSONP wrapper. `data.list[].title_ch` + `notice_date`.

---

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

**⚠️ PORTFOLIO MODE**: When generating briefs for multiple stocks (e.g. "投资组合简报", "昨日简报"), you MUST complete ALL URLs + output for ONE stock before starting the next. Do NOT batch kline fetches for all stocks first — that causes you to skip fflow. Instead: fetch all 4 URLs for stock A → write brief A → then fetch all 4 URLs for stock B → write brief B.

For each CN_A asset, execute ALL steps. Do NOT skip any step.

Determine `{secid}`: code starts with 6 → `1.{code}` (SH), starts with 0/3 → `0.{code}` (SZ).

### Step 1: Fetch K-line — visit this URL

```
https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&klt=101&fqt=1&end=20500101&lmt=5&fields1=f1,f2,f3,f4,f5,f6,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61
```

Response: `data.klines` array. Each line = `"date,open,close,high,low,volume,amount,amplitude%,change%,change_amt,turnover%"`.
Use the **LAST** entry. Extract: date, close(=price), change_pct, high, low, amount(元), turnover%.
`amount` in 元: `/1e8` = 亿元.

### ⚠️ Step 2: Fetch Fund Flow — YOU MUST VISIT THIS URL (资金流)

**This step is MANDATORY.** Without it you will output "资金面数据暂缺" which is WRONG.

**IMPORTANT**: Use `push2his` (historical), NOT `push2` (real-time). The real-time endpoint only returns TODAY's data. For "昨日简报" you NEED the historical endpoint which returns multiple days.

```
https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid={secid}&klt=101&lmt=5&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58
```

Response: `data.klines` array. Each line = `"date,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入,主力净占比%,小单净占比%"` (流入 in 元, 占比 in %).
Returns last 5 trading days. Pick the entry matching your target date (same date as the kline entry you're using from Step 1).

Column 1 (after date) = 主力净流入 (元).
Column 6 = 主力净占比 (%, already calculated, can use directly as `ratio_pct`).

Calculate:
- `main_net_wan = abs(column1) / 10000` (万元)
- `direction`: column1 > 0 → "净流入", < 0 → "净流出"
- `ratio_pct`: use column6 directly (it's already a percentage), OR `= abs(column1) / amount_from_Step1 * 100`
- `retail_direction`: inverse of main (主力净流出 → 散户净流入)

**Example** (688306 on 2026-02-26): `"2026-02-26,-28839271.0,..."` → 主力净流出 `2883.93` 万元, 占比 `-20.15%`

### Step 3: Fetch Snapshot — 量比 (vol_ratio)

```
https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f57,f58,f50
```

`f50` = 量比 (raw integer, divide by 100). Example: `f50=170` → 量比 `1.70`.
`f58` = stock name.

### Step 4: Fetch Announcements

```
https://np-anotice-stock.eastmoney.com/api/security/ann?cb=jQuery&stock_list={code}&page_size=10&page_index=1&ann_type=A&begin_time={90_days_ago}&end_time={today}
```

Response: JSONP. Parse `data.list[]`. Each: `title_ch`, `notice_date`, `art_code`, `columns[].column_name`.
Rewrite announcement titles as natural event sentences.

### Step 5: Fetch Sector Boards (optional, for 板块背离/同步)

```
https://push2.eastmoney.com/api/qt/clist/get?fs=m:90+t:2&fields=f2,f3,f12,f14&fid=f3&pn=1&pz=50&po=1
```

`f14` = board name, `f3` = change% (raw int, /100). Find stock's sector, compare direction.

### Step 6: Build headline

Apply headline generation rules (above) using fund flow data (Step 2) and announcement titles (Step 4).

### Step 7: Write narrative paragraph

Weave ALL data into ONE paragraph:
1. "最新价格：{price}元（{pct}%），{M}月{D}日，"
2. "{name}主力资金{方向}{main_net_wan}万元，占总成交额{ratio}%。" ← **from Step 2**
3. "主力资金呈{方向}状态，散户资金呈现{inverse}。"
4. "走势与所属的{sector}板块（{sector_pct}%）{背离/同步}。" (omit if unavailable)
5. "交易量{活跃/萎缩/持平}，量比为{f50}。" ← **from Step 3**

### Step 8: Write event paragraphs

From Step 4 announcements. Deduplicate. Most recent first. Max 5.
`{date}，公司{event_description}。`

### Step 9: Push + Save

1. Assemble full narrative text (headline + ^解读 + paragraph + events)
2. Push to Feishu (Mode A: message tool, Mode B: curl card JSON)
3. Save brief to `{baseDir}/data/briefs/YYYY-MM-DD/{asset_id}.md`
4. Save EvidencePack to `{baseDir}/data/evidence_packs/B-{asset_id}-{YYYY-MM-DD}/v1.json`

### Optional: fetch_cn.py script

If you have shell/terminal access, run `python3 {baseDir}/fetch_cn.py {code}` first. It fetches all sources and saves to `{baseDir}/data/fetched/{code}.json`. Then read that file instead of visiting URLs individually.

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

### `/ms brief portfolio` or "投资组合简报" or "昨日简报"

**CRITICAL**: Do NOT try to process all stocks at once. Process ONE stock at a time, completing ALL steps (including fund flow URL #2) for each stock before moving to the next.

Execute as sequential individual briefs:
1. Run `/ms brief 688306` — visit ALL 4 URLs, generate narrative, push
2. Run `/ms brief 600519` — visit ALL 4 URLs, generate narrative, push
3. Run `/ms brief AAPL` — fetch quote + news, generate narrative, push
4. Run `/ms brief BTC` — fetch quote, generate narrative, push

Each stock MUST have its own complete data collection before writing its brief. Do NOT batch kline fetches first then come back for fflow — that causes "资金面数据暂缺".

### `/ms digest start`

**CN_A:**
```bash
openclaw cron add \
  --name "market-sentry:digest-cn" \
  --cron "0 15 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --no-deliver \
  --message "For each CN_A symbol in watch_rules: 1) Run: python3 {baseDir}/fetch_cn.py {code} 2) Read {baseDir}/data/fetched/{code}.json 3) Follow SKILL.md Output Contract to build narrative brief from the JSON data 4) Push to Feishu + save brief.md + save EvidencePack. STRICT: output ONLY the narrative text. NO bullet lists, NO section headers, NO [收盘] format, NO E1/E2/E3 labels." \
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
| 东方财富搜索 API | Fail/empty | "暂无近期相关公告或新闻。" | E2+E3 unavailable |
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
