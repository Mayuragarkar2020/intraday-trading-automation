# Inactive persisted-receipt to paper bridge

1 November 2026. Source library only. No endpoint, scheduler, activation flag,
broker order call, credential read or production database write is introduced.

The bridge accepts committed setup/breakout receipt IDs, never uploaded candles,
prices, ranking scores or source flags. Store reads validate retained integrity.
An ARMED setup must be known before the *opening* of a later breakout candle.
Its initial stop must survive the complete path. Only the first eligible later
breakout is used. Completed-bar evidence becomes known at/after interval close;
a prospective decision within 90 seconds cannot fill that past interval.

When future verified source gates and a VERIFIED_PAPER_UNIVERSE are available,
twenty-day average traded value is taken from the hash-bound same-day universe.
Reservations retain both receipt IDs in immutable ranking evidence. Management
reads a later committed receipt, rebuilds EMA10 from retained prices and dispatches
to the existing receipt-time simulator. Initial stops, EMA exits before 1.5R,
cost breakeven, one daily fill and unlevered risk/cash rules are preserved.
Computed EMA retains Decimal precision; rounding it onto the price grid could
change close-below-EMA decisions. Existing tick-batch fingerprints remain stable.

## Current holds and remaining integration

The current universe producer writes LIQUIDITY_RESEARCH_ONLY and false reference/
calendar clearance, and current receipts write all four verification flags false.
This bridge cannot promote those states. There is NO production writer for the
future verified source/universe formats. Tests explicitly construct synthetic
future clearances to exercise wiring; they are not proof of real verification.
Real stored research receipts are tested to hold without touching the ledger.

reserve_interval reads an entire committed scan cycle, holds incomplete coverage,
and derives pairs for every selected instrument from retained receipts. The most
recent ARMED setup known before that bar opens is the working setup. Callers do
not choose the ranking subset. The pair-level helper is an internal building
block; a future runtime must use the coverage coordinator. Bounded JSON queries
avoid loading multi-day full-pool candle payloads into RAM. Duplicate workers reuse
only committed original decision times, while changed costs/inputs still conflict.

Contract verification, full-session position feed, pinned execution assumptions/
account identity, feed-independent clock scheduling and incident recovery remain
required before activation. No paper runtime is wired yet.

Local targeted checks: 47 passed, 12 PostgreSQL-only cases skipped before the final
backwards-clock guard. Full exact-head CI exercises both SQLite and PostgreSQL,
including the interval coordinator and source-to-fill/exit path. Golden tick-batch
fingerprint compatibility is checked against the deployed pre-bridge source.
Actual data/session/reference verification and market coverage remain unproven.
PR #12's approved recorder is live separately; calendar still ends 6 November.

Do not deploy or activate this later proposal under the PR #12 recorder approval.
