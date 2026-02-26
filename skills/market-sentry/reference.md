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
  "asof": "2026-02-25T15:00:00+08:00",
  "asset": { "market": "CN_A", "symbol": "688306", "name": "均普智能" },
  "evidences": [
    {
      "evidence_id": "E1",
      "source_type": "quote",
      "status": "ok",
      "source_name": "东方财富 push2",
      "url_or_id": "https://push2.eastmoney.com/api/qt/stock/get?secid=1.688306&fields=f57,f58,f43,f170,f44,f45,f46,f47,f48,f50,f168,f137,f193,f86",
      "retrieved_at": "2026-02-25T15:01:00+08:00",
      "excerpt": "10.52 -1.68% 成交额1.25亿 换手0.95% 量比1.70 主力净流出1541.73万"
    },
    {
      "evidence_id": "E2",
      "source_type": "announcement",
      "status": "ok",
      "source_name": "巨潮资讯",
      "url_or_id": "https://www.cninfo.com.cn/new/hisAnnouncement/query",
      "attempted_url": "stock=688306&tabName=fulltext&pageSize=10&pageNum=1&seDate=2026-01-26~2026-03-04",
      "retrieved_at": "2026-02-25T15:01:10+08:00",
      "excerpt": "临时股东会2/27, 战略投资觅蜂科技2/13, 科创债2亿2/12"
    },
    {
      "evidence_id": "E3",
      "source_type": "news",
      "status": "ok",
      "source_name": "GDELT",
      "url_or_id": "https://api.gdeltproject.org/api/v2/doc/doc?query=(%22均普智能%22+OR+%22688306%22)&mode=artlist&format=json&maxrecords=5&timespan=1week",
      "attempted_url": "query=(\"均普智能\" OR \"688306\")",
      "retrieved_at": "2026-02-25T15:01:15+08:00",
      "excerpt": "2 articles found"
    }
  ],
  "claims": []
}
```

Key rules:
- E2 and E3 MUST exist even when retrieval failed: `"status": "unavailable"` + `attempted_url` + `error`
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

## CN_A push2 field reference

Full field list used in one-call URL:

| Field | Meaning | Conversion |
|---|---|---|
| f57 | Code | — |
| f58 | Name | — |
| f43 | Price | 分→/100=元 (skip if already reasonable) |
| f170 | Change% | 1/100%→/100=% |
| f44 | High | 分→/100 |
| f45 | Low | 分→/100 |
| f46 | Open | 分→/100 |
| f47 | Volume | 股 |
| f48 | Amount | 元→/1e8=亿元, →/1e4=万元 |
| f50 | 量比 (volume ratio) | /100 if >10, else as-is |
| f168 | Turnover% | 1/100%→/100=% |
| f137 | Main net inflow | 元→/1e4=万元; >0=净流入, <0=净流出 |
| f193 | Main net ratio | 1/100%→/100=% |
| f86 | Timestamp | Unix sec → HH:MM CST |

散户方向: if 主力净流出 → 散户净流入 (and vice versa).
