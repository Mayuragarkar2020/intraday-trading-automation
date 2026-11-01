# Next work plan — human-selected intraday automation

Updated 1 November 2026. Read AUTOMATION_OBJECTIVES.md and PROJECT_HANDOFF.md.

The objective is simple: scanner shortlists -> Mayur chooses the stock -> system
enters by the agreed rules, manages the trade and journals it. Do not substitute
automatic stock selection for Mayur's decision.

## Work order

1. Deliver the human-choice cockpit: setup shortlist, read-only entry/SL/size/risk
   review, saved/recoverable choice, withdrawal before order, position and journal.
2. Bind the exact choice atomically to a paper entry. Recheck source/selection,
   risk/capital, one daily filled entry and later-bar timing. Never substitute
   another stock, rerank into a different entry or use prices before approval.
3. Connect independently verified receipt data to the chosen stock's entry and
   full-session position feed. The inactive PR #13 adapter must be changed to
   require the saved choice and HumanChoicePaperLedger before it is used.
4. Run the existing initial-SL, EMA10-close, 1.5R cost-breakeven and prospective
   flatten manager. Drive its clock independently of feed success. Close by
   15:00 IST; retain partial/rejected exits and breaches across restart.
5. Expose the actual durable account/fill/decision journal and completed-trade
   outcomes. No retyping trades or daily per-stock screenshots as a prerequisite.
6. Test the COMPLETE user journey with realistic failures, then request approval
   for a concrete forward-paper release. Validate actual market sessions before
   any proposal involving real money.

## Current deployment

- Web: PR #9, d724f82f48a6588acb92770f7a78246355e77b6a,
  dep-dbjbh93bc2fs73cbijl0, live.
- Research cron: PR #12, 6d6e8152da96da2c575a59e0b980448b774d059b,
  dep-dbjbnf67bikc73f03i8g, live. Receipt flag configured.
- Auto-deploy off. No paper/live executor active. PR #10 deferred.
- PR #13 remains draft/unapproved/undeployed; its auto-selection assumption is
  superseded by the clarified human-decision workflow.

## In progress: human-choice release

The cockpit/API save immutable choices from stored setup receipts; ranking is
advisory and a lower-ranked stock can be chosen. Fixed paper account, explicit
cost estimate, risk/size review, idempotence, stale-tab/concurrency guards and a
decision journal are included. Selection never submits an order while runtime
gates are incomplete. HumanChoicePaperLedger checks the exact stock/setup, entry,
initial stop, size envelope and choice time under the account writer lock.

Proposed release after exact-head CI: existing WEB SERVICE ONLY; no cron deploy,
schedule/flag/compute change, broker orders or paper/live activation. Three choice
tables initialize on an authenticated user write, not deployment or a read.

## Data validation in parallel

Observe 2 November's same-day universe, pool coverage, receipt timing and storage
growth. Resolve timestamp/session/reference contracts from actual evidence; never
turn verification flags true merely to advance a milestone. Reviewed calendar
ends 6 November; extend only with verified sessions. Sunday deployment is not an
observed weekday run. Continue useful source integration while these checks wait.

## Acceptance checks

Human choice required; exact stock preserved; stale/revised/wrong-session data
held; no pre-choice or backdated fills; no duplicate under retries/concurrency;
no replacement while a trade is pending/open or daily entry is used; initial SL
and EMA exits before 1.5R; cost breakeven; gaps/partial/rejected exits; feed/DB
outage recovery; deadline breaches; immutable decision/fill journal and reconciled
cash/costs/P&L; authentication, lock clearing and mobile usability.
