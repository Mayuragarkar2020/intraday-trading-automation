# Exact existing setup, universe, pool and scaling

[READ_CODE] Source claims in this document refer to main 79a2d3086c8aea660dc31068e2758db1f7332808. They are code readings, not market validation. Proposed changes are separately labelled.

## As implemented: auditable setup

| Component | Exact current behavior | Evidence |
|---|---|---|
| [READ_CODE] Session bars | Ordered contiguous same-session 5m CLOSE times; open 09:15; generic close helper permits through 15:30; initial candle close must be 09:20 | src/candle_session.py; qualified_scanner.py::qualify |
| [READ_CODE] Range | Last three completed current-session candles by default; configurable minimum cannot be below three; range does not span sessions | setup_detector.py::detect_setup |
| [READ_CODE] 5m EMA | SMA seed from first period closes; alpha=2/(period+1); recursive EMA thereafter; full Decimal calculation | candle_pipeline.py::ema |
| [READ_CODE] Warm-up | >=20 prior closes required; universe candidate uses last 200 historical 5m closes plus current-session closes | qualified_scanner.py; universe_scanner.py::candidate_from |
| [READ_CODE] Alignment | EACH of last three bars EMA10>EMA20, close>EMA10, close>EMA20, close>its session VWAP | setup_detector.py |
| [READ_CODE] VWAP | Sum(((H+L+C)/3)*volume)/sum(volume) over complete current session from first 09:20 close; rejects zero total volume | session_vwap.py |
| [READ_CODE] Relative volume | Latest range bar volume divided by mean of matching HH:MM slot from twenty distinct prior sessions; every slot volume>0; threshold >=1.2 | qualified_scanner.py::baseline_for_slot; setup_detector.py |
| [READ_CODE] Higher timeframe | Aggregate exactly three consecutive 5m bars into completed 15m bar; >=21 completed 15m closes; EMA10>EMA20 AND each strictly rising versus its preceding EMA value | dhan_research_scanner.py::aggregate_15m; qualified_scanner.py::higher_tf_confirmed |
| [READ_CODE] HTF timeliness | Latest 15m close cannot be future or >15m behind latest 5m; prior history precedes current session; same latest HTF boolean supplied to all three range bars | qualified_scanner.py::qualify |
| [READ_CODE] Range width | (max(high)-min(low))/latest.close <=0.025 | setup_detector.py |
| [READ_CODE] Proposal prices | Trigger=max(high)+0.05; SL=min(low)-0.05; reject nonpositive SL. This fixed buffer is not instrument-tick-aware | setup_detector.py |
| [READ_CODE] Breakout | Later bar low<=initialSL invalidates FIRST; otherwise high>=trigger means breakout, independent of close>trigger | setup_detector.py::confirm_breakout |
| [READ_CODE] Orchestration | Scan window 09:45–11:30; reference warm-up 08:30–09:40; history accepts 72/75-bar sessions; reference dates must match calendar | universe_scanner.py |
| [READ_CODE] Source gates | Present research paths are not execution certification. Indicators and closed-bar normalization do not prove source timestamp convention/session validity | research_input_gate.py; handoff |

[ASSUMED: proposal] Preserve these rules across the new scan window, but rename detector output SETUP_QUALIFIED/DETECTED: its legacy ARMED label is not a user arm. Only a confirmed choice may produce ARMED in the new lifecycle.
[ASSUMED: proposal] Preserve the 0.05 *strategy range buffer* in rule version until explicitly changed; require resulting proposed/override prices to be valid on the instrument tick grid. The separate stop-limit tolerance is not a replacement for this buffer. Unknown/incompatible ticks hold rather than silently change the strategy.
[ASSUMED: proposal] At 09:15 there is no current completed range; first possible detection is 09:30 (three bars), provided twenty matching prior slots and completed 15m confirmation exist. Prior-day HTF alone fails freshness before first completed current 15m bar. Do not fabricate an earlier signal to satisfy a scheduler window.
[ASSUMED: proposal] Early/late changes must test opening three-bar cases, exact slot-volume coverage through 14:35, intraday HTF aggregation and reference session shapes. The old window guard and warm-up timing need redesign, not just a wider string range. Afternoon results remain UNVALIDATED; bucket every detection, selection and fill.

## Hybrid universe and pool

[READ_CODE] config/universe.yaml and screening.py use: EQ series, close INR300–5000, twenty completed sessions; 20D mean turnover>=100Cr; median>=50Cr; latest>=75Cr; latest/mean>=0.75; minimum last-five-session turnover>=30Cr; all twenty volumes>0. Unknown schema/missing files fail run. Restrictions exclude 2%/5%, ASM/GSM, unknown restriction/mapping holds.
[READ_CODE] Current universe runner publishes same-day, checks same-day publication and scans eligible snapshot candidates; it does not implement the hybrid/final pool contract.
[ASSUMED: proposal] D-008 stages: after T-1 official reports are actually available, build provisional target-T list from twenty COMPLETED exchange sessions through T-1, official cash-market data/bands/security/status sources plus Dhan identity/reference feed. Proposed evening attempt 18:30 IST; missing reports mean PROVISIONAL_INCOMPLETE, not synthetic prices. Store publication effective date, retrieval time, originals/hashes and provisional revision.
[ASSUMED: proposal] 08:30–09:10 T: revalidate effective band/restrictions/security/series/Dhan mapping/tick sources, complete reference cache/EMA/RVOL/ADV, create immutable FINAL_VALIDATED revision by 09:15. Pre-open real-time five-minute candles are not available; use prior completed history for warm-up. Current-session VWAP begins only with current-session bars.
[ASSUMED: proposal] If a required date/status is unknown or whole-source retrieval fails, no new scanning/arming/entries; show UNIVERSE_FINAL_NOT_READY plus failed source. For verified per-stock exclusions, publish final with explicit exclusion/suspension reasons. Do not reuse provisional/stale final. A late final is research-only for that day under this conservative proposal; any broader late-start behavior needs reviewed config.
[ASSUMED: proposal] Runtime reference revision is pinned per setup. New restrictions after final immediately hold/cancel unfilled attempts; an existing position retains its manager/feed and exit authority. Eligibility hold must not disable protective exits.
[ASSUMED: proposal] Proposed systematic pool: top100 final eligible names by 20D mean traded value; stable tie security ID; plus eligible manual-catalyst memberships up to20, deduplicated. Persist pool membership/reason/rank/version, source provenance, exclusions and capacity truncation. No automatic pool churn intraday; active arms/positions retain feeds until terminal even if removed from a future pool.
[ASSUMED: proposal] A pool capacity shortfall is explicit POOL_COVERAGE_INCOMPLETE; never represent missing stocks as no setups. No entry competition resolves on partial armed coverage. Pool size/freshness is subject to actual load evidence, not solely broker advertised ceilings.

## Persistent manual catalysts

[ASSUMED: approved user intent] D-016 membership persists until user removal; daily revalidation; failing stocks visibly SUSPENDED; reminder after thirty days; about twenty entries.
[ASSUMED: proposal] Hard membership cap=20 INCLUDING suspended names to prevent quota evasion. Fields: membership_id, identity, note, added_by/at, updated_at, last_confirmed_at, removed_at, last_revalidated_at, status, reason, next_reminder_at. Add/remove requests idempotent; never delete history.
[ASSUMED: proposal] New intraday additions join scanning only after complete current-day identity/band/restriction/tick/price/liquidity checks, twenty-slot/EMA/HTF warm-up and source contracts pass. Otherwise PENDING_VALIDATION or SUSPENDED with reason; not silently scanned. Removal cancels its unfilled manual arms; an open trade continues managed until exit.
[ASSUMED: proposal] Same liquidity minima apply; no news exception for 2%/5%/unknown/restricted/thin stocks. Thirty-day reminder is once per thirty days since explicit review, not daily spam. Manual note can be revised with history.
[ASSUMED: proposal] If also systematic, fetch/scan once and record both provenance memberships; a manual-selected trade retains universe_source=manual_catalyst plus systematic_member=true for separate journal cohorts. No duplicate setup/arm/fill from dual membership.
[ASSUMED: proposal] Extra read-only feed/history requests share the broker budget; no extra subscription fee or entitlement is asserted. Show added instrument/request counts, warm-up cost and any service plan impact before later activation approval.

## Scaling: documented-only limits, not exercised

[ASSUMED: documented-only] Dhan docs retrieved 2026-11-01: https://dhanhq.co/docs/v2/ lists Data APIs 5 requests/second, 100,000/day; https://dhanhq.co/docs/v2/live-market-feed/ lists five connections/user, 5,000 instruments/connection and 100 instruments/subscription message. Actual entitlement, combined consumers, throughput and platform behavior were NOT exercised.
[READ_CODE] Current research loop is serial, spaces requests at least0.3 seconds and has a180-second cycle budget; caches references but does one current historical-data request per stock. Broker errors/auth/429 can halt remaining coverage.
[ASSUMED: calculation] Lower-bound warm-cache sweep=N/5 seconds; current spacing lower bound=0.3*N, excluding initial/final/processing overhead. With serial one-second response time, estimate >=N seconds. Cold cache roughly doubles request count; compute/network/Telegram/other consumers add overhead. These are arithmetic examples, not benchmarks.

| Pool N | 5 req/s ideal seconds | Current0.3s spacing lower bound | Serial1s response example | Fits300s candle? |
|---|---:|---:|---:|---|
| [ASSUMED]25 |5|7.5|25|Arithmetic yes; freshness not proved |
| [ASSUMED]50 |10|15|50|Arithmetic yes; freshness not proved |
| [ASSUMED]100|20|30|100|Arithmetic yes; exceeds90s freshness in example |
| [ASSUMED]200|40|60|200|Arithmetic yes; exceeds180s cycle budget and90s freshness |

[ASSUMED: proposal] A sweep fitting five minutes is insufficient: all armed evidence must be timely and quotes fresh. Use shared account-wide rate limiter, reserve management/clock priority and prevent research jobs starving active positions; no uncoordinated workers each assuming5/s.
[ASSUMED: proposal] Prefer warm historical references and five-minute REST pool scanning first, conditionally reduce pool until measured complete p95 sweep<=60s. For reliable fresh arm quotes/management, evaluate one shared WebSocket feed with aggregated five-minute bars and explicit gap detection; this is a future architecture option, not a deployed feature or approval to consume ticks.
[ASSUMED: proposal] Subscription size is count(unique(pool ∪ arms ∪ open-position instruments)), not pool+5 when arms are already members. Worst disjoint case N+5 plus a retained position and manual additions, bounded by deduped120-member pool proposal. Historical REST requests are not WebSocket instrument subscriptions. Reconnect/warm-up and missed ticks hold primary entries; never mix incomplete socket bars with historical bars silently.
