# market-sentry 📈

**Multi-asset financial monitor for OpenClaw.**
一个协助openclaw监控你的持仓异动的skills，支持A股、港股、美股、crypto，支持异动监控与提醒、收盘简报、异动解读，服务于你的投资组合～

#使用与安装：

cd /path/to/openclaw/skills

git clone https://github.com/ZiyaZhang/market-sentry.git

#英文介绍：

`market-sentry` is an OpenClaw skill that provides narrative daily briefs, real-time anomaly alerts, and auditable data tracking for A-shares (CN_A), US stocks, and Crypto.

It is designed to be "quiet until necessary" (anomaly alerts) but "reliable when asked" (daily briefs), with a strong focus on data provenance via EvidencePacks.

## Features

- **Narrative Briefs**: Generates natural language daily digests (like a research note), not just bullet points.
- **Multi-Market Support**:
  - **A-shares (CN_A)**: K-line, **Fund Flow (主力资金)**, Volume Ratio (量比), Announcements (公告), Sector performance.
  - **US Stocks**: Quote, News, SEC Filings (best-effort).
  - **Crypto**: Price, Volume, On-chain data (optional).
- **Anomaly Detection**:
  - Price thresholds (e.g., >2% in 5m).
  - Z-score statistical anomalies.
  - Volume spikes.
- **Feishu Integration**:
  - **Mode A**: Direct message via Feishu App bot.
  - **Mode B**: Rich Interactive Cards via Webhook (recommended).
- **Auditable**: Every brief generates a JSON `EvidencePack` containing the raw API responses used to generate the text, ensuring no hallucination.

## Prerequisites

- **OpenClaw**: This is a skill for the [OpenClaw](https://github.com/openclaw/openclaw) agent framework.
- **Feishu Webhook** (Optional but recommended): For rich card notifications.

## Installation

1.  Clone this repository into your OpenClaw skills directory:
    ```bash
    cd /path/to/your/openclaw/skills
    git clone https://github.com/ZiyaZhang/market-sentry.git
    ```

2.  (Optional) Configure Feishu Webhook:
    Add `FEISHU_WEBHOOK_URL` to your OpenClaw environment variables or `.env` file.

## Usage

### 1. Setup Portfolio
Add assets to your watch list. The market is auto-detected.

```bash
/ms add 688306 均普智能 1000   # CN_A
/ms add AAPL Apple 100        # US
/ms add BTC Bitcoin 0.5       # CRYPTO
```

Or import in bulk:
```bash
/ms portfolio import
600519 贵州茅台 100
NVDA Nvidia 50
ETH Ethereum 10
```

### 2. Generate Briefs (On-Demand)
Generate a narrative brief for a specific asset or the whole portfolio.

```bash
/ms brief 688306          # Single asset
/ms brief portfolio       # All assets (sequential)
```

### 3. Start Automation
Set up cron jobs for daily digests and continuous monitoring.

```bash
/ms digest start   # Schedules daily briefs (15:00 CN, 16:05 US)
/ms watch start    # Starts 5-minute silent anomaly monitoring
```

### 4. Feishu Setup
Check connection mode (App vs Webhook).

```bash
/ms setup feishu
```

## Data Sources

- **CN_A**: Eastmoney (东方财富) APIs for K-line, historical fund flow, and announcements.
- **US**: Finnhub (primary), Stooq (fallback).
- **Crypto**: CoinGecko.

## Architecture

- **Briefs**: Triggered on-demand or via cron. They fetch comprehensive data (4+ sources for CN_A), generate a narrative, push to Feishu, and save a markdown file + JSON EvidencePack.
- **Monitor**: Runs every 5 minutes (silent). Checks for price/volume anomalies. If a threshold is breached, it pushes an alert immediately.
- **EvidencePack**: A JSON file saved to `data/evidence_packs/` for every generated brief. It proves *why* the agent wrote what it wrote.

## License

MIT
