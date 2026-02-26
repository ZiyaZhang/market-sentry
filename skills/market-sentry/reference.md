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
      "digest_time": "15:05",
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
- `CN_A`: `"15:05"` (just after close)
- `US`: `"16:05"` ET
- `CRYPTO`: `null` (no scheduled brief)

### Alert (`alerts.json`)

Same as before. Alert ID format: `A-YYYYMMDD-NNNNN`.

```json
{
  "alerts": [],
  "next_seq": 1
}
```

### Brief (`briefs/<symbol>/<date>.json`)

```json
{
  "brief_id": "B-688306-20260225",
  "symbol": "688306",
  "name": "均普智能",
  "market": "CN_A",
  "as_of": "2026-02-25T15:00:00+08:00",
  "generated_at": "2026-02-25T15:05:30+08:00",
  "quote": {
    "price": 10.70,
    "change_pct": -0.56,
    "open": 10.75,
    "high": 10.83,
    "low": 10.66,
    "amount": 125000000,
    "amount_display": "1.25亿元",
    "turnover_pct": 0.95,
    "amplitude_pct": 1.58
  },
  "events": [
    {
      "date": "2026-02-27",
      "type": "shareholder_meeting",
      "text": "将于2月27日召开2026年第一次临时股东会，审议调整募投项目闲置场地用途、预计年度日常关联交易等多项议案",
      "source": "巨潮资讯"
    },
    {
      "date": "2026-02-13",
      "type": "strategic_investment",
      "text": "作为产业投资方，战略投资具身智能数据平台觅蜂科技，布局具身智能数据新基建",
      "source": "公告"
    },
    {
      "date": "2026-02-12",
      "type": "bond_issuance",
      "text": "成功发行全国首单AI+人形机器人研发领域科创债，规模2亿元，票面利率2.49%，资金将用于相关技术研发及装备升级",
      "source": "公告"
    }
  ],
  "fund_flow": {
    "date": "2026-02-24",
    "main_net_flow": -10170900,
    "main_net_flow_display": "净流出1017.09万",
    "main_pct_of_amount": 7.1,
    "interpretation": "主力资金今日净流出约1598.5万元，占成交比例较高，显示短期资金态度偏谨慎"
  },
  "technical": {
    "pattern": "股价今日小幅收跌，振幅1.58%，整体在10.66元至10.83元区间内窄幅震荡。成交量较前一交易日有所萎缩，技术形态呈现弱势整理格局",
    "resistance": "10.83元（今日高点）及11元整数关口附近",
    "support": "10.66元（今日低点）及10.5元平台附近"
  },
  "research_notes": [
    {
      "confidence": "中",
      "text": "事件驱动弱、资金偏谨慎，短期延续震荡概率较大",
      "evidence_ids": ["E-flow", "E-price"]
    },
    {
      "confidence": "低",
      "text": "人形机器人/具身智能政策主题对估值弹性",
      "evidence_ids": ["E-event-2", "E-event-3"]
    },
    {
      "confidence": "中",
      "text": "债券融资利率低，研发投入预期增强中长期逻辑",
      "evidence_ids": ["E-event-3"]
    }
  ],
  "evidence_pack_id": "EP-B-688306-20260225-v1",
  "pushed_at": "2026-02-25T15:05:45+08:00"
}
```

### EvidencePack (for briefs and alerts)

```json
{
  "pack_id": "EP-B-688306-20260225-v1",
  "ref_id": "B-688306-20260225",
  "ref_type": "brief",
  "version": 1,
  "generated_at": "2026-02-25T15:05:30+08:00",
  "evidences": [
    {
      "evidence_id": "E-price",
      "source_type": "quote",
      "source_name": "东方财富",
      "url_or_id": "https://quote.eastmoney.com/sh688306.html",
      "retrieved_at": "2026-02-25T15:05:00+08:00",
      "excerpt": "688306 均普智能: 10.70 -0.56% 成交额1.25亿 换手0.95%"
    },
    {
      "evidence_id": "E-flow",
      "source_type": "fund_flow",
      "source_name": "东方财富资金流向",
      "url_or_id": "https://data.eastmoney.com/zjlx/688306.html",
      "retrieved_at": "2026-02-25T15:05:10+08:00",
      "excerpt": "2/24盘后 主力净流出1017.09万 占总成交额7.1%"
    },
    {
      "evidence_id": "E-event-1",
      "source_type": "announcement",
      "source_name": "巨潮资讯",
      "url_or_id": "http://www.cninfo.com.cn/...",
      "published_at": "2026-02-25T00:00:00+08:00",
      "retrieved_at": "2026-02-25T15:05:15+08:00",
      "excerpt": "将于2/27召开临时股东会，审议多项议案"
    },
    {
      "evidence_id": "E-event-2",
      "source_type": "announcement",
      "source_name": "公告",
      "published_at": "2026-02-13T00:00:00+08:00",
      "retrieved_at": "2026-02-25T15:05:18+08:00",
      "excerpt": "战略投资觅蜂科技，布局具身智能数据新基建"
    },
    {
      "evidence_id": "E-event-3",
      "source_type": "announcement",
      "source_name": "公告",
      "published_at": "2026-02-12T00:00:00+08:00",
      "retrieved_at": "2026-02-25T15:05:20+08:00",
      "excerpt": "发行AI+人形机器人科创债2亿元 票面利率2.49%"
    }
  ],
  "claims": [
    {
      "claim_id": "C1",
      "text": "资金面偏谨慎，主力持续净流出",
      "evidence_ids": ["E-flow"],
      "confidence": "中"
    },
    {
      "claim_id": "C2",
      "text": "具身智能布局+低成本融资强化中长期逻辑",
      "evidence_ids": ["E-event-2", "E-event-3"],
      "confidence": "低"
    }
  ]
}
```

## Feishu Card Templates

### Brief Card (Mode B webhook)

```json
{
  "msg_type": "interactive",
  "card": {
    "config": { "wide_screen_mode": true },
    "header": {
      "title": { "tag": "plain_text", "content": "解读：{name}({symbol})" },
      "template": "blue"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**{name} {symbol}**  {price} {change_pct}%\n\n截至{date} {time}，**{name}({symbol})**最新价格：{price}元，最新涨跌幅：{change_pct}%。{price_context}。成交额{amount}，换手率{turnover}%。\n\n{events_text}\n\n📈 **技术与资金**\n\n| 维度 | 分析要点 |\n|------|----------|\n| 资金流向 | {flow_text} |\n| 技术形态 | {tech_text} |\n| 上方阻力 | {resistance} |\n| 下方支撑 | {support} |\n\n📝 **投研要点**\n{research_notes_text}\n\n*以上内容由 AI 生成，不构成任何投资建议*"
        }
      }
    ]
  }
}
```

Header `template` color by change:
- Positive change → `"red"` (A-share convention: red = up)
- Negative change → `"green"` (A-share convention: green = down)
- Flat (< 0.1%) → `"blue"`

### Alert Card (Mode B webhook)

```json
{
  "msg_type": "interactive",
  "card": {
    "config": { "wide_screen_mode": true },
    "header": {
      "title": { "tag": "plain_text", "content": "[异动] {symbol} {direction}{r_5m}% (5m) | {severity}" },
      "template": "{color}"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**发生了什么**\n- 5m: {direction}{r_5m}%  |  1h: {direction}{r_1h}%\n- 波动Z: {vol_z}  |  量能Z: {volume_z}\n- 当前价: {price}\n\n**初步解释（置信度：{confidence}）**\n- {primary_claim}（证据 {evidence_ids}）\n\n**下一步**\n- 持续追踪中，若出现新证据将推送更新\n\n`{alert_id}`"
        }
      },
      { "tag": "hr" },
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**证据链接**\n{evidence_links}"
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
| `digest_time` | `"15:05"` | `"16:05"` | `null` |
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
