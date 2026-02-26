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
> - 688306: both (brief at 15:05 + anomaly trigger at 2%)
> - 600519: both (brief at 15:05 + anomaly trigger at 2%)
> - BTC: on_trigger (anomaly only, 3%)
> - AAPL: both (brief at 16:05 ET + anomaly trigger at 2%)

---

## Example 3: `/ms brief 688306` — A-stock daily brief

**User:** `/ms brief 688306`

**Agent pushes to Feishu:**

> **解读：均普智能(688306)**
>
> 均普智能 688306  10.70  -0.56%
>
> 截至2026年02月25日 15:00，**均普智能(688306)**最新价格：10.70元，
> 最新涨跌幅：-0.56%。股价日内小幅震荡，成交额1.25亿元，换手率0.95%。
>
> · 公司将于2月27日召开2026年第一次临时股东会，审议调整募投项目闲置场地用途、预计年度日常关联交易等多项议案。(E-event-1)
>
> · 2月24日盘后数据显示，公司主力资金净流出1017.09万元，占总成交额7.1%。(E-flow)
>
> · 公司于2月13日作为产业投资方，战略投资具身智能数据平台觅蜂科技，布局具身智能数据新基建。(E-event-2)
>
> · 公司于2月12日成功发行全国首单AI+人形机器人研发领域科创债，规模2亿元，票面利率2.49%，资金将用于相关技术研发及装备升级。(E-event-3)
>
> 📈 **技术与资金**
>
> | 维度 | 分析要点 |
> |------|---------|
> | 资金流向 | 主力资金今日净流出约1598.5万元，占成交比例较高，显示短期资金态度偏谨慎。(E-flow) |
> | 技术形态 | 股价今日小幅收跌，振幅1.58%，整体在10.66至10.83区间内窄幅震荡。成交量较前一交易日有所萎缩，技术形态呈现弱势整理格局。(E-price) |
> | 上方阻力 | 10.83元（今日高点）及11元整数关口附近。(E-price) |
> | 下方支撑 | 10.66元（今日低点）及10.5元平台附近。(E-price) |
>
> 📝 **投研要点**
> 1. (中) 事件驱动弱、资金偏谨慎，短期延续震荡概率较大（引用 E-flow, E-price）
> 2. (低) 人形机器人/具身智能政策主题对估值弹性（引用 E-event-2, E-event-3）
> 3. (中) 债券融资利率低，研发投入预期增强中长期逻辑（引用 E-event-3）
>
> *以上内容由 AI 生成，不构成任何投资建议*

---

## Example 4: `/ms digest start`

**User:** `/ms digest start`

**Agent:**
> Created 2 digest cron jobs:
>
> 1. **market-sentry:digest-cn**
>    - Schedule: 15:05 Mon-Fri (Asia/Shanghai)
>    - Assets: 688306, 600519
>    - Job ID: cron-cn-001
>
> 2. **market-sentry:digest-us**
>    - Schedule: 16:05 Mon-Fri (America/New_York)
>    - Assets: AAPL
>    - Job ID: cron-us-001
>
> BTC has push_policy=on_trigger, no digest scheduled.
>
> Manage with:
> - `openclaw cron list`
> - `openclaw cron run cron-cn-001` (force run now)

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

Later, BTC surges +6.2% in 5 minutes:

> **[异动] BTC +6.2% (5m) | High**
>
> **发生了什么**
> - 5m: +6.2% | 1h: +8.1%
> - 波动Z: 2.9 | 量能Z: 3.4
> - 当前价: $97,500
>
> **初步解释（置信度：中）**
> - 机构资金大规模流入，某基金宣布$5亿BTC配置（证据 E2）
>
> **下一步**
> - 持续追踪中，若出现新证据将推送更新
>
> `A-20260225-00001`
>
> ---
> **证据链接**
> - [E1 价格快照]()
> - [E2 CoinDesk: 机构配置公告](https://coindesk.com/example)

---

## Example 6: Brief for US stock

**User:** `/ms brief AAPL`

**Agent pushes:**

> **解读：Apple Inc.(AAPL)**
>
> AAPL  $213.84  -0.32%
>
> As of 2026-02-25 16:00 ET, **Apple (AAPL)** last price: $213.84,
> change: -0.32%. Intraday range $212.50–$215.20. Volume: 45.2M shares.
>
> · Q1 2026 earnings beat estimates: EPS $2.18 vs $2.10 est. (E-event-1)
> · Apple Intelligence rollout expanding to 8 new countries in March. (E-news-1)
>
> 📈 **Technical & Flow**
>
> | Dimension | Analysis |
> |-----------|----------|
> | Institutional flow | Net buying $120M over past 5 days (E-flow) |
> | Technical pattern | Consolidating near 50-day MA ($212), low volatility (E-price) |
> | Resistance | $215.20 (today's high), $218 (Jan high) (E-price) |
> | Support | $212 (50-day MA), $208 (200-day MA) (E-price) |
>
> 📝 **Research Notes**
> 1. (High) Post-earnings consolidation is healthy; no distribution signals (E-price, E-flow)
> 2. (Medium) Apple Intelligence rollout may be a catalyst for services revenue re-rating (E-news-1)
> 3. (Low) Macro headwinds from rising yields could cap near-term upside (unconfirmed — missing: Fed commentary)
>
> *AI-generated, not investment advice*

---

## Example 7: Cold-start monitor run

First monitor run after `/ms watch start`:

> **market-sentry monitor loop @ 2026-02-25 15:30 Asia/Shanghai**
>
> Loaded 4 watch rules.
>
> Fetching prices:
> - 688306: 10.70 CNY (baseline established — no prior cache)
> - 600519: 1688.00 CNY (baseline established)
> - BTC: $65,055 (fetched 5m K-line: -0.3% vs 5m ago → below 3% threshold)
> - AAPL: market closed (quiet hours), skipped
>
> Detection: 0 triggers (2 baselines, 1 below threshold, 1 skipped)
> Saved price_cache.json with 3 snapshots.
>
> Next run in 5 minutes — all symbols will have prior data for comparison.
