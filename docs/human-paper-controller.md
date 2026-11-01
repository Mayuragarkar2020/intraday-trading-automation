# Human-selected paper controller — inactive candidate

1 November 2026. Objective: Mayur chooses the stock once; the system performs
subsequent rule-based paper entry, management and journaling. No stock substitution.

## Whole journey

Read the pinned paper-main choice from durable storage. Recheck that exact setup,
current receipt, reviewed date, source clearance, stop validity and risk/capital.
Only a later eligible breakout can reserve the entry. A later full post-decision
bar can produce a simulated fill. The existing initial-SL, pre-1.5R EMA10-close,
additional cost-breakeven and ten-minute flatten-lead manager then runs without
another user decision. Completed trades derive automatically from immutable fills:
choice/setup IDs, entry/exit, quantity, initial SL, fees, net P&L/R, reason and
risk/deadline breaches. Partial/rejected exits stay open, not completed trades.

The choice is checked again under the account writer lock by HumanChoicePaperLedger.
One filled entry/day, long-only, no leverage and Rs 9,800 maximum planned risk
including estimated execution costs remain enforced. An attempted/unfilled choice
does not automatically chase a new breakout or switch stocks.

## Explicit PAPER execution model

NEXT_TIMELY_CLOSE_AT_RECEIPT / PAPER_SIM_CLOSE_V1 is a conservative bar-based
simulation, distinct from historical replay next-open fills or real broker/tick
execution. It may miss/delay entries and cannot establish queue priority or
intrabar path. It is a software rehearsal, not a claim of broker realism or
strategy profitability. No past fill is invented after a choice/decision.
Entry remains inside the selected limit envelope; gap-up fills outside it cancel.

Pin per-order assumptions: Rs 1/share round-trip fees, 5 bps adverse slippage,
0.05 tick and 1% participation. Final risk sizing additionally reserves stop-side
slippage/tick rounding and may reduce the preview quantity. Cost-breakeven requests
cover the declared execution assumptions; gaps/unfilled exits can still lose.
Derived EMA keeps full Decimal precision. A clock's new exit request cannot fill
the same already-completed receipt; it records zero/pending and waits for later data.

## Optional worker and feed

FORWARD_PAPER_ENABLED defaults OFF. No production flag was set and no controller
release/deployment is authorized by PR #14's web-only approval. When separately
approved, the existing scheduler's opt-in branch prioritizes the paper clock/feed
before research. No new service/compute/schedule is required. It would add one
chosen-stock/position historical-data request per needed tick, including after
11:30 for management. Capture normalizes using still-unverified OPEN/session
assumptions and retains the recorder's FALSE verification flags.

Protective clock state is persisted before any network fetch. Missing/stale/
failed data cannot fill an exit or erase exposure. The 15:00 deadline breach
remains visible. Unknown session/calendar/reference/assumption state holds.
Current reviewed calendar ends 6 November. No auction/cross-session recovery fill
is manufactured. Database failure reports exposure UNKNOWN, never flat.

An optional enabled worker writes one operational heartbeat projection
paper_worker_status; no DDL occurs from import/deployment/default-disabled paths.
It does not replace immutable trade evidence. The cockpit distinguishes price
age, worker freshness, pending exposure and completed trades. Trade management
liveness is not inferred from a saved choice or a clock update alone.

## Critical current boundary

Current receipt producers always write all four source-verification flags FALSE.
The research universe cannot supply VERIFIED_PAPER_UNIVERSE clearance. The default
source adapter therefore cannot create entries. No flag, upload or stock choice
can promote these facts. Synthetic future-clearance fixtures in tests exercise
the whole journey but are not real source certification.

Before forward-paper activation, inspect actual market capture and implement/
review independently verified source/reference/session production. Then review
the chosen execution model, actual throughput/latency and exact activation
settings. A genuine complete automatic-paper milestone additionally requires the
approved deployment running and actual market-session outcomes inspected.

Local targeted checks: 31 passed, 14 PostgreSQL-only skipped on the pinned-policy
subset; a broader preceding subset passed 56 with 35 skips. Exact-head full CI
must validate the current complete changes. No production data/fills are claimed.
