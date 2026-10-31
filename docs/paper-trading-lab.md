# Paper trading lab — replay release

This release tests execution rules without a broker order adapter. It does not submit, amend or cancel real orders. The lab uses explicit test plans; it does not automatically convert the current research scanner into trades. The 103 research candidates are not trading-cleared.

## How to use it

1. Unlock the cockpit with the existing access token and open **Paper lab**.
2. Run the controlled scenario checks. A pass means the software behaved as expected under that injected condition, not that a trading strategy made money.
3. Load the synthetic example to inspect the JSON schema. Change the label/source and provide a dated dataset for a user-supplied replay. Do not label historical data as synthetic or synthetic data as market evidence.
4. Supply one normal 2026 session, explicit signal-close times, trigger/stop/reference declarations, and contiguous subsequent completed 5-minute OHLCV/EMA10 bars. Offset-aware timestamps are bar **closes**. The first replay bar must close five minutes after the signal was known. Up to 25 plans and 75 bars per plan; 2 MB HTTP limit.
5. Review the cost, slippage and volume-participation assumptions before running. Inspect plan rejections, fill events, realised P&L, unresolved positions and the input hash. Download JSON for the full input and audit; CSV contains completed trades only.
6. Load the paper journal to reopen a saved run. The existing research PostgreSQL connection stores runs separately in `paper_replay_runs`. No new cloud service or recurring job is required. If no database is configured, the response explicitly says it is not persisted; download it before leaving.

## Policy versus modelling assumptions

The lab reuses `RiskPolicy`, `size_long`, and the current `trade_manager` decisions: INR 980,000 starting capital, at most INR 9,800 planned risk including estimated round-trip costs, one filled entry per day, long only and no leverage. A partial entry counts as the day's trade. The current trade manager requests cost breakeven after 1.5 price R and exits after a close below EMA10. This is not a fixed 2R take-profit model.

The replay defaults to a 09:45–11:30 entry window and 15:15 flatten request. These windows can be changed **for the simulation** and are recorded in each run. They do not modify a production strategy. Explicit per-share round-trip costs are split equally between entry and exit; these are not asserted to be Dhan's actual fee schedule. Adverse slippage in basis points and tick rounding apply to both sides. Entry sizing includes estimated stop-exit slippage and a tick cushion. Actual gap losses may exceed the planned budget and are flagged.

`price_band: 0` explicitly means no fixed band; 2/5% bands and HOLD/EXCLUDED/UNKNOWN references block entries. `RESEARCH_ONLY` is a declared test input and never grants live eligibility. The lab does not independently calculate or authenticate supplied EMA values or reference declarations. Tick size is an explicit assumption, not an exchange master lookup.

## Fill and event rules

- Only later bars can fill a known signal. Entry/stop ambiguity in a bar invalidates the setup. No automatic entry uses the signal candle's future high.
- Orders compete in chronological bar-close order and then plan-ID order; this stable tie break is a modelling assumption, not an exchange queue. There is one account and at most one position.
- Buy fills use the worse of the trigger and next open, plus adverse slippage and upward tick rounding. Stop exits use the worse of stop and opening price, minus adverse slippage and downward tick rounding. Model prices outside the bar cannot fill.
- Fill size is capped at the declared percentage of that bar's volume (maximum 10%). Partial entry remainders are cancelled (IOC model). Exit remainders stay pending and retry on a subsequent open.
- Stops take priority over close-based EMA and trailing decisions. New breakeven stops apply to the following bar. EMA exits use a following opening price, never the same closing price that generated the decision. Entry-bar extrema cannot request a trailing stop.
- Injected entry/exit/stop-change rejection and `can_fill: false` test failures or missing executable liquidity. They are controlled assumptions, not a realistic order-book model.
- Replays with missing, duplicate, unordered, future, timezone-free or cross-session bars fail. Only the repository's reviewed normal-session 2026 calendar is accepted; special sessions require a later implementation.
- A flatten time is a request, not a guaranteed exit. If no later executable bar exists, the run reports an unresolved open position. It never invents an end-of-file sale. Bar-close equity/drawdown estimates do not measure intrabar drawdown or future performance.

## Persistence and reproducibility

Run identity hashes the engine version and normalized input. Identical inputs are idempotent and never overwrite an existing result. Changed assumptions produce a separate run. Input JSON, result JSON, source label, engine version and event ledger are preserved together. Schema initialization is serialized for PostgreSQL; retries commit once. The lab does not modify scan snapshots, universe evidence, research schedules or broker credentials. The cockpit token stays in memory and is cleared with paper data on lock.

## Coverage and remaining work before money

The controlled matrix covers EMA next-open exit, 5% band, identity hold, rejection, zero liquidity, partial entry, rejected stop change, unfillable exit, ambiguous entry/stop, gap loss, competing signals, and missing/duplicate/future bars. Additional automated tests cover partial exits, force-exit timing, costs/cash reconciliation, invalid numbers, windows, authentication, journal retry/restart, database outages and CSV safety.

Passing these checks cannot test every possible scenario or establish strategy expectancy. This release is **candle replay and failure injection**, not forward paper trading. Next: verify actual Dhan candle timing/session completeness against charts; bind immutable scanner signals and dated universe evidence to a read-only feed; capture several forward sessions with reconnect/restart/stale-feed controls; reconcile simulated and observable prices; then evaluate sufficient out-of-sample trades net of conservative costs and stress assumptions. Broker order-state reconciliation and operational kill/recovery controls must be reviewed before any separate real-money release. Live execution remains disabled throughout.
