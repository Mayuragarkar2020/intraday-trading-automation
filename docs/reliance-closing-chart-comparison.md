# RELIANCE closing-chart comparison — proposed web-only release

31 October 2026. Mayur supplied two Dhan NSE regular five-minute screenshots
for 30 October. Their selected candle labels and exact visible OHLC are:

| Chart label IST | Open | High | Low | Close |
| --- | ---: | ---: | ---: | ---: |
| 15:05 | 1161.30 | 1163.50 | 1160.50 | 1163.30 |
| 15:10 | 1163.30 | 1163.90 | 1158.40 | 1159.00 |

The 15:10 candle appears as the final visible chart candle. These are
user-supplied visual observations, not API responses. Raw screenshots remain
in the chat; research/2026-10-30/reliance-closing-chart-observations.json retains
the transcription and scope. No API match has yet been demonstrated.

## Proposed comparison

Authenticated POST /api/dhan-closing-chart-reconciliation uses the existing
Dhan secret mechanism and fixed RELIANCE/2885, NSE_EQ, five-minute padded
29–31 October historical request. There is no caller-controlled symbol/date,
no order endpoint, and no database/trading-state write.

Both observations are compared exactly against OPEN and CLOSE timestamp
hypotheses. Full agreement requires two unique matches using the same
convention. Partial, conflicting and ambiguous results stay inconclusive.
The response reports raw target-date count/first/last timestamps and any raw
timestamps at or after 15:15 without inventing continuous/auction semantics.
The fingerprint is SHA-256 of decoded requested-field JSON, not raw HTTP bytes.

Diagnostics adds Compare closing candles with Dhan. It shows each candidate's
raw timestamp/OHLC and the bounded scope. Authentication, response/session
guards, lock clearing and mobile overflow are covered. The original 09:15
comparison and response format remain supported.

All timestamp/CAS/forward-readiness flags remain false. Absence of a candle in
a response is not session-closure proof. This does not alter 15:15 replay
flatten defaults or approve an earlier flatten request. No broker orders,
forward ledger, account state, cron schedule, flag or new service is involved.

## Release boundary

Requires separate approval to merge/deploy to the existing web service only.
PR #9 ledger/signal source must remain excluded. Keep auto-deploy off. After
approval, verify exact merged source and deploy, then have the user run the
new authenticated Diagnostics comparison and retain the result. Passing CI
with fixtures is not an observed production/broker match.
