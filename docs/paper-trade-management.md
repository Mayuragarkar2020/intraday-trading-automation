# Inactive persistent paper management

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


## Source and execution boundary

src/paper_trade_management.py is a library only. It does not fetch market data,
trust uploads, read credentials, register routes or schedule execution. Its four
source attestations are mandatory holds, not an implemented proof chain. Tests
use synthetic fixtures. Never expose a user-facing endpoint accepting these
attestations as clearance. The current research journal reports false gates.

Reservations bind symbol/security ID/universe and original stop. Every bar stores
its source hash and receipt time. At most one bar per instrument/close/account is
journaled; changed retries conflict. New bar state and all accounting changes
commit together. Paper-clock events must be driven independently of feed success
in a future approved runtime. No runtime is connected yet. Cross-session bars
hold; old exposure needs explicit incident recovery, never automatic backfills.

The ten-minute lead is an engineering assumption, not a closure guarantee. A
14:50 receipt requests flatten; a timely 14:55 receipt can fill; a 15:00:10 receipt
is already late. Rejected/zero-volume/partial attempts keep remaining exposure.
A clock at 15:00 flags any outstanding exposure. Late recovery preserves the flag.
Source gaps block fills; stop and EMA requests still record protective intent.

Prices use adverse slippage, tick rounding and a declared participation cap. IOC
entry is bounded by the reserved limit/risk envelope and cannot reuse the signal
interval. This version consumes the reservation with one eligible bar result;
zero/partial entry remainder cancels. Cost-per-share assumptions must permit
six-decimal half-share fees. Changed execution assumptions are included in each
immutable bar; pin their approved values in the future runtime. No claim of
broker realism, fill priority, all-symbol coverage or actual trading readiness.
