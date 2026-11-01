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

This pair-level library does not claim complete full-pool candidate coverage.
A future coordinator must derive all valid pairs for an interval from stored
coverage, rather than trusting a caller-chosen subset. Contract verification,
automatic interval assembly, full-session position feed, pinned execution
assumptions/account identity, feed-independent clock scheduling and incident
recovery remain required before activation. No paper runtime is wired yet.

Local targeted checks: 63 passed, three PostgreSQL-only skipped before the final
golden fingerprint assertion. Full exact-head CI is required. The synthetic test
covers stored IDs -> liquidity winner -> later receipt fill -> pre-1.5R EMA request
-> later exit, restart/audit/cash reconciliation. Actual data/session/reference
verification and market coverage remain unproven. PR #12's approved recorder is
live separately; reviewed calendar still ends 6 November.

Do not deploy or activate this later proposal under the PR #12 recorder approval.
