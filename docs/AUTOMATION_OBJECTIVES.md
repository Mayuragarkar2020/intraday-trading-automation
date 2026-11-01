# Automation objectives and mechanics

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


Confirmed with Mayur, 31 October 2026. Keep engineering tied to this workflow.

1. Build the daily liquid NSE stock universe from the previous twenty completed
   sessions using the existing liquidity/price settings. Exclude 2%/5% bands;
   hold unknown band/identity data. Preserve existing surveillance exclusions.
2. Scan each selected stock after completed five-minute candles against the
   existing EMA10/EMA20, VWAP, relative-volume, 15-minute trend and range setup.
   Setup-ready records contain the range-high-plus-buffer entry and
   range-low-minus-buffer initial stop. A later breakout is needed for entry.
3. Size within INR 980,000 available capital, INR 9,800 maximum planned risk
   including estimated costs, long only, one filled entry/day, no leverage.
4. Keep the initial protective stop; at 1.5 price R request cost breakeven.
   EMA10-close exits are active BEFORE 1.5R too. Mayur explicitly chose to keep
   this current code behaviour when asked. Do not gate EMA exits behind 1.5R.
5. Test actual entries/exits through the separate paper simulator and durable
   ledger before any real-money activation. Fill assumptions and pending exit
   exposure must be visible. All positions must be closed by 15:00 IST, as
   confirmed by Mayur on 31 October. Start exits early enough to meet that
   deadline; never treat an exit request as a confirmed fill. The existing
   15:15 replay default remains in code pending implementation/review.

Universe selection does not require daily manual chart checks for every stock.
Chart diagnostics are bounded integration/exception checks, not daily user work.
Full-universe scanner coverage and trade-management work take priority over
additional diagnostics. PR #10 stays unapproved; it is not a prerequisite for
the universe/scanner research release. No existing approval covers live orders
or later releases. Source and tests may proceed; production changes require
Mayur's approval of the concrete release.

Working ranking rule accepted 31 October: when several valid breakouts occur
in one five-minute interval, prefer highest 20-day average traded value. Keep
ranking versioned and replaceable as more factors are introduced. Equal values
use symbol/security ID for deterministic ordering. This is a source-development
rule, not forward-paper runtime activation. Completed-interval selection must
never generate a fill earlier than the actual selection decision.
