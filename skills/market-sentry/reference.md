# market-sentry Reference

## Data Models

### Portfolio (`portfolios.json`)

```json
{
  "portfolios": [
    {
      "portfolio_id": "P-001",
      "name": "Main Portfolio",
      "positions": [
        {
          "asset_id": "688306",
          "symbol": "688306",
          "name": "均普智能",
          "asset_class": "stock",
          "market": "CN_A",
          "qty": 1000,
          "cost_basis": 10.50,
          "tags": ["AI", "机器人"]
        },
        {
          "asset_id": "AAPL",
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "asset_class": "stock",
          "market": "US",
          "qty": 100,
          "cost_basis": 175.50,
          "tags": ["tech"]
        },
        {
          "asset_id": "BTC",
          "symbol": "BTC",
          "name": "Bitcoin",
          "asset_class": "crypto",
          "market": "CRYPTO",
          "qty": 0.5,
          "cost_basis": 42000,
          "tags": []
        }
      ],
      "source": "text",
      "created_at": "2026-02-25T10:00:00Z",
      "updated_at": "2026-02-25T10:00:00Z"
    }
  ]
}
```

Field rules:
- `market`: `"CN_A"` | `"US"` | `"CRYPTO"` — determines which provider to use
- `name`: human-readable name (required for CN_A, helps with search queries)
- Auto-detect market: 6-digit numeric → `CN_A`, alphabetic 1-5 → `US`, known crypto tickers → `CRYPTO`
- Users manage their own portfolio via `/ms add` and `/ms remove`. The above JSON is illustrative only.

### WatchRule (`watch_rules.json`)

```json
{
  "rules": [
    {
      "rule_id": "R-001",
      "asset_id": "688306",
      "name": "均普智能",
      "market": "CN_A",
      "portfolio_id": "P-001",
      "detector": "threshold",
      "params": {
        "window": "5m",
        "pct": 2.0,
        "z_threshold": 2.5,
        "volume_z_threshold": 3.0,
        "cooldown_min": 30,
        "quiet_hours": { "start": "15:30", "end": "09:15", "tz": "Asia/Shanghai" }
      },
      "push_policy": "both",
      "digest_time": "15:00",
      "digest_tz": "Asia/Shanghai",
      "delivery": {
        "feishu": true,
        "severity_min": "medium"
      },
      "enabled": true,
      "created_at": "2026-02-25T10:00:00Z"
    }
  ]
}
```

`push_policy` values:
- `"brief_only"`: only produce daily briefs at `digest_time`, never alert on anomalies
- `"on_trigger"`: only alert on anomalies, no scheduled briefs
- `"both"`: produce daily briefs AND alert on anomalies (recommended for stocks)

Default `quiet_hours` by market:
- `CN_A`: 15:30–09:15 (non-trading hours)
- `US`: 16:05–09:25 ET
- `CRYPTO`: no quiet hours (24/7)

Default `digest_time` by market:
- `CN_A`: `"15:00"` (at close)
- `US`: `"16:05"` ET
- `CRYPTO`: `null` (no scheduled brief)

### Alert (`alerts.json`)

Alert ID format: `A-YYYYMMDD-NNNNN`.

```json
{
  "alerts": [],
  "next_seq": 1
}
```

### Brief (`briefs/YYYY-MM-DD/{asset_id}.md`)

The brief file is the narrative text exactly as pushed to Feishu. Example:

```markdown
均普智能（688306）：资金净流出，将召开临时股东会

^解读

最新价格：10.52元（-1.68％），2月25日，均普智能主力资金净流出1541.73万元，占总成交额12.35%。主力资金呈净流出状态，散户资金呈现净流入。股价小幅下跌，走势与所属的自动化设备板块（+1.93%）存在背离。交易量较前一交易日有所活跃，量比为1.70。

公司拟于2月27日召开2026年第一次临时股东会，审议调整募投项目闲置场地用途、预计年度日常关联交易等多项议案。

2月13日，公司作为产业投资方，战略投资具身智能数据平台觅蜂科技，布局具身智能数据新基建。

2月12日，公司在银行间市场成功发行全国首单AI+人形机器人研发领域科创债，发行规模2亿元，票面利率2.49%。
```

### EvidencePack (`evidence_packs/B-{asset_id}-{YYYY-MM-DD}/v1.json`)

```json
{
  "pack_id": "B-688306-2026-02-25",
  "type": "narrative_brief",
  "target_date": "2026-02-25",
  "asof": "2026-02-25T15:00:00+08:00",
  "asset": { "market": "CN_A", "symbol": "688306", "name": "均普智能" },
  "evidences": [
    {
      "evidence_id": "KLINE",
      "status": "ok",
      "url_or_id": "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.688306&klt=101&fqt=1&end=20500101&lmt=5",
      "retrieved_at": "2026-02-25T15:01:00+08:00",
      "excerpt": "close=10.52 pct=-1.68% high=10.83 low=10.66 amount=1.25亿 turnover=0.95%"
    },
    {
      "evidence_id": "FLOW",
      "status": "ok",
      "url_or_id": "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid=1.688306&klt=101&lmt=5",
      "retrieved_at": "2026-02-25T15:01:05+08:00",
      "excerpt": "主力净流出1541.73万 占比12.35%"
    },
    {
      "evidence_id": "SNAP",
      "status": "ok",
      "url_or_id": "https://push2.eastmoney.com/api/qt/stock/get?secid=1.688306&fields=f57,f58,f50",
      "retrieved_at": "2026-02-25T15:01:08+08:00",
      "excerpt": "f50=170 量比=1.70"
    },
    {
      "evidence_id": "ANN",
      "status": "ok",
      "url_or_id": "https://np-anotice-stock.eastmoney.com/api/security/ann?stock_list=688306",
      "retrieved_at": "2026-02-25T15:01:10+08:00",
      "excerpt": "临时股东会2/27, 科创债2亿2/12"
    },
    {
      "evidence_id": "NEWS",
      "status": "ok",
      "url_or_id": "https://api.gdeltproject.org/api/v2/doc/doc?query=...",
      "attempted_url": "query=(\"均普智能\" OR \"688306\")",
      "retrieved_at": "2026-02-25T15:01:15+08:00",
      "excerpt": "2 articles found"
    }
  ],
  "claims": []
}
```

Key rules:
- All 5 evidence entries (KLINE, FLOW, SNAP, ANN, NEWS) MUST exist even when retrieval failed: set `"status": "unavailable"` + `attempted_url` + `error`
- `claims` array may be empty for narrative briefs (analysis is woven into the narrative)

## Feishu Templates

### Narrative Brief Card (Mode B webhook)

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
          "content": "**^解读**\n\n最新价格：{price}元（{pct}%），{date}，{name}主力资金{direction}{amount}万元，占总成交额{ratio}%。主力资金呈{main_dir}状态，散户资金呈现{retail_dir}。{price_ctx}，走势与所属的{sector}板块（{sector_pct}%）{diverge}。交易量{vol_ctx}，量比为{vol_ratio}。\n\n{event_paragraphs}"
        }
      }
    ]
  }
}
```

Header `template` color (A-share convention):
- Positive change → `"red"` (red = up)
- Negative change → `"green"` (green = down)
- Flat (< 0.1%) → `"grey"`

### Alert Card (Mode B webhook)

```json
{
  "msg_type": "interactive",
  "card": {
    "config": { "wide_screen_mode": true },
    "header": {
      "title": { "tag": "plain_text", "content": "{name}（{symbol}）：{alert_headline}" },
      "template": "{color}"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**^解读**\n\n{narrative_paragraph}"
        }
      }
    ]
  }
}
```

### Webhook signing (when `FEISHU_SIGN_SECRET` is set)

```
timestamp = current Unix epoch seconds (string)
string_to_sign = timestamp + "\n" + FEISHU_SIGN_SECRET
sign = base64(HMAC-SHA256(string_to_sign, ""))
```

Add `"timestamp"` and `"sign"` to payload root alongside `"msg_type"` and `"card"`.

## Anomaly Detection

### Threshold

```
trigger if |current_return| > pct within window
```

### Z-score

```
z = (current_return - mean(rolling_returns)) / std(rolling_returns)
trigger if |z| > z_threshold
```

Rolling window: 20 periods of configured `window` duration.

### Volume spike

```
volume_z = (current_volume - mean(rolling_volume)) / std(rolling_volume)
trigger if volume_z > volume_z_threshold
```

### Cold-start bootstrap

If cache lacks prior price for a symbol:
1. Try to fetch recent K-line data (last 2-4 bars of window)
2. If K-line available: compute return immediately, can trigger
3. If K-line unavailable: record baseline, skip trigger, log "baseline established for {symbol}"

### Cooldown

After alert fires, suppress for `cooldown_min` unless:
- New severity is higher than existing open alert
- Price reversed direction

## Market-specific defaults

| Field | CN_A | US | CRYPTO |
|---|---|---|---|
| `pct` | 2% | 2% | 3% |
| `push_policy` | `"both"` | `"both"` | `"on_trigger"` |
| `digest_time` | `"15:00"` | `"16:05"` | `null` |
| `digest_tz` | `Asia/Shanghai` | `America/New_York` | — |
| `quiet_hours` | 15:30–09:15 CST | 16:05–09:25 ET | none |
| `window` | `5m` | `5m` | `5m` |

## A-share market prefix for URLs

| Code range | Exchange | Prefix |
|---|---|---|
| 600xxx, 601xxx, 603xxx, 605xxx, 688xxx | Shanghai (SH) | `sh` or `1.` |
| 000xxx, 001xxx, 002xxx, 003xxx, 300xxx | Shenzhen (SZ) | `sz` or `0.` |
| 830xxx, 8xxxxx (NQ) | Beijing (BJ) | `bj` or `0.` |

Example URL: `https://quote.eastmoney.com/sh688306.html`

## CN_A Data Sources

### E1a: push2his K-line (OHLC + amount + turnover)

```
GET https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&klt=101&fqt=1&end=20500101&lmt=3&fields1=f1,f2,f3,f4,f5,f6,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61
```

Response: `data.klines` array, each = `"date,open,close,high,low,volume,amount,amplitude%,change_pct%,change_amount,turnover%"`

### E1b: push2 stock/get (snapshot — mainly for 量比 and name)

Primary use: fetch `f50` (量比) and `f58` (name). Price/change data should come from K-line (E1a) which is more reliable.

Minimal request:
```
GET https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f57,f58,f50
```

Full field set (for reference; f43/f170 encoding varies and is unreliable):

| Field | Meaning | Conversion | Reliability |
|---|---|---|---|
| f57 | Code | — | reliable |
| f58 | Name | — | reliable |
| f50 | 量比 (volume ratio) | always /100 (e.g. 102→1.02) | reliable |
| f43 | Price | encoding varies by stock | unreliable — use kline |
| f170 | Change% | encoding varies | unreliable — use kline |
| f47 | Volume | 股 | ok |
| f48 | Amount | 元 | ok |
| f137 | 主力净流入 (today only) | 元 | ok (fallback for fund flow) |
| f193 | 主力净占比 (today only) | raw ÷100 = % | ok (fallback for fund flow) |

### E1c: fflow daykline/get (PRIMARY fund flow source — 主力资金)

**Use the HISTORICAL endpoint (push2his) as the primary source.** The real-time endpoint (push2) only returns today's data and cannot be used for 昨日简报.

```
GET https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid={secid}&klt=101&lmt=5&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57,f58
```

Response: `data.klines` = array of `"date,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入,主力净占比%,小单净占比%"` (流入 in 元, 占比 in %).

| Column | Meaning | Conversion |
|---|---|---|
| 0 | Date | YYYY-MM-DD |
| 1 | 主力净流入 | 元→/1e4=万元; >0=净流入, <0=净流出 |
| 2 | 小单净流入 | 元→/1e4=万元 |
| 3 | 中单净流入 | 元→/1e4=万元 |
| 4 | 大单净流入 | 元→/1e4=万元 |
| 5 | 超大单净流入 | 元→/1e4=万元 |
| 6 | 主力净占比 | % (已计算好, 可直接用; 取 abs 用于展示) |
| 7 | 小单净占比 | % |

Pick the entry whose `date` matches the kline target_date.

**Calculations**:
- `main_net_wan = abs(column_1) / 10000`
- `ratio_pct = abs(column_6)` (优先用 API 返回的占比; fallback: `abs(column_1) / amount_from_E1a * 100`)
- 散户方向 = inverse of 主力 (if 主力净流出 → 散户净流入)

### Sector board data (clist/get)

**Industry boards (行业板块)**:
```
GET https://push2.eastmoney.com/api/qt/clist/get?fs=m:90+t:2&fields=f2,f3,f12,f14&fid=f3&pn=1&pz=50&po=1
```

**Concept boards (概念板块)**:
```
GET https://push2.eastmoney.com/api/qt/clist/get?fs=m:90+t:3&fields=f2,f3,f12,f14&fid=f3&pn=1&pz=50&po=1
```

Response fields: `f14` = board name, `f3` = change%, `f12` = board code, `f2` = latest index.

**Batch fund flow (ulist.np/get)** for boards/indices:
```
GET https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids={secid_list}&fields=f62,f184,f66,f69,f72,f75,f78,f81,f84,f87
```
f62=主力净流入, f184=主力净比, f66=超大单净流入, f69=超大单净比, etc.

### Fallback: f137/f193 from stock/get (REAL-TIME ONLY)

If push2his fflow/daykline/get (E1c) fails, add f137,f193 to the stock/get request as fallback.
**WARNING**: f137/f193 only reflect TODAY's fund flow. Cannot be used for 昨日简报.

```
GET https://push2.eastmoney.com/api/qt/stock/get?secid={secid}&fields=f57,f58,f50,f137,f193
```
f137 = main net inflow (元), f193 = main net ratio raw (÷100 = %). Use same calculations as E1c.
