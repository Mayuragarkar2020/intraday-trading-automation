# Daily research-universe refresh — 31 October 2026

## Approval summary

Approve updating the existing research scheduler and cockpit, and adding one research snapshot table/index to the existing PostgreSQL database. No new Render service, public database access, credential change, schedule change or order capability is included.

The current 103-name list is not being reapproved for trading. Daily refresh produces a dated research pool using the existing configured thresholds; execution and eligibility verification remain disabled. Intraday scanning still covers RELIANCE only.

## What changes

| Time / condition | Behavior |
|---|---|
| Existing cron first runs at 08:30 IST | Rebuild the day's universe if none was successfully published that day |
| Before 09:15 | Retry on subsequent existing cron ticks if an earlier build failed |
| Successful refresh | Save immutable report/evidence in PostgreSQL; later ticks reuse it |
| From 09:15 | Do not start a late rebuild; hold if that day's refresh is missing |
| Setup window | RELIANCE research requires membership, matching Dhan ID and exact 20-session candles |
| Weekend / configured holiday | Exit before reading or initializing the shared store |
| Unreviewed calendar date | Fail the build; do not extend the calendar by assumption |

An advance publication made on another IST date does not qualify as today's refresh.

The calendar explicitly covers target sessions **2–6 November 2026**, using ordinary-session dates from 1 October and the published NSE holiday circular. The short horizon avoids guessing across the upcoming special-session period. Further target dates require reviewing/extending config/research_calendar.json.

## Source and publication checks

The builder downloads exactly 20 official NSE UDiFF archives, the NSE equity-share list, current NSE price bands, the Dhan instrument master and official NSE ASM/GSM/corporate-action responses. Every archive must parse and match its expected date. The surveillance lists must match the latest reference session date. Wrong/missing/oversized sources, unknown schemas or invalid evidence stop the build.

The Dhan reference parser streams the file and retains only NSE/E/EQ rows instead of materializing the full multi-exchange master. This limits unnecessary memory use on the existing 512 MB service. Corporate-action identity conflicts and exchange surveillance restrictions retain precedence over broker flags.

Published reports contain configuration/calendar hashes, public-source hashes and the parsed official NSE evidence bundle. The original source archives and full master CSVs are temporary and are deleted after the run; their URLs and hashes are retained. No historical adjusted candles, complete target-date eligibility or point-in-time backtest validity is claimed.

Publication uses a single insert transaction with content-hash deduplication. Corrections create another revision; existing records are not overwritten. The universe and its evidence are kept together in universe_research_snapshots, with an index on target_date/created_at. The existing scan_snapshots table is unchanged.

A failed build never publishes a partial new report. Earlier dated reports remain available as evidence, but the scanner will not reuse them for a different target date.

## Cockpit

The authenticated universe endpoint reads the latest shared report. If the table is not yet initialized, empty or unavailable, it displays the committed dated snapshot with an explicit fallback message. The as-of and intended-session dates stay visible. Dashboard reads do not initialize schema or publish reports.

The Download research-pool CSV button exports only the latest pool rows, with as-of/target dates, source, mode and execution-disabled status. The CSV endpoint requires the existing cockpit token and sends no-store caching headers.

All original candidates, including exclusions and holds, remain visible for audit. The research candidate count can change each day. The current static [CSV](../research/2026-10-30/candidates.csv) remains the 30 October research result; this change does not add a replacement list that should be approved manually.

## Deploy and verification

1. Merge the reviewed PR after final CI succeeds.
2. Manually deploy intraday-session-research and intraday-cockpit-preview from the merged commit; automatic deploys remain off.
3. Confirm preview health and authenticated fallback/source labels. No orders are enabled.
4. On the first reviewed pre-market session, the scheduler initializes the new table/index and publishes the daily report. Then confirm cockpit source=PERSISTED_DAILY_RESEARCH_UNIVERSE and the expected target date.
5. If refresh fails, inspect the error type and source/calendar gate. Do not mark the earlier snapshot as current to make the scan run.

The first production database publication is intentionally deferred to an eligible pre-market run. A Saturday deploy does not exercise that path. Direct external SQL access remains blocked by the existing database settings.

## Validation

CI uses an isolated PostgreSQL 18 service with dedicated test credentials, separate from Render. Tests cover publication/readback, idempotence, append-only corrections, hash corruption, evidence tampering, read-only dashboard fallback, pre-market retry, no late rebuild, stale/advance publication, weekends, missing archives, wrong dates, stale surveillance and the bounded calendar.

A review-branch-only CI smoke check downloads live public sources for the intended 2 November research snapshot and round-trips the result through a temporary SQLite store. It never connects to Render or uses a broker token. Approval at a later date requires refreshing the smoke target and calendar/evidence review. Production rollout is pending approval even if CI succeeds.
