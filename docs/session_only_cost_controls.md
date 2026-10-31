# Session-only research deployment (October 2026)

## Current billable resources
- Existing `intraday-cockpit-preview` Starter **web** remains always-on until explicitly suspended or changed. It is NOT automatically shut down by the cron.
- Existing `intraday-cockpit-scans` Postgres stays available all day; never suspend without a tested persistence/backup and recovery plan.
- New `intraday-session-research` Cron Job runs on 0.5 CPU / 512MB, 5-minute UTC schedule `*/5 3-6 * * 1-5`. Render charges based on active run time, with a $1 monthly minimum. See https://render.com/docs/cronjobs.

The 5-minute cron covers a wider UTC band, but `src.market_schedule.research_window` enforces **09:15–11:40 Asia/Kolkata** for verified 2026 trading weekdays excluding listed NSE equity holidays. Weekend/special sessions require reviewed exceptions and the year 2027 fails closed. Only the ~09:45–11:30 subset should be used for setup qualification. Holiday list: https://www.nseindia.com/resources/exchange-communication-holidays.

## Safe shutdown and continuity contract
1. One-shot jobs exit after each short run; no always-on worker costs.
2. Keep raw completed candles, 20-day RVOL baseline, checkpoints, last candle close, pending virtual trade state, and scan snapshots in durable Postgres. Retain session/day labels for the next morning.
3. On startup read the last persisted checkpoint, fetch a *padded* historical window, reconcile missing five-minute bars, and process only unprocessed candle closes in order; never invent bars or repeat published decisions.
4. Missing/stale provider data must block all new signals until catch-up is complete; never take a stale breakout.
5. **Any real broker-side position, pending order, stop amendment or fill-monitoring requires an always-on risk-control service** through exit/reconciliation. Do not shut down risk monitoring merely because new entries close at 11:30. Live orders are disabled in this deployment.
6. Database storage and web dashboard may still bill during off-hours. Suspending the web breaks access until resumed; do not assert billed savings without checking Render accounting.

## Not yet connected
The cron entrypoint currently returns `PUBLISHER_NOT_APPROVED` or `DATA_PUBLISHER_NOT_CONFIGURED`; it does **not** yet fetch candles, publish snapshots, or paper-trade. Configure Dhan and Postgres secrets in Render only when the verified collector is implemented. Do not share secrets in GitHub or ChatGPT.
