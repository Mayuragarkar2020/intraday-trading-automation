# Intraday Trading Automation — authoritative project handoff

Updated: 31 October 2026 (IST). Read this first when resuming.
Owner: Mayur Agarkar. Private repository: https://github.com/Mayuragarkar2020/intraday-trading-automation

## Resume order and source of truth
1. Read this file, then docs/NEXT_WORK_PLAN.md.
2. Inspect current main, open PRs #9 and #10, CI and actual Render deploy/settings. Reconcile changes since this checkpoint before acting.
3. Use current source and dated evidence over older README text, chat memory or general trading memories.
4. Read docs/forward-feed-capture.md on branch codex/forward-feed-capture (PR #8); that document is not on main at this checkpoint.
5. Use Context Mode for bulk code/log processing, indexed retrieval and concise summaries. Never index credentials.

## Working agreement and approval boundary
- Continue authorized implementation/testing autonomously; stop for genuinely missing input or production approval.
- Mayur requires approval before production changes. PRs #5, #6 and #7 were approved, merged and deployed.
- Mayur approved PR #8 recorder merge/deploy, capture flag and extended cron schedule on 31 October 2026. It is merged and deployed; see the activation checkpoint below. PR #9 remains unapproved/inactive.
- No existing approval authorizes real-money orders, automatic forward paper execution, revised exit timing or later releases.
- Keep source, tests, evidence and continuity in GitHub. Temporary local copies are disposable; do not depend on Mayur's computer.
- No subagents unless expressly authorized. Never expose credentials or ask for tokens in chat.
- Do not extract cockpit tokens from browser/page memory. User can unlock the UI using the existing token.
- Render auto-deploy is OFF. Documentation commits do not deploy. Before any manual deployment inspect the exact main commit and confirm only approved changes will ship.
- Current policy differs from older personal trading memories. Do not substitute NIFTY 200, two trades/day, 0.75% risk or fixed 2R targets.

## Current state at a glance
| Area | Verified state |
|---|---|
| Cockpit | Live: https://intraday-cockpit-preview.onrender.com/ |
| Web release | PR #7; commit 4504ecfa5325aa1bc85ab2120954d6b05c319b58 |
| Render web deploy | dep-dbisjhss728c7386v93g — live |
| Safety | /health returned 200, mode PREVIEW_ONLY, execution_enabled=false |
| Protected comparison | Unauthenticated POST returns 401; new UI button exists |
| Paper module | Deterministic replay/failure injection; NOT automatic forward paper trading |
| Scanner coverage | RELIANCE only; NOT the full 103-stock research pool |
| Chart check | User-reported exact API/chart OHLC match for one historical RELIANCE candle |
| Forward recorder | PR #8 approved, merged and deployed on existing cron; actual weekday capture unobserved |
| Monday 2 November | Research/data-validation target; do not promise automatic paper trades |

The web deployment was rechecked through Render after PR #7. Later documentation
commits can make main newer than that live release without changing production.

## Render resources
Confirmed workspace: tea-da6sf5qfngtc73c8jfi0 (My Workspace).
- Web: srv-dbicbu1srm7s73ds0o30, intraday-cockpit-preview, Singapore, branch main, auto-deploy off.
- Research cron: crn-dbimqnbbc2fs73ap21vg, intraday-session-research, Singapore, auto-deploy off.
- Current cron schedule: */5 3-10 * * 1-5 UTC; command python -m src.run_scheduled_research; FORWARD_CAPTURE_ENABLED=true. Application gate 08:30–15:25 IST, capture gate 09:20–15:25.
- PostgreSQL: dpg-dbicbq8ae00c73bqrp6g-a, Singapore, PostgreSQL 18, 1 GB. External access closed.
- SCAN_DATABASE_URL is an internal secret. Dhan/cockpit credentials remain in existing secret mechanisms.
- No new paid service was created for paper replay or proposed capture.
- Do not touch the older suspended Oregon trading-automation service.
- Web-only releases #5–#7 did not redeploy the research cron. Inspect the cron's actual deployed source before any future release; do not assume it equals current web/main.

## Universe and calendar
- Dated evidence: research/2026-10-30/. Twenty exact official NSE sessions from 1–30 October; T-1 boundaries and source hashes preserved.
- 109 liquidity candidates: 103 research candidates, 2 identity holds, 4 exclusions. None is trading-cleared.
- Holds: TECHM, SHRIRAMFIN (corporate-action/ISIN conflicts).
- Exclusions: LIQUIDBEES, LALITHAA (low band); ESDS, WELCORP (ASM).
- HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE means research only.
- Static snapshot intended session: 2 November 2026.
- Daily premarket refresh and immutable PostgreSQL universe snapshots were deployed in PR #4.
- First eligible scheduled publication is expected Monday 2 November at 08:30 IST, subject to successful source fetches/job execution. Saturday deployment did not demonstrate it.
- Reviewed daily-refresh calendar covers target sessions 2–6 November only. Review/extend before expiry; never infer special sessions.
- From 09:15, missing same-day refresh holds instead of starting a late rebuild. Prior/advance publications do not count as today's publication.
- Authenticated /api/universe-research.csv exports the 103 research candidates with explicit source/target/mode.
- Read docs/daily-universe-refresh-2026-10-31.md and source before changing refresh/scheduling.

## Locked implemented trading and replay policy
- Capital INR 980,000; planned risk 1% inclusive of estimated costs, capped at INR 9,800.
- Long-only; one daily filled entry; no leverage.
- Trade manager requests cost-breakeven stop after 1.5 price R, then EMA10 close exit. No fixed 2R take profit.
- Replay assumptions: entry window 09:45–11:30 IST; force-exit request default 15:15; explicit per-share cost, adverse slippage, tick size and volume participation.
- Costs are declared simulation assumptions, not verified broker charges or live approval.
- Later-bar entry only; stop-first ambiguity; stop changes next bar; EMA exit next open.
- IOC partial entry remainder cancelled; exit remainder stays pending. Gap losses may exceed planned risk.
- A flatten request is not a guaranteed fill. With no later executable bar, position remains unresolved.

## Cockpit and paper replay
Views: Overview, Scanner, Universe, Paper lab, Diagnostics.
- Universe separates pool/holds/exclusions; includes evidence, search/sort/pagination and authenticated CSV.
- Synthetic/uploaded diagnostics never populate stored research scanner.
- Lock clears token, private inputs/results/history; response guards reject stale sessions.
- Sources: src/paper_models.py, paper_engine.py, paper_scenarios.py, paper_store.py, paper_routes.py; src/static/cockpit.html.
- Usage and limitations: docs/paper-trading-lab.md.
- Endpoints: GET /api/paper/scenarios; POST /api/paper/replay; GET /api/paper/runs; GET /api/paper/runs/{run_id}; GET /api/paper/runs/{run_id}/trades.csv.
- Bounded finite input; one reviewed normal 2026 session; at most 25 plans/75 bars each; 2 MB body cap.
- Missing/duplicate/future/out-of-order/cross-session replay data fails closed.
- Supplied EMA/reference declarations remain unverified. This is replay, not live-feed forward trading.
- Identical normalized inputs plus engine version reuse an immutable content-addressed run.
- Costs, cash, realised partial-exit P&L and remaining-position estimated P&L reconcile.
- Paper schema initializes on first persisted replay, not deployment. Stateless mode is disclosed if no DB; DB errors safely return 503.
- Authenticated production replay persistence has NOT been demonstrated to the agent. Never claim a saved production run without verification.
- PR #6 CI: 281 Python tests and both Chromium suites passed; 14 controlled scenarios are software checks, not strategy results.

## Chart reconciliation — completed scoped check
Mayur supplied the Dhan RELIANCE NSE regular 5m chart for 30 October 2026,
09:15 IST (UTC+5:30), then ran the authenticated production comparison and pasted:

| Hypothesis/raw timestamp IST | Open | High | Low | Close | Result |
|---|---:|---:|---:|---:|---|
| OPEN / 2026-10-30 09:15 | 1170.4 | 1174.6 | 1162.7 | 1164.3 | Exact chart match |
| CLOSE / 2026-10-30 09:20 | 1163.7 | 1166.0 | 1163.1 | 1163.6 | No match |

- Provenance: user-supplied chart and user-pasted output from production UI; not an agent-observed authenticated response or retained raw broker payload.
- Supports open-labelled timestamps for ONE historical RELIANCE candle. Does not establish all-symbol/all-session conventions, daily CAS classification or live-feed health.
- PR #7 added authenticated POST /api/dhan-chart-reconciliation and Diagnostics → Reconcile RELIANCE chart → Compare with Dhan historical data.
- Source: src/dhan_chart_reconciliation.py. Fixed RELIANCE security ID 2885 and padded historical fetch.
- Report remains ONE_HISTORICAL_CANDLE_ONLY, timestamp_convention_verified=false, cas_eligibility_verified=false, forward_paper_ready=false.
- PR #7 tested source 0e33358d419d53bdb4e05067588c7be759f4e79b: 303 Python tests plus both Chromium suites passed.
- CI: https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41194685872

## Session/CAS issues still unresolved
- Earlier startup audit FETCHED_AUDITED, orders_enabled=false, timestamp_verified=false.
- Padded fetch recovered 3 sessions of 72 candles for 28–30 October; recovery came from wider requests, not synthetic fill.
- Historical scanner WAIT is not a trade.
- Existing scheduled research assumes open timestamps and 72 bars; broader assumptions stay unverified.
- Saved research/2026-10-30/cas-master-observation.json: ElgbltyClsgAuctnSsn=1 for RELIANCE; 85 pool names have 1, 18 have 0. Field interpretation/effective daily history still require verification.
- Official overview: https://www.nseindia.com/static/products-services/closing-auction-session
- Official archive: https://www.nseindia.com/static/reports/closing-auction-session-historical-data
- Broker reference: https://dhanhq.co/docs/v2/historical-data/
- Reconcile applicable NSE circulars, effective dates and per-symbol/day classification before codifying session policy. A Saturday mock-trading circular is not evidence of a normal live session.
- For a 15:15 continuous-session end, 72 bars end at 15:15 close. A 15:15 next-open flatten cannot assume a subsequent executable bar.
- Earlier flatten (for example 15:10) is a PROPOSAL only. Keep partial/unfilled exits unresolved; do not manufacture auction fills or silently alter the locked exit policy.

## PR #8 — approved recorder; activation verified 31 October
URL: https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/8
Branch: codex/forward-feed-capture
Tested source head: 81999fd81c7430070301d45dcfcd8f190a9bddac.
Documentation-only synchronization may advance the branch after this checkpoint;
recheck current head/CI before any merge.

Implemented:
- src/forward_capture.py: current-session candle observations, first-seen timestamps, source hashes, missing/stale/late markers, immutable candles and observation transactions.
- src/run_forward_capture.py: opt-in finite RELIANCE recorder; binds same-day universe revision and exact twenty reviewed reference dates; clocks observation AFTER fetch.
- src/run_scheduled_research.py: default morning behavior retained; extended capture window only if FORWARD_CAPTURE_ENABLED=true.
- tests/test_forward_capture.py: duplicate/concurrent writers, restarts, conflicts, rollback, clock/reference gates, stale/gap/reconnect cases, decimal-encoding equivalence and PostgreSQL concurrency.
- Tables: forward_research_candles and forward_research_observations; created only on actual capture.
- A revised candle rolls the whole observation back. 100 and 100.0 canonicalize equally.
- Conservative capture cutoff 15:15 is research scoping, not verified daily CAS classification or an approved flatten rule.
- NO simulated orders, fills or forward account ledger. Capture does not complete automatic paper trading.

Validation:
- 327 Python tests passed including PostgreSQL 18 concurrency; both Chromium suites passed.
- CI: https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41195680196
- Local targeted tests: 23 passed; PostgreSQL exercised in CI.
- Local Windows TestClient hangs at asyncio socketpair under sandbox; use CI evidence for API/browser coverage rather than claiming local success.
- Local pytest temporary-directory restrictions were avoided with a new workspace basetemp.

Approved request (Mayur answered on 31 October 2026; activation details below):
Merge/deploy PR #8 to the EXISTING RESEARCH CRON, enable
FORWARD_CAPTURE_ENABLED=true, and extend schedule from */5 3-6 * * 1-5 to
*/5 3-10 * * 1-5 UTC. Command unchanged. Additional invocations/runtime cost;
no additional paid service. Keep auto-deploy off. No web deploy is needed
for the recorder-only code. Those approved production settings are now active; see the exact deployment checkpoint below.
Render cron/deploy skills, settings and intended merged commit were checked;
the recorder build is live. Actual
weekday observation/persistence must be checked separately.
Rollback proposal: disable capture flag and restore previous schedule;
retain immutable evidence.

## Remaining automatic paper milestone and timing
Read docs/NEXT_WORK_PLAN.md for the work order and acceptance criteria.
Remaining: verified feed/session contracts; immutable signal-to-order binding;
separate persistent paper account/order/fill/position ledger; simulated entries,
stops, EMA/flatten exits; restart/concurrency recovery; realistic declared
cost/slippage/partial-fill handling; full-session observability and failure tests;
approved release and actual market-session validation.
Prior estimate communicated to Mayur: 2–3 focused working days for implementation,
then 3–5 live trading sessions for validation. Planning estimate only, not a
deadline, background-work commitment, or guarantee. Expand if gates uncover issues.
Monday 2 November is a data-recording/validation target, contingent on approval
and operational success, not promised automatic paper trading.
No work continues between chat turns unless an explicit automation/service does it.

## Context Mode and continuity
- Earlier handoff reported ineffective Context Mode use and zero savings; do not rewrite that historical fact.
- Context Mode IS now used for bulk source retrieval/indexing, selected excerpts and filtered test output.
- Runtime statistics estimate avoided context volume, not billing savings or immunity from chat limits.
- GitHub handoff is durable authority; Context Mode local index, chat history, node/CUA bindings and local test copies are not.
- Browser verification previously failed: in-app tab creation returned a session mismatch; native Chrome inspection stopped because current URL could not be determined safely. Do not bypass safeguards.
- User can run authenticated Diagnostics; never recover tokens from browser memory.
- New-chat starter: "Continue Intraday Trading Automation. Read docs/PROJECT_HANDOFF.md and docs/NEXT_WORK_PLAN.md first. Use Context Mode for bulk analysis. Continue until you need my input or approval; do not make unapproved production changes."

## Earlier checkpoint — inactive ledger foundation (before PR #8 activation)

31 October 2026: draft https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/9
Branch codex/forward-paper-ledger, stacked on PR #8; tested source head
03106d39fd82ec00b5372e51323b54fb25d6371e. Neither PR has been approved or merged.
Read docs/forward-paper-ledger.md on that branch (not present on main).

- Added an inactive accounting library: atomic account projection and immutable
  command/result journal; idempotent retries, serialized concurrent writers,
  daily filled-entry guard, partial IOC entry cancellation, persistent partial/
  rejected exits, restart/audit recovery and exact cash/cost-basis/P&L identity.
- Orders/fills/position are logical JSON projection records; there are not yet
  separate relational order/fill tables. Review projection retention/growth
  before activation. Pin the eventual runtime account ID to prevent resets.
- Caller-supplied source/signal declarations are NOT verified feed bindings.
  No runtime imports the ledger; no API, cron, executor, broker-order call or
  production DB write was added. Session/source gates, breakeven/EMA10 execution
  and actual-market validation remain outstanding. Automatic paper NOT READY.
- Local targeted tests: 110 passed, 2 PostgreSQL-only checks skipped.
- Exact-head CI: 372 Python/API/PostgreSQL tests passed; both Chromium suites
  passed. https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41210571449
- Same-day production recheck: cockpit health 200, PREVIEW_ONLY,
  execution_enabled=false; web still 4504ecfa5325aa1bc85ab2120954d6b05c319b58.
  Cron still 0ce3cdb340d268c397f7adbd905a30a5f4e8edb7,
  deploy dep-dbiqu8oae00c73ceuksg; schedule */5 3-6 * * 1-5 UTC.
  Both auto-deploy settings off. No production changes were made.
- PR #8's recorder-only activation request remains pending. Approval of #8
  must not include #9. If #8 is approved, merge/deploy only recorder source
  plus documentation; do not deploy the ledger branch. Keep #9 draft until
  trusted session/signal/executor integration is reviewed and tested.
- This main-branch documentation checkpoint does not merge either proposal
  or deploy anything. Before the next release recheck actual main and cron.

## Current activation checkpoint — supersedes earlier pending statements

Mayur approved PR #8 on 31 October 2026. It is merged and deployed to the existing
research cron: 69a0c31ec3b4a8a492414b09b8422f774bc50a96,
dep-dbivtvnf3r2c73ej3l7g (live). Capture flag true, extended schedule and auto-deploy
off were verified. One successful Saturday smoke run returned MARKET_CLOSED
with execution_enabled=false. Actual weekday capture/persistence remains
unobserved. Read docs/forward-capture-activation-2026-10-31.md for evidence,
including the environment-update intermediate build and SQL access limitation.
The web remains at PR #7. PR #9 remains draft/unapproved/undeployed; no forward
paper executor or broker ordering was activated. Earlier pending statements
in historical checkpoints describe the earlier time, not current authorization.

## Latest inactive-source checkpoint — receipt-bound signals

PR #9 is now based on main and includes both the accounting ledger and an
inactive research signal journal. Exact tested head:
1a529075c68e43bb2e40c207aaadf0b1d5b0805c. Full CI: 390 Python/API/PostgreSQL
tests plus both Chromium suites passed in run 41213273260. Local targeted
checks: 127 passed, 3 PostgreSQL-only skipped. Read docs/forward-research-signal.md
on codex/forward-paper-ledger; no runtime imports either new module.

The new journal reads committed recorder observations and the original universe
revision, checks hashes, dates, calendar and first-seen timeliness, derives
scanner inputs and freezes full normalized input/result evidence and post-scan
known_at. Conflicting recomputation and reconnect/backfill signals hold. It
always reports forward_paper_ready=false and execution_enabled=false because
reference-price provenance and session contracts are still unverified.
No ledger/order adapter, simulator runtime or production integration is added.

Added dated official NSE CAS evidence: RELIANCE appears in the 30 October
CAS archive. Read docs/session-contract-checkpoint-2026-10-31.md and
research/2026-10-30/cas-session-observation.json. This narrows that day's CAS
uncertainty; it does not certify future dates, all reference days, or broker
candle labels. Originals 73845/74466 remain unread via available PDF retrieval.
Next user-dependent evidence: independent Dhan regular five-minute closing
candle view for RELIANCE on 30 October (last and preceding candle, time/OHLC).
No revised flatten time is approved. Keep open/partial exposure unresolved.

## Latest chart input — closing screenshots received

Mayur supplied the requested two Dhan RELIANCE NSE five-minute screenshots
on 31 October 2026. Visible labels/OHLC on 30 October (IST):
- 15:05: O 1161.30, H 1163.50, L 1160.50, C 1163.30.
- 15:10: O 1163.30, H 1163.90, L 1158.40, C 1159.00.
15:10 appears as the last visible chart candle. No closing-candle API match
has yet been observed. Raw screenshots are in the chat; exact transcription
is in research/2026-10-30/reliance-closing-chart-observations.json.

PR #10 (codex/closing-chart-comparison) prepares a separate web-only authenticated
comparison for these two fixed observations, with a Diagnostics button and
raw target-day timestamp metadata. It preserves the original 09:15 comparison.
It does not deploy PR #9, modify the cron, certify session/CAS/forward readiness
or change exit timing. Inspect current head/CI and obtain separate approval
before merge/deploy to the existing web service only. User input fulfilled the
screenshot request; it did not authorize a new production release.

PR #10 exact tested source: e89b32bbaf72ab1ab4334caf795b0c84579e2141.
CI run 41214406739: 346 Python/API/PostgreSQL tests and both Chromium suites
passed. Local pure checks: 39 passed, 2 API tests deselected for the known
Windows TestClient sandbox limitation. The tests use fixtures, not actual
broker data. PR #10 remains OPEN/UNAPPROVED/UNDEPLOYED. Proposed release scope:
existing web service only; no cron deployment/config change and no PR #9
ledger/signal source. After approval and verified deploy, the user can run
Diagnostics → Compare closing candles with Dhan and retain the actual result.
