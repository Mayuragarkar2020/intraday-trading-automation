# Intraday Trading Automation — project handoff
Updated: 31 October 2026. Read this before resuming in a new chat.

## Working agreement
- Owner: Mayur Agarkar. Repository is the source of truth: https://github.com/Mayuragarkar2020/intraday-trading-automation (private).
- Continue authorized implementation and testing autonomously. Stop for genuinely missing input or production approval.
- Mayur explicitly requires approval before production changes. PR #5 and PR #6 were approved, merged and deployed. Those approvals do not authorize real-money trading or later releases.
- Keep durable project source/evidence in GitHub; do not depend on Mayur's computer. Temporary test copies are disposable.
- Do not ask for credentials in chat, expose tokens, or read browser memory to extract them. Cockpit authentication token stays in page memory.
- Do not spawn subagents unless expressly authorized.
- Older general trading memories differ from this project's implemented policy. Read current repository code and locked project decisions before changing rules; do not silently substitute older Nifty-200/2-trade/0.75%-risk settings.
- README contains outdated milestone descriptions. Current dated docs, source and deployment evidence take precedence.

## Current production state
- Cockpit: https://intraday-cockpit-preview.onrender.com/
- PR #5 (UI redesign): https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/5 — merged/deployed.
- PR #6 (Paper lab): https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/6 — merged/deployed after explicit user approval.
- Paper release main commit: 5db368372f66d84fcf45ed55678eafe35c1e07da.
- Paper release Render deploy: dep-dbis7k8u01pc73dqi910 — live.
- Last verification: normal cockpit URL returned 200 and contains data-view="paper"; health returned 200, execution_enabled=false, PREVIEW_ONLY. Paper scenarios/runs endpoints and universe CSV returned 401 without token.
- Render auto-deploy is OFF. A documentation commit does not deploy production. Before any future manual trigger, inspect main and ensure it contains only intended approved changes.
- If menu looks old, Ctrl+Shift+R. Paper lab sits between Universe and Diagnostics.
- Paper UI and core/API tests passed in CI; authenticated production replay/database publication has not been demonstrated to the agent. User should run the scenario suite and synthetic example from the live UI. Do not claim a saved production run until verified.

## Render resources (confirmed workspace)
- Workspace: tea-da6sf5qfngtc73c8jfi0 (My Workspace), explicitly confirmed by user.
- Web: srv-dbicbu1srm7s73ds0o30, intraday-cockpit-preview, Singapore, main, auto-deploy off.
- Research cron: crn-dbimqnbbc2fs73ap21vg, Singapore; schedule */5 3-6 * * 1-5 UTC; auto-deploy off.
- PostgreSQL: dpg-dbicbq8ae00c73bqrp6g-a, Singapore, PostgreSQL 18, 1 GB; external access closed. Existing SCAN_DATABASE_URL is internal and secret.
- Do not touch older suspended Oregon trading-automation service.
- Paper module uses existing web service/database; no additional paid service created. Research cron was not redeployed for frontend/paper releases.

## Universe and research
- Dated research evidence: research/2026-10-30/.
- 20 exact official NSE sessions from 1–30 October; T-1 boundaries and source hashes preserved.
- 109 liquidity candidates, 103 research-pool candidates, 2 identity holds, 4 exclusions. None is trading-cleared.
- Holds: TECHM and SHRIRAMFIN (corporate-action/ISIN conflicts).
- Exclusions: LIQUIDBEES and LALITHAA (low band), ESDS and WELCORP (ASM).
- Pool status HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE means research only, not approval.
- Universe CSV export /api/universe-research.csv exports only the 103 research candidates with explicit dates/mode.
- Daily premarket refresh and immutable PostgreSQL universe snapshots deployed in PR #4.
- Intended session of static snapshot: 2 November 2026. Reviewed calendar for daily refresh only covers 2–6 November; extend/review before it expires.
- First scheduled production daily refresh expected 2 November 08:30 IST. Saturday deployment did not demonstrate that publication.
- Automatic scanner coverage remains RELIANCE only. Do not claim it scans all 103 stocks.
- Read docs/daily-universe-refresh-2026-10-31.md and relevant source before changing refresh/scheduling.

## Cockpit and paper module
- Views: Overview, Scanner, Universe, Paper lab, Diagnostics.
- Universe tabs separate pool/holds/exclusions; search, sorting, pagination, evidence details and authenticated CSV.
- No automatic synthetic setup load on login. Synthetic/uploaded diagnostics never populate stored scanner.
- Lock clears token, private inputs, loaded results and paper history; async response guards reject stale sessions.
- Paper sources:
  - src/paper_models.py: bounded/finite validated replay inputs.
  - src/paper_engine.py: deterministic pure replay, no broker/network.
  - src/paper_scenarios.py: 14 controlled synthetic checks.
  - src/paper_store.py: append-only content-addressed paper_replay_runs.
  - src/paper_routes.py: authenticated /api/paper endpoints.
  - src/static/cockpit.html: integrated UI.
  - docs/paper-trading-lab.md: usage, assumptions, limitations.
- Paper endpoints: GET /api/paper/scenarios, POST /api/paper/replay, GET /api/paper/runs, GET /api/paper/runs/{run_id}, GET /api/paper/runs/{run_id}/trades.csv.
- Existing risk policy: INR 980,000 capital, 1% planned risk inclusive of estimated costs (INR 9,800), one daily filled entry, long only, no leverage.
- Existing trade manager: cost-breakeven stop request after 1.5 price R; EMA10 close exit. No fixed 2R take-profit model.
- Test assumptions default to entry window 09:45–11:30 IST and flatten request 15:15, explicit per-share cost, adverse slippage, tick size and volume participation. They are NOT verified broker fees or an approved live strategy change.
- Later-bar entry only; stop-first ambiguity; stop changes effective next bar; EMA exit next open. IOC partial entry remainder cancelled; partial/unfilled exits stay pending; gap losses can exceed risk budget.
- Missing/duplicate/future/out-of-order/cross-session data fails closed. One normal 2026 session per run, max 25 plans/75 bars each, 2 MB body cap.
- Identical normalized inputs + engine version reuse one immutable run. Costs/cash/partial-exit realised P&L/open-position estimated P&L reconcile.
- Supplied EMA/reference declarations remain unverified. This is replay/failure injection, NOT live-feed forward paper trading.
- Paper schema initializes on first persisted replay, not deployment. Stateless mode explicitly disclosed if no DB; DB errors return safe 503 rather than claiming persistence.

## Validation evidence
- Final PR #6 tested head: 669cd47a984033e6a3451e4f36d01a07259a0523.
- CI: https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41192714819
- 281 Python tests passed including PostgreSQL 18 concurrency/idempotence tests.
- Both Chromium suites passed: existing cockpit and new paper UI, desktop and 360px mobile, downloads/history/locking.
- 14/14 controlled synthetic scenarios passed. These are software checks, not trading results.
- Review screenshots: cockpit-ui-review artifact on that CI run.
- Local temporary artifacts/tests are reproducible; do not assume their paths/runtime objects survive into a new chat.

## Current blocker and next work
Mayur supplied the requested Dhan RELIANCE NSE 5-minute screenshot on 31 October. Selected candle: 30 October 2026 09:15 IST. OHLC: 1170.40 / 1174.60 / 1162.70 / 1164.30. This is chart evidence only; an API match has NOT yet been demonstrated.

A proposed read-only `/api/dhan-chart-reconciliation` endpoint compares exact OHLC under both timestamp hypotheses. It remains on the review branch until release approval. Read docs/forward-paper-readiness-2026-10-31.md. Monday 2 November automatic forward paper trading is NOT READY: live signal binding, full-session collection/position management, durable forward ledger and failure tests remain outstanding. The existing cron ends in the morning. No new production changes or revised exit policy have been approved.

Latest startup audit on deployed instance:
- FETCHED_AUDITED; orders_enabled=false; timestamp_verified=false.
- Padded historical fetch produced 3 sessions of 72 candles, 28–30 October; opening boundary recovered by a wider request (not synthetic filling).
- Historical scanner result WAIT; no trade implied.
- Chart reconciliation and daily CAS eligibility remain unverified.
- Existing scheduled pipeline assumes timestamps_are_open=True and 72 expected bars for research but labels those assumptions unverified.
- Saved CAS master observation: research/2026-10-30/cas-master-observation.json. Field ElgbltyClsgAuctnSsn is 1 for RELIANCE; 85 pool names have 1, 18 have 0. File interpretation and historical daily classification not yet verified.
- Official NSE CAS page: https://www.nseindia.com/static/products-services/closing-auction-session
- Dhan historical docs: https://dhanhq.co/docs/v2/historical-data/
- Recheck current authoritative NSE circulars and effective dates before codifying CAS timing; October rule changes/search results may differ from the overview page.
- Important forward-model issue to resolve: 72 bars end at 15:15 close, while a 15:15 next-open flatten request requires a subsequent executable bar. Current replay intentionally leaves that position unresolved. Do not invent an auction fill or silently mark it closed. Choose and review a session-aware flatten policy before forward paper release.
- After chart check: bind immutable scanner signals and dated reference evidence to verified read-only candles, capture forward sessions, test stale-feed/reconnect/restart/idempotence, compare prices and costs, then assess out-of-sample outcomes. Prepare reviewable code/PRs and ask before deploying further changes.
- Never enable real-money orders under existing approvals.

## Context Mode and chat continuity
- User explicitly asked whether Context Mode is reducing token spend.
- Honest status at handoff: Context Mode is available but was not effectively used in this build. ctx_stats reported 0 tokens saved; do not claim savings retroactively.
- Future workflow: use Context Mode for bulk source/log processing and indexed retrieval; return only relevant excerpts/summaries. Filter connector payloads in code before returning them. Batch independent reads. Never index credentials/secrets.
- Context Mode reduces content entering the LLM context; it does not automatically reduce every model call, guarantee a billing reduction, or prevent a chat limit. Runtime statistics are estimates, not billing records.
- Keep this GitHub handoff current at milestones. Do not rely exclusively on automatic ChatGPT memory, prior-chat compaction, Context Mode's local index, or ephemeral functions/node/CUA state.
- New-chat starter: "Continue Intraday Trading Automation. First read docs/PROJECT_HANDOFF.md in Mayuragarkar2020/intraday-trading-automation. Use Context Mode for bulk analysis. Continue until you need my input or approval; do not make unapproved production changes."
