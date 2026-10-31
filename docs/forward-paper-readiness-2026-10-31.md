# Forward paper readiness — 31 October 2026

## Decision for Monday, 2 November

Automatic forward paper trading is **NOT READY**. The deployed Paper lab is a
deterministic replay/failure-injection tool. It does not subscribe to market
data, bind immutable scanner signals to paper orders, or manage a persisted
forward position throughout the session. The existing cron runs morning research
only; automatic scanner coverage remains RELIANCE, not the 103-stock pool.

## Chart observation supplied by Mayur

Mayur supplied a Dhan chart screenshot in this conversation on 31 October 2026.
The visible chart is RELIANCE INDUSTRIES, NSE, regular 5-minute candles, timezone
UTC+5:30. The crosshair label is Friday 30 October 2026 09:15.

| Field | Screenshot value |
|---|---:|
| Open | 1170.40 |
| High | 1174.60 |
| Low | 1162.70 |
| Close | 1164.30 |

These values are a manual transcription of the supplied screenshot. The image
itself is not embedded in this repository. They are **not an API observation**.
The deployed diagnostics report coverage but do not expose the required price
comparison. No broker/API match has yet been demonstrated to the agent.

## Proposed read-only reconciliation release

POST `/api/dhan-chart-reconciliation` uses existing cockpit authentication and
the server's existing Dhan token. It fetches a fixed, padded historical window
for NSE_EQ/EQUITY security ID 2885. It compares the screenshot's exact OHLC with
raw timestamps 09:15 and 09:20 to distinguish open- and close-labelled hypotheses.

The response is SAMPLE_MATCHED for exactly one matching hypothesis, AMBIGUOUS
for two, and NO_MATCH for neither. Malformed arrays/values, unordered/duplicate
timestamps and fetch failures fail closed. Broker exception messages and tokens
are never returned. Only the two candidate candles are exposed, behind auth.
No database writes, scheduled task changes or order calls are introduced.

Even SAMPLE_MATCHED remains ONE_HISTORICAL_CANDLE_ONLY: it does not establish
all-instrument timestamp semantics, daily CAS eligibility, live-feed quality,
or trading readiness. Existing scanner verification flags stay false.

## Remaining gates before a forward-paper release

1. Run the reconciliation against actual Dhan data and retain the observed result.
   Confirm further candles/session boundaries; do not substitute test fixtures.
2. Establish dated session classification and CAS eligibility for RELIANCE and
   each intended symbol. The saved security-master field alone is insufficient.
3. Review a continuous-session exit policy. With a 15:15 continuous-session end,
   the last bar closes at 15:15; a request to fill at the next 15:15 open cannot
   be assumed executable. Proposed research policy: request flatten before the
   final executable interval (for example 15:10 for this session type), keep
   partial/unfilled positions unresolved, and never manufacture an auction fill.
   This is a proposal, not an approved or implemented rule change.
4. Capture read-only current candles throughout the session with an explicit
   freshness gate, closed-candle checks, reconnect/backfill, and immutable
   timestamped signal/reference evidence. Never backdate orders after downtime.
5. Persist a separate paper account/order/fill ledger with restart recovery,
   idempotence and concurrency controls. Replay history alone is insufficient.
6. Test entry/exit failures, partial fills, stale data, gaps, reconnects, restarts,
   duplicate signals and cash/cost/P&L reconciliation end to end.
7. Review and approve the release and its full-session service schedule, then
   deploy and verify authenticated persistence and real-feed observation.

Monday can be a supervised research/data-validation session if the premarket
refresh and Dhan access succeed. It should not be presented as a validated
automatic forward-paper session. A research HOLD or WAIT is not a trade.

## Official sources checked

- NSE CAS overview: https://www.nseindia.com/static/products-services/closing-auction-session
- NSE CAS historical archives: https://www.nseindia.com/static/reports/closing-auction-session-historical-data

The overview describes CAS from 15:15 and separate non-CAS continuous trading
through 15:30. The archive lists 30 October. These pages corroborate the need
for session-aware handling; applicable circulars/effective dates and symbol/day
membership still require reconciliation before codifying a forward session.

## Approval boundary

This proposal changes no production state. Approval is required to merge/deploy
the reconciliation endpoint to the existing web service. That release does not
authorize real-money trading, forward-paper operation, or a changed exit rule.
