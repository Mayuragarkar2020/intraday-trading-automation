# Forward paper ledger foundation - inactive proposal

31 October 2026. Builds on PR #8 without changing its activation request.

`src/forward_paper_ledger.py` is a separate accounting state machine and durable
journal. Nothing imports it from the web app, research cron, feed recorder or
replay engine. Importing it creates no tables. No production database was used.

## Implemented

- INR 980,000 initial paper cash; long only; no leverage; maximum planned
  entry risk INR 9,800 inclusive of the declared fee budget; existing
  09:45-11:30 entry window. Quantities, money, IDs and commands are bounded.
- Entry request binds one caller-supplied signal ID, source hash and universe
  revision. A signal cannot be rebound to another order. These declarations
  are not yet verified against the capture/scanner stores.
- Entry results require a later bar opening after signal-known time and no
  earlier than order creation, in the same session and entry window. The
  ledger receives computed results; it does not manufacture candle fills.
- One pending order/open position per account. Partial IOC entry cancels its
  remainder. Any filled quantity consumes that account's daily filled entry.
  Fully rejected entries remain flat. Daily entry use survives a full exit.
- STOP/EMA10/FLATTEN exit requests are accounting intents only. Zero or rejected
  exit results preserve pending quantity. Partial exits preserve exposure.
  Gap-stop results may realise losses beyond planned risk. No implied auction
  fill or forced flat state is created.
- Cash, actual declared simulation fees, realised partial-exit P&L, remaining
  entry-fee basis, orders and fills are atomically persisted. Fee basis is
  apportioned on partial exit; its residual is allocated on final exit.
- PostgreSQL advisory transaction locks/SQLite immediate transactions serialize
  writers. Immutable event IDs reject conflicting retry payloads. Same-command
  retries return their original result, which can be older than the current
  account; callers must read current state before making another decision.
- The event journal stores immutable command/result snapshots; the account row
  stores the current projection. Orders/fills/position are logical records in
  that JSON projection, not independently queryable relational tables yet.
  `audit` replays commands and compares every recorded projection and final
  account under the writer lock. Database errors propagate without success.

## Explicit remaining boundaries

This is a library for a future trusted executor, not a public ingest endpoint.
It accepts declared commands and does not establish trusted receipt clocks,
verified session/CAS classification, signal provenance, candle timeliness,
EMA10/breakeven rules, volume participation, adverse slippage, cost estimation,
stop replacement or flatten eligibility. No forward executor, scheduler,
monitoring UI, live broker order calls or deployment is included. Session,
source and strategy gates must be implemented before any activation. The
replay engine's existing exit policy remains unchanged.

Current event snapshots retain cumulative orders/fills; before long-running
activation, address retention/projection growth and decide relational views.
Account IDs separate test/research books; production must pin one account ID
and prevent reset/new-account creation from bypassing daily risk constraints.
No runtime API currently exposes account creation or commands.

## Validation

Targeted SQLite tests cover concurrency, idempotency conflicts, rejection and
partial fills, risk/cash/clock validation, daily-fill persistence, restart,
database failure, transaction rollback after journal insertion, projection
corruption and decimal fee reconciliation. A PostgreSQL CI test exercises
concurrent duplicate fills and restart/audit. See the review PR for exact
tested revision and CI results; local PostgreSQL is not claimed.

PR #8 capture approval remains separate and pending. This ledger branch must
not be merged or deployed as part of a recorder-only approval. Automatic paper
trading remains NOT READY pending the work in NEXT_WORK_PLAN.md.

