# Next work plan — automatic paper trading

## 1 November 2026 — inactive deadline and persistent manager source

PR #9 now proposes replay v2: force_exit is a completed-closure deadline, default
15:00 IST, capped at 15:00. Flatten attempts start ten minutes earlier. Partial,
unfilled or late exits stay visible; late recovery retains the deadline breach.
Old stored replay runs are immutable; the engine-version change creates new IDs.

An inactive receipt-time simulator connects ranked entry reservations to durable
fills, initial/cost-breakeven stops, EMA10 exits before 1.5R, partial/rejected exits,
clock-driven flatten requests and persistent breach state. Its fill model is
NEXT_TIMELY_CLOSE_AT_RECEIPT, distinct from historical replay next-open fills.
A signal/order decision cannot use an earlier bar. Gaps cannot generate fills.
Clock events request/cancel/flag exposure but cannot manufacture closing prices.
All effects of one bar are journaled atomically; retries/concurrent workers and
restart audit are tested. Source attestations are caller declarations until a
trusted adapter verifies them; current research sources MUST remain held.

Local checks: 139 passed, four PostgreSQL-only skipped. Exact-head CI must be
checked on the current PR head; do not reuse the former 447-test result.
No runtime/API/cron imports the simulator. No production changes or activation.
The verified signal adapter, authoritative session/reference contracts and actual
full-universe operation remain incomplete. Calendar still ends 6 November.
Next: inspect CI, verify actual 2 November research operation and evidence, bind
trusted persisted signals/receipts, then obtain approval for a concrete release.

Updated: 31 October 2026. Read PROJECT_HANDOFF.md first.

## Latest decision and resume checkpoint — 15:00 IST closure

Mayur confirmed on 31 October 2026: **all positions must be closed by 15:00 IST
(Asia/Kolkata)**. This is a completed-closure deadline, not permission to wait
until 15:00 to start an exit. It supersedes the former 15:15 strategy default
and the earlier pending exit-time question. Implement prospective exits early
enough for the chosen execution model; never backdate a fill or report an
unfilled/partially filled position as closed. Any failure to flatten by the
deadline must remain visible as outstanding exposure and a deadline breach.
Exact execution lead time/retry mechanics remain engineering work, not a newly
agreed trading rule. Existing replay code still uses its old default until a
reviewed source change; this documentation update does not change runtime.

Continuity summary:
- Daily liquid NSE universe; exclude 2%/5% bands, hold unknown band/identity
  data and preserve surveillance exclusions. No daily manual chart checks.
- Scan completed 5m bars using the existing EMA10/20, VWAP, relative-volume,
  15m confirmation and range conditions; entry above range high plus buffer,
  initial stop below range low minus buffer, later eligible breakout required.
- INR 980,000 capital, maximum INR 9,800 planned risk inclusive of estimated
  costs, long only, one filled entry/day and no leverage.
- Working ranking: highest 20-day average traded value among valid breakouts
  in the same 5m interval; policy remains replaceable for future ranking factors.
- EMA10-close exits remain active before 1.5R. At 1.5 price R additionally
  request cost breakeven. No fixed target. All exposure closed by 15:00 IST.
- PR #11 is deployed at 5b9693c657f1475c1a1fd4a9c3a6a8749621eece on existing
  web and research cron. Auto-deploy off; no paper/live execution. Actual
  full-pool market coverage, warm-up and persistence still require observation.
- PR #9 remains draft/unapproved/undeployed: inactive ledger, receipt-bound
  signal journal and ranked prospective reservations. Head
  91bd84736364ea1cc420fd21184b57db2b1033dd passed 447 Python/API/PostgreSQL
  tests and both browser suites in run 41222564313. Local: 79 passed,
  3 PostgreSQL-only skipped. Source holds, immutable retries, concurrency,
  rollback and no-backdated-fill checks passed; actual broker readiness unproven.
- PR #10 remains optional/deferred/unapproved; do not make it a prerequisite.
- Next: implement/test the 15:00 closure rule on the inactive paper branch,
  connect persistent trade management and trusted full-universe signals,
  then prepare a concrete release for approval. Verify market data/session
  contracts and actual operation; current research attestations remain false.
- Next reviewed session: 2 November 2026; reviewed calendar ends 6 November.
  Extend reviewed coverage before expiry. Do not promise automatic paper trades.
- Keep source/tests/context in GitHub, use Context Mode for bulk analysis,
  keep communication simple, and continue until real input/approval is needed.
  No production deployment, configuration change or paper/live activation is
  authorized by this context-recording request. No subagents; no credential exposure.

Older dated checkpoints below retain historical evidence. This latest decision
supersedes their statements that exit timing or the liquidity ranking awaits input.

## Current deployment checkpoint

PR #11 was approved and deployed to existing web + research cron at revision
5b9693c657f1475c1a1fd4a9c3a6a8749621eece. Both deploys are live; full-universe
research flag enabled on cron only. Health/auth checks passed. Actual full-pool
market coverage, warm-up/persistence and a #11 cron invocation remain unobserved.
Read docs/universe-scanner-activation-2026-10-31.md. No paper or real orders.
Working ranking confirmed: highest 20-day average traded value among valid
breakouts in the same five-minute interval, replaceable as factors evolve.
End-of-day policy confirmed: all positions closed by 15:00 IST. Old pending-approval statements below describe
source checkpoints before this activation.

## Current work order after Mayur's simplification

Read docs/AUTOMATION_OBJECTIVES.md. Priorities:
1. Keep the daily liquid-stock/band universe automatic; no daily per-stock screenshots.
2. Activate the reviewed full-pool research scanner only after approval (PR #11).
3. Inspect actual coverage, source freshness and broker/runtime behaviour in a market session.
4. Continue the paper execution/ledger work on PR #9 using the confirmed mechanics.

Mayur confirmed EMA10-close exits remain active before 1.5R; preserve existing
trade-manager code. The 1.5R threshold additionally requests cost breakeven.
PR #10 is optional diagnostic work, not the next prerequisite or an approved
release. Earlier chronological plans below remain historical context.

PR #11 tested head 874680b4860506106add2e965c66917d6d928121: 365 full tests
and both Chromium suites passed (run 41219670517). Pending approval scope:
merge/deploy existing web + research cron; set UNIVERSE_SCAN_ENABLED=true on
cron only; keep schedule/compute plans/auto-deploy off/capture flag as is.
No new service; more requests/runtime. No paper or live execution activation.

## Immediate checkpoint
PR #8 was approved, merged and deployed on 31 October 2026; the capture flag and
extended existing cron schedule are configured. A Saturday smoke run exited
MARKET_CLOSED successfully. Actual eligible-session capture/persistence remains
unobserved. See docs/forward-capture-activation-2026-10-31.md. Updating context
does not authorize those changes. Further reversible source implementation and
tests may proceed on review branches. Never silently deploy later work.

## Work order and acceptance criteria
| Stage | Deliverable | Required evidence |
|---|---|---|
| 1. Activate research capture after approval | Existing cron records RELIANCE candles across the session | Intended deploy/config verified; same-day universe published; actual first-seen timestamps and PostgreSQL observations inspected |
| 2. Verify feed and sessions | Dated instrument/session contract and explicit closed-candle convention | Additional independent candle/boundary checks; authoritative CAS/effective-date evidence; unknown inputs hold |
| 3. Bind signals | Immutable scanner signal and dated reference revision | Signal known-at precedes order eligibility; symbol/ID/date/hash agree; synthetic/uploaded diagnostics cannot enter forward stream |
| 4. Build paper ledger | Separate persisted account, orders, fills, positions and events | Idempotent signal/order IDs; atomic state transitions; no duplicate entry under concurrent/restarted workers; account reconciliation |
| 5. Execute simulation | Later-bar entries, stops, EMA exits and explicit session-aware flatten | Locked policy preserved; costs/slippage/volume assumptions disclosed; stop-first ambiguity and partial/rejected fills tested; no auction fill invention |
| 6. Recover and monitor | Restart/reconnect/stale-feed holds and visible state | No backdated orders after outage; pending exits/open exposure preserved; replayable audit trail and alerts/status |
| 7. Release and validate | Reviewed deployment with full-session schedule | Separate production approval; authenticated persisted results; compare observed prices/costs through 3–5 live market sessions |

This sequence can overlap in source development; validation cannot be fabricated
before live sessions happen. Research capture alone is not simulated execution.

## Critical design constraints
- Start with RELIANCE only. Expansion to 103 stocks needs explicit coverage,
  symbol-specific evidence, throughput/rate-limit review and tests.
- Account: INR 980,000; one filled entry/day; 1% planned risk inclusive of estimated costs; long only; no leverage.
- Maintain the existing 1.5 price-R cost-breakeven request and EMA10 close exit.
- A signal is eligible only after it was recorded as known. Do not reconstruct
  supposedly live orders from a complete day fetched later.
- Backfilled candles remain research evidence, not timely trade events.
- Immutable observations can detect revisions; do not overwrite history to make
  a strategy look as though it saw corrected prices at the original time.
- Separate execution time, exchange candle time, receipt time and signal-known
  time. A bar's opening timestamp is not its completion time.
- Make session-aware flatten policy reviewable before activation. Earlier
  flatten examples are proposals, not approved rules. Unknown CAS/holiday/
  special-session classification holds.
- Persist partial fills, pending exit quantities, stops, cash, costs and P&L
  atomically. A restart must retain both open exposure and used daily entry.
- Feed failure cannot be converted into a favourable exit or a flat account.
- No live broker order endpoint is authorized.

## Required failure scenarios
Missing opening/intermediate/last candles; duplicate/out-of-order/future data;
stale feed; cross-session contamination; wrong ID/reference date; revised bar;
expired token; API timeout; database outage; duplicate cron ticks; concurrent
workers; process crash before/after commit; reconnect backfill; entry rejection;
partial IOC entry; stop-change rejection; exit rejection/partial exit; gap
through stop; no executable bar at flatten; fees/cash/P&L reconciliation.

## Definition of complete
Automatic paper entries and exits use actual read-only market data, with
immutable source/signal evidence, a durable separate ledger, restart/concurrency
safety, explicit session rules, and explainable matching cash/position/P&L.
The intended approved deployment is live and actual market-session outcomes
have been inspected. CI success, synthetic scenarios, a menu, or a historical
replay alone does not satisfy this milestone. No minimum profit is implied.

## Estimate and communication
Previously communicated estimate: 2–3 focused working days to implement, plus
3–5 live market sessions to validate. It is provisional and depends on data,
session evidence, approved policies/releases and failures found during testing.
Do not promise Monday automatic paper trades. Distinguish implemented,
tested, approved, deployed, observed and validated at every update.

## New-session first actions
1. Read the handoff and this plan; inspect main and PR #8 current heads.
2. Determine whether Mayur has approved the pending capture activation.
3. Recheck current CI and Render state without revealing secret values.
4. If approved, carry out only the reviewed capture activation and verify it.
   If not approved, prepare remaining ledger/execution source independently.
5. Keep documentation synchronized at milestones and explicitly request the
   next production/policy approval only when the change is concrete and reviewable.

## Source progress after the initial checkpoint

Draft PR #9 (codex/forward-paper-ledger, stacked on #8) adds the inactive
ledger accounting foundation only. Tested head 03106d39fd82ec00b5372e51323b54fb25d6371e:
372 Python/API/PostgreSQL tests and both Chromium suites passed in run
41210571449. Local targeted checks: 110 passed, 2 PostgreSQL-only skipped.
See PROJECT_HANDOFF.md and docs/forward-paper-ledger.md on the review branch.
Stages 3–6 remain incomplete: declarations are not verified scanner/feed
bindings, and no automatic forward executor/runtime has been connected.
No production change or activation is authorized by this source work.
PR #8 recorder activation is complete; eligible market-session validation is
pending. PR #9 remains unapproved and inactive.

Current next steps: inspect Monday's same-day universe and first-seen capture
observations, verify session/timestamp contracts, then bind trustworthy signals
to the inactive ledger. Do not treat an existing historical research scan as
an execution-ready forward signal: it lacks persisted receipt/source binding.

PR #9 expanded source checkpoint: 390 full Python/API/PostgreSQL tests and both
Chromium suites passed at head 1a529075c68e43bb2e40c207aaadf0b1d5b0805c (run
41213273260). It now computes an immutable receipt-bound research signal from
committed capture evidence, but supplied reference prices and session contracts
remain unverified. It cannot create paper orders. All later source remains
draft/unapproved/undeployed. See the latest handoff and session evidence note.

## Closing-chart input received; comparison release pending

Mayur supplied the 30 October RELIANCE 15:05/15:10 chart screenshots. Exact
observations are retained in research/2026-10-30/reliance-closing-chart-observations.json.
The screenshot request is fulfilled. No API match is yet observed for these
closing candles. PR #10 prepares a separate read-only authenticated Diagnostics
comparison, tested at e89b32bbaf72ab1ab4334caf795b0c84579e2141: 346 full tests and
both Chromium suites passed in run 41214406739. It is not approved/deployed.
Next production decision is PR #10 web-only merge/deploy, keeping PR #9 excluded
and the research cron unchanged. After an approved deploy, inspect the actual
comparison result before expanding timestamp/session verification or proposing
an executable exit policy. Earlier flatten times remain unapproved proposals.
