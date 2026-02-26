# market-sentry Examples

## Example 1: Setup

**User:** `/ms setup feishu`

**Agent:**
> Checking delivery channels...
> - FEISHU_WEBHOOK_URL: not set
> - channels.feishu: enabled (App bot "Claw")
> → Using Mode A (Feishu App channel)
>
> Sending test message... sent.
> Saved config: delivery_mode = "app"
> Setup complete.

---

## Example 2: Import A-stock portfolio

**User:** `/ms portfolio import`

```
688306 均普智能 1000
600519 贵州茅台 10
BTC 0.5
AAPL 100
```

**Agent:**
> Parsed 4 positions:
>
> | Symbol | Name | Qty | Market |
> |--------|------|-----|--------|
> | 688306 | 均普智能 | 1000 | CN_A |
> | 600519 | 贵州茅台 | 10 | CN_A |
> | BTC | Bitcoin | 0.5 | CRYPTO |
> | AAPL | Apple | 100 | US |
>
> Saved to portfolio P-001 (source: text).
> Created 4 watch rules:
> - 688306: both (brief at 15:00 + anomaly trigger at 2%)
> - 600519: both (brief at 15:00 + anomaly trigger at 2%)
> - BTC: on_trigger (anomaly only, 3%)
> - AAPL: both (brief at 16:05 ET + anomaly trigger at 2%)

---

## Example 3: `/ms brief 688306` — A-stock narrative brief

**User:** `/ms brief 688306`

**Agent pushes to Feishu and saves brief + EvidencePack. Output (Mode A):**

> 均普智能（688306）：资金净流出，将召开临时股东会
>
> ^解读
>
> 最新价格：10.52元（-1.68％），2月25日，均普智能主力资金净流出1541.73万元，占总成交额12.35%。主力资金呈净流出状态，散户资金呈现净流入。股价小幅下跌，走势与所属的自动化设备板块（+1.93%）存在背离。交易量较前一交易日有所活跃，量比为1.70。
>
> 公司拟于2月27日召开2026年第一次临时股东会，审议调整募投项目闲置场地用途、预计年度日常关联交易等多项议案。
>
> 2月13日，公司作为产业投资方，战略投资具身智能数据平台觅蜂科技，布局具身智能数据新基建。
>
> 2月12日，公司在银行间市场成功发行全国首单AI+人形机器人研发领域科创债，发行规模2亿元，票面利率2.49%。

Side effects (not visible in output):
- Pushed to Feishu via message tool
- Saved: `data/briefs/2026-02-25/688306.md`
- Saved: `data/evidence_packs/B-688306-2026-02-25/v1.json`

---

## Example 4: `/ms digest start`

**User:** `/ms digest start`

**Agent:**
> Created 2 digest cron jobs:
>
> 1. **market-sentry:digest-cn**
>    - Schedule: 15:00 Mon-Fri (Asia/Shanghai)
>    - Assets: 688306, 600519
>    - Job ID: cron-cn-001
>
> 2. **market-sentry:digest-us**
>    - Schedule: 16:05 Mon-Fri (America/New_York)
>    - Assets: AAPL
>    - Job ID: cron-us-001
>
> BTC has push_policy=on_trigger, no digest scheduled.

---

## Example 5: `/ms watch start` + anomaly alert

**User:** `/ms watch start`

**Agent:**
> Created anomaly monitor:
> - Name: market-sentry:monitor
> - Schedule: every 5 minutes
> - Job ID: cron-mon-001
>
> Monitoring 4 assets. Will alert when thresholds are breached.

Later, BTC surges +6.2% in 5 minutes. Agent pushes to Feishu:

> BTC（Bitcoin）：5分钟急涨6.2%，疑似机构大额配置
>
> ^解读
>
> 当前价格：$97,500（+6.2%/5min, +8.1%/1h），波动Z值2.9，量能Z值3.4。CoinDesk报道某基金宣布5亿美元BTC配置计划，市场短线情绪快速升温，链上大额转账同步放量。
>
> 某头部对冲基金宣布将配置5亿美元等值BTC，消息发布后15分钟内价格急拉。

---

## Example 6: Brief for US stock

**User:** `/ms brief AAPL`

**Agent pushes to Feishu:**

> Apple Inc.（AAPL）：小幅回落，Q1财报超预期

> ^Briefing
>
> Price: $213.84 (-0.32%), Feb 25. Volume 45.2M shares, slightly below 20-day average. Intraday range $212.50–$215.20.
>
> Q1 2026 earnings beat estimates: EPS $2.18 vs consensus $2.10, driven by 18% YoY growth in Services revenue.
>
> Apple Intelligence rollout expanding to 8 new countries in March, with on-device AI features for iPhone 16 series.

---

## Example 7: Digest with degraded data

**Agent runs digest-cn cron at 15:00. One asset has no CNINFO results and GDELT fails:**

> 某某科技（300XXX）：缩量微涨，无近期重大公告

> ^解读
>
> 最新价格：25.30元（+0.42%），2月25日，某某科技主力资金净流入203.5万元，占总成交额1.8%。主力资金呈小幅净流入状态，散户资金呈现净流出。交易量较前日有所萎缩，量比为0.85。
>
> 近期暂无重要公告或新闻。

Side effects:
- EvidencePack saved with E2 status="unavailable", attempted_url="https://www.cninfo.com.cn/...", error="empty result"
- E3 status="unavailable", attempted_url="https://api.gdeltproject.org/...", error="timeout"

---

## Example 8: Cold-start monitor run (silent, no output)

First monitor run after `/ms watch start`. Agent writes to `logs/monitor-20260225.log`:

```
2026-02-25T15:30:00+08:00 | 4 rules | 688306:baseline | 600519:baseline | BTC:-0.3%(below 3%) | AAPL:closed | 0 triggers
```

No chat output. No Feishu push. Brief/digest is a separate pipeline.
