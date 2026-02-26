# market-sentry

An [OpenClaw](https://docs.openclaw.ai/skills) skill for multi-asset financial monitoring with daily briefs, anomaly alerts, auditable evidence packs, and Feishu push notifications.

## Features

- **Daily Briefs** — Scheduled close-of-market reports for A-shares (15:00 CST), US stocks (16:05 ET), and crypto
- **Anomaly Alerts** — Real-time price/volume anomaly detection with configurable thresholds
- **Auditable Evidence Packs** — Every claim cites evidence with source URLs and timestamps
- **Feishu Push** — Supports both Feishu App channel and group bot webhook
- **Multi-market** — A-shares (东方财富 API + 巨潮资讯), US stocks (Yahoo Finance), Crypto (CoinGecko)

## Quick Start

### 1. Install

```bash
cp -r skills/market-sentry ~/.openclaw/workspace/skills/market-sentry
```

### 2. Configure

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "market-sentry": {
        "enabled": true
      }
    }
  }
}
```

### 3. Use

Start a new OpenClaw session, then:

```
/ms setup feishu          # Test Feishu channel
/ms portfolio import      # Import your holdings
/ms brief 688306          # Generate a brief now
/ms digest start          # Schedule daily briefs
/ms watch start           # Start anomaly monitoring
```

## Skill Structure

```
skills/market-sentry/
├── SKILL.md          # Main instructions (agent reads this)
├── reference.md      # Data models, API details, card templates
└── examples.md       # Example interactions and output
```

## Commands

| Command | Description |
|---------|-------------|
| `/ms setup feishu` | Detect and test Feishu delivery channel |
| `/ms portfolio import` | Import positions (text or image) |
| `/ms watch add` | Add monitoring rules |
| `/ms brief <symbol>` | Generate an immediate brief for any asset |
| `/ms digest start` | Create scheduled digest cron jobs |
| `/ms watch start` | Start anomaly detection cron |
| `/ms explain <alert_id>` | Deep-dive explanation with evidence chain |
| `/ms follow <alert_id>` | Enable follow-up tracking for an alert |

## Data Sources

| Market | Quote & Flow | Events | News |
|--------|-------------|--------|------|
| CN_A | 东方财富 push2 API | 巨潮资讯 CNINFO | web_search |
| US | Yahoo Finance | SEC EDGAR | web_search |
| Crypto | CoinGecko API | — | web_search |

## License

MIT
