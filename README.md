# Intraday Trading Automation

Private NSE equity research cockpit and paper-trading development project.

**Resume here:** [Project handoff](docs/PROJECT_HANDOFF.md) and
[next work plan](docs/NEXT_WORK_PLAN.md). Updated 31 October 2026.
These documents distinguish approved/deployed behavior from pending proposals.

## Current status
- [Cockpit](https://intraday-cockpit-preview.onrender.com/) is live in PREVIEW_ONLY mode; real-money execution is disabled.
- Daily premarket research-universe refresh is deployed. First eligible Monday publication still needs operational verification.
- Dated universe: 103 research candidates, 2 identity holds and 4 exclusions; none is trading-cleared.
- Automatic scanner coverage is RELIANCE only.
- Paper lab supports deterministic candle replay, execution-failure scenarios and an append-only replay journal. Automatic forward paper trades are **not ready**.
- PR #7 chart reconciliation is deployed. Mayur reported one exact RELIANCE 30 October 09:15 IST API/chart OHLC match under opening-time labels.
- [PR #8](https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/8) adds opt-in full-session research capture. It is approved, merged and deployed on the existing research cron; actual eligible-session capture is still unobserved.
- Render auto-deploy is off. Production changes require Mayur's approval. No approval authorizes real-money orders.

## Implemented account policy
Capital INR 980,000; maximum planned risk INR 9,800 inclusive of estimated
costs; long only; one filled entry per trading day; no leverage.
Trade management requests cost-breakeven after 1.5 price R and an EMA10
close exit. Replay assumptions are not verified live fees or strategy approval.

## Documentation
- [Paper lab usage and assumptions](docs/paper-trading-lab.md)
- [Forward-paper readiness checkpoint](docs/forward-paper-readiness-2026-10-31.md)
- [Daily universe refresh](docs/daily-universe-refresh-2026-10-31.md)
- [Universe research and reproduction](docs/universe-research-2026-10-31.md)
- [NSE eligibility audit](docs/nse-eligibility-audit-2026-10-31.md)
- [Dated candidate CSV](research/2026-10-30/candidates.csv)

The proposed capture document currently lives on PR #8's review branch:
[forward-feed-capture.md](https://github.com/Mayuragarkar2020/intraday-trading-automation/blob/codex/forward-feed-capture/docs/forward-feed-capture.md).

## Development and safety
Install requirements and run Python tests with python -m pytest -q.
CI also exercises PostgreSQL 18 concurrency and both Chromium browser suites.
Synthetic fixtures test software; they are not market-performance evidence.
Older entrypoints such as src/run_daily.py and the root render.yaml describe
earlier scaffold work; they are not the current deployed cron configuration.
Use the handoff, current source and actual Render settings before operating.

No credentials, internal database URLs or live trading secrets belong in GitHub.
