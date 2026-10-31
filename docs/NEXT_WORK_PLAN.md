# Next work plan — automatic paper trading
Updated: 31 October 2026. Read PROJECT_HANDOFF.md first.

## Immediate checkpoint
PR #8 is implemented and tested but awaits approval for merge/deploy, enabling
the capture flag, and extending the existing cron schedule. Updating context
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
