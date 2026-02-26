# market-sentry — Deployment Guide

## Prerequisites

- OpenClaw installed and running (`~/.openclaw/` exists)
- A Feishu group with a custom bot webhook configured

## Step 1: Copy skill to OpenClaw workspace

```bash
# Option A: workspace skills (per-agent, highest precedence)
cp -r skills/market-sentry ~/.openclaw/workspace/skills/market-sentry

# Option B: managed skills (shared across all agents)
cp -r skills/market-sentry ~/.openclaw/skills/market-sentry
```

OpenClaw auto-discovers skills from these locations. Workspace takes precedence over managed.

## Step 2: Configure Feishu webhook

### 2.1 Create Feishu group bot

1. Open the target Feishu group
2. Settings → Bots → Add Bot → Custom Bot
3. Copy the webhook URL (format: `https://open.feishu.cn/open-apis/bot/v2/hook/xxx`)
4. Optional: enable "Signature Verification" and copy the secret

### 2.2 Add secrets to OpenClaw config

Edit `~/.openclaw/openclaw.json` and add (or merge into existing `skills.entries`):

```json5
{
  "skills": {
    "entries": {
      "market-sentry": {
        "enabled": true,
        "env": {
          "FEISHU_WEBHOOK_URL": "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK_ID",
          // Only if you enabled keyword verification:
          "FEISHU_KEYWORD": "异动",
          // Only if you enabled signature verification:
          "FEISHU_SIGN_SECRET": "YOUR_SECRET"
        }
      }
    }
  }
}
```

## Step 3: Verify

Start a new OpenClaw session (skills reload on new session), then:

```
/ms setup feishu
```

You should see a green test card in your Feishu group.

## Step 4: Import portfolio and start monitoring

```
/ms portfolio import
AAPL 100
BTC 0.5
ETH 3.0

/ms watch start
```

## Directory structure after deployment

```
~/.openclaw/workspace/skills/market-sentry/
├── SKILL.md              # Main instructions (agent reads this)
├── reference.md          # Data models, card templates, algorithms
├── examples.md           # Example interactions
└── data/                 # Created at runtime
    ├── portfolios.json
    ├── watch_rules.json
    ├── alerts.json
    ├── price_cache.json
    └── evidence_packs/
        └── A-20260225-00001/
            ├── v1.json
            └── v2.json
```

## Cron job created by `/ms watch start`

```
Name:     market-sentry:monitor
Schedule: */5 * * * * (every 5 minutes)
Session:  isolated
```

Manage with:
```bash
openclaw cron list                      # see all jobs
openclaw cron run <jobId>               # force immediate run
openclaw cron edit <jobId> --patch '{"enabled":false}'  # pause
openclaw cron remove <jobId>            # delete
```

## Phase 2 Roadmap (future)

- [ ] Feishu App (双向交互): card button callbacks, per-user private alerts
- [ ] Hook-based delivery: `message:sent` hook to unify Feishu/Slack/Telegram
- [ ] External webhook trigger: connect real-time market data websocket to `/hooks/agent`
- [ ] Multi-portfolio support with per-portfolio alert routing
- [ ] Historical alert dashboard (query past EvidencePacks)
