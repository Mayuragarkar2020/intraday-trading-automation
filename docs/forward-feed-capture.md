# Forward market-data capture — proposed release

## What this delivers

An opt-in RELIANCE NSE five-minute **research recorder**, using the existing
Dhan historical endpoint and PostgreSQL. It records completed current-session
candles and actual first-observation timestamps after receiving the broker
response. It creates no paper positions, simulated fills, or broker orders.
It does not make automatic forward paper trading ready.

The user ran the approved PR #7 reconciliation on 31 October 2026 and reported:

| Raw timestamp, IST | Open | High | Low | Close | Chart match |
|---|---:|---:|---:|---:|---|
| 30 October 09:15 | 1170.4 | 1174.6 | 1162.7 | 1164.3 | Exact |
| 30 October 09:20 | 1163.7 | 1166.0 | 1163.1 | 1163.6 | No |

Evidence source: user-pasted output from the authenticated production comparison,
not an agent-observed response or a retained raw broker response. This supports
open-labelled timestamps for one RELIANCE candle. It does not verify other
instruments, all session boundaries, or daily CAS classification.

## Behavior and integrity

- Runs only on the reviewed 2–6 November calendar, within the conservative
  09:20–15:25 IST capture window. Weekend/unreviewed dates exit before DB writes.
- Requires a same-day-published research universe and exact reviewed twenty
  reference dates, a unique RELIANCE/2885 mapping, and no exclusion/identity hold.
  The pool's existing research-only status never becomes trading approval.
- Uses the existing open-labelled adapter, with its validation and incomplete
  candle filter. Retains only current-date candles through 15:15. The cutoff is
  a conservative research boundary, not verified daily CAS eligibility.
- Reports missing slots, stale observations (over 90 seconds), or a fresh latest
  observation. A fresh last candle does not mean earlier candles were seen live.
- `forward_research_candles` keeps each candle and its first observation immutable.
  Late candles are explicitly backfill; they cannot become backdated trade events.
- `forward_research_observations` retains each received observation, source hash,
  dated universe revision, missing slots and newly inserted/late candle counts.
- Transactional locking serializes writers on PostgreSQL and SQLite. A changed
  candle rolls back the entire observation. Restarts do not overwrite first-seen
  timestamps; the same observation clock cannot identify two different inputs.
- No stateless-success mode: enabled capture requires PostgreSQL. Logs omit
  credentials, connection strings, prices and broker exception text.

## Proposed activation (requires approval)

No production settings have been changed for this proposal. Default
`FORWARD_CAPTURE_ENABLED` is absent/disabled. The current production morning
research job therefore keeps its existing behavior.

After approval and CI, deploy the merged revision to the **existing research
cron only**, enable `FORWARD_CAPTURE_ENABLED=true` on that cron, and extend its
schedule from `*/5 3-6 * * 1-5` to `*/5 3-10 * * 1-5` UTC. The command remains
`python -m src.run_scheduled_research`. The process itself gates to 08:30–15:25
IST; captures begin after 09:20. Extra schedule ticks outside that window exit.
The morning universe/scanner retains its own existing time gates.

This increases scheduled invocations and billable runtime, with no additional
service created. No monthly cost estimate is claimed. A finite five-minute poll
is not a tick feed and is not guaranteed to run exactly on the five-minute close.
If a job starts late, that lateness is recorded rather than treated as timely.

Before activation: verify auto-deploy remains off, source commit matches the
approved PR, credentials are configured through existing secret mechanisms, and
the same-day universe publication succeeds. Saturday cannot prove Monday's
forward capture. Once Monday's ticks run, verify FRESH_OBSERVATION and database
rows; missing/stale/fetch failures remain visible holds.

Rollback: disable the capture flag and restore the previous cron schedule.
Keep existing observations; no data deletion or schema rollback is required.

## Still required for forward paper trading

Bind immutable timestamped signals to a separate paper order/fill/account ledger,
approve session-aware flatten timing, verify dated CAS/session evidence, and
test position recovery, partial exits, rejected fills and full cash/P&L
reconciliation. These are not implemented by this recorder. No approval for this
capture release authorizes either simulated order execution or real-money orders.
