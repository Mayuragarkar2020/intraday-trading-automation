# Setup and universe — authoritative C0 strategy, round 2

[READ_CODE] Approval update2026-11-01: Mayur answered “all yes” to the five round2 questions. Approved scope: C0 filter scope/prior3 width denominator; max(T-S)/T2.5%; one-tick default T/S buffers; stop-limit rather than plain-limit; proposed override bounds and conservative low<Q stop-no-fill rule with sensitivity. This is design approval of those choices, not implementation/test proof, buffer calibration or Phase2 authorization. Other proposals remain proposed.

[READ_CODE] As-implemented source below was reread at main79a2d3086c8aea660dc31068e2758db1f7332808. New strategy is Mayur's authoritative definition, NOT implemented by this docs-only revision.
[READ_CODE] Mayur has now approved the reviewed filter scope,maximum distance and one-tick defaults. This approval updates round2 review status only; no implementation or performance validation is implied.

## Side-by-side change map

| Topic | As implemented (READ_CODE) | Authoritative target / default (ASSUMED) | Required implementation change |
|---|---|---|---|
| Signal | Last3 bars qualify a range; no C0 close breakout comparison | C0.close>highest high of -1C/-2C/-3C, strictly; surface after C0 close | setup_detector.detect_setup:four-bar input, separate prior3 range and C0; equality false |
| Entry | Prior-range high+fixed0.05 | T0=high(C0)+one effective tick (default review defaults; approved scope stated above) | setup_detector:effective tick input; include C0 ID/high; no fixed buffer |
| SL | Last3 minimum low-fixed0.05 | S0=min(lowC0,low-1,low-2,low-3)-one effective tick (default review defaults; approved scope stated above) | setup_detector:four-low stop and tick validation |
| Trend/VWAP | All last3 bars EMA10>EMA20 and close>both/VWAP | Keep thresholds but apply to C0 only (review defaults; approved scope stated above) | qualified_scanner computes C0 indicator snapshot; detector checks C0 only |
| RVOL | Latest range bar volume/20 matching slots>=1.2 | C0 slot ratio>=1.2 (review defaults; approved scope stated above) | qualified_scanner binds matching slot to C0, not last pre-signal bar |
| HTF | Latest completed15m EMA10>EMA20, both rising | Same confirmation at C0 close (review defaults; approved scope stated above) | qualified_scanner:no future15m, no stale HTF; attach source IDs |
| Width | Last3 range width/latest range close<=2.5% | Width of -1C..-3C only<=2.5% (review defaults; approved scope stated above); denominator close(-1C) proposal | detector:exclude C0 from width high/low; document denominator/config |
| Required bars | >=3 current-session candles | >=4 contiguous current-session bars; prior3 cannot span sessions | qualified_scanner:four inputs, C0 explicit; earliest possible09:35 |
| Entry interpretation | Detector says ARMED before human choice; confirm_breakout uses later high | Detector says DETECTED/SURFACED; human confirmation creates resting arm; same trigger candle may fill | detector terminology; qualified_scanner result schema; universe_scanner persisted output |
| Lifetime | No explicit C0+15min contract in detector | Expire15min after C0 close; pre-entry low<=S invalidates | stable C0 expiry/invalidation IDs; no renewal by repeated scan |
| Scan window | universe_scanner09:45–11:30; warm-up until09:40 | Scan09:15–14:35, hidden post-cutoff; warm references/final universe before09:15 | universe_scanner window/publication/cache/freshness/visibility gates |
| Price/evidence fields | range-high/low trigger/stop and current receipt | C0 and prior3 IDs, T0/S0, tick source, expiry, filter/width snapshot | version candidate/receipt payload and hashes; do not reinterpret old stored receipts |
| Execution | Pure breakout helper not a resting bracket | Entry stop-limit plus protective stop-limit, AON, same candle, stop-failure recovery | detector output feeds future broker-neutral lifecycle; no broker call in these modules |

## Exact preserved calculations and proposed filter scope

[READ_CODE] EMA uses initial SMA seed, alpha2/(n+1), Decimal recurrence. Universe candidate uses last200 prior5m closes, minimum20; session VWAP=sum(((H+L+C)/3)*V)/sumV from09:20 opening close; positive total volume, ordered contiguous bars.
[READ_CODE] RVOL baseline uses20 distinct prior sessions, matching HH:MM slot with positive volume each. HTF uses21+completed15m closes, EMA10>EMA20 and both rising vs preceding values; latest15m no future and at most15min old. No rounding changes are implied.
[ASSUMED: review defaults; approved scope stated above] Apply trend/VWAP/RVOL checks to C0; prior3 define only breakout reference/width. Width=(maxHighPrior3-minLowPrior3)/close(-1C). Retain2.5%, RVOL1.2 and HTF direction until reviewed; these choices were explicitly approved by Mayur's five answers, not by retention of old defaults.
[ASSUMED] Same-session first four bars: -3 closes09:20,-2 closes09:25,-1 closes09:30,C0 closes09:35. Scanner active09:15 does not mean a valid C0 exists then. Warm EMA/20-slot/HTF beforehand; C0 cannot use unfinished15m bars. Original09:45–11:30 and afternoon windows remain separate cohorts; afternoon strategy efficacy UNVALIDATED.
[ASSUMED: review defaults; approved scope stated above] Maximum distance(T-S)/T<=2.5% and bounded overrides are in TIME_AND_EXECUTION. This is a guard proposal, not replay-selected optimum.
[ASSUMED] All old-rule replay/scanner outcomes are NON_EVIDENCE_FOR_C0_V2: missing C0 confirmation, four-bar stop/tick fields and resting bracket semantics. Preserve them unchanged with original rule IDs; do not relabel as new strategy, even if selected stocks overlap.

## Hybrid universe and pool

[READ_CODE] config/universe.yaml and screening.py use: EQ series, close INR300–5000, twenty completed sessions; 20D mean turnover>=100Cr; median>=50Cr; latest>=75Cr; latest/mean>=0.75; minimum last-five-session turnover>=30Cr; all twenty volumes>0. Unknown schema/missing files fail run. Restrictions exclude 2%/5%, ASM/GSM, unknown restriction/mapping holds.
[READ_CODE] Current universe runner publishes same-day, checks same-day publication and scans eligible snapshot candidates; it does not implement the hybrid/final pool contract.
[ASSUMED: proposal] D-008 stages: after T-1 official reports are actually available, build provisional target-T list from twenty COMPLETED exchange sessions through T-1, official cash-market data/bands/security/status sources plus Dhan identity/reference feed. Proposed evening attempt 18:30 IST; missing reports mean PROVISIONAL_INCOMPLETE, not synthetic prices. Store publication effective date, retrieval time, originals/hashes and provisional revision.
[ASSUMED: proposal] 08:30–09:10 T: revalidate effective band/restrictions/security/series/Dhan mapping/tick sources, complete reference cache/EMA/RVOL/ADV, create immutable FINAL_VALIDATED revision by 09:15. Pre-open real-time five-minute candles are not available; use prior completed history for warm-up. Current-session VWAP begins only with current-session bars.
[ASSUMED: proposal] If a required date/status is unknown or whole-source retrieval fails, no new scanning/arming/entries; show UNIVERSE_FINAL_NOT_READY plus failed source. For verified per-stock exclusions, publish final with explicit exclusion/suspension reasons. Do not reuse provisional/stale final. A late final is research-only for that day under this conservative proposal; any broader late-start behavior needs reviewed config.
[ASSUMED: proposal] Runtime reference revision is pinned per setup. New restrictions after final immediately hold/cancel unfilled attempts; an existing position retains its manager/feed and exit authority. Eligibility hold must not disable protective exits.
[ASSUMED: proposal] Initial systematic pool:25 names by default, operational range25–50 final eligible names by 20D mean traded value; stable tie security ID; plus eligible manual-catalyst memberships up to20, deduplicated. Persist pool membership/reason/rank/version, source provenance, exclusions and capacity truncation. No automatic pool churn intraday; active arms/positions retain feeds until terminal even if removed from a future pool.
[ASSUMED: proposal] A pool capacity shortfall is explicit POOL_COVERAGE_INCOMPLETE; never represent missing stocks as no setups. No entry competition resolves on partial armed coverage. Pool size/freshness is subject to actual load evidence, not solely broker advertised ceilings.

## Persistent manual catalysts

[ASSUMED: approved user intent] D-016 membership persists until user removal; daily revalidation; failing stocks visibly SUSPENDED; reminder after thirty days; about twenty entries.
[ASSUMED: proposal] Hard membership cap=20 INCLUDING suspended names to prevent quota evasion. Fields: membership_id, identity, note, added_by/at, updated_at, last_confirmed_at, removed_at, last_revalidated_at, status, reason, next_reminder_at. Add/remove requests idempotent; never delete history.
[ASSUMED: proposal] New intraday additions join scanning only after complete current-day identity/band/restriction/tick/price/liquidity checks, twenty-slot/EMA/HTF warm-up and source contracts pass. Otherwise PENDING_VALIDATION or SUSPENDED with reason; not silently scanned. Removal cancels its unfilled manual arms; an open trade continues managed until exit.
[ASSUMED: proposal] Same liquidity minima apply; no news exception for 2%/5%/unknown/restricted/thin stocks. Thirty-day reminder is once per thirty days since explicit review, not daily spam. Manual note can be revised with history.
[ASSUMED: proposal] If also systematic, fetch/scan once and record both provenance memberships; a manual-selected trade retains universe_source=manual_catalyst plus systematic_member=true for separate journal cohorts. No duplicate setup/arm/fill from dual membership.
[ASSUMED: proposal] Extra read-only feed/history requests share the broker budget; no extra subscription fee or entitlement is asserted. Show added instrument/request counts, warm-up cost and any service plan impact before later activation approval.

[ASSUMED: Mayur-approved amendment D-020] Scale above the initial25–50 systematic pool ONLY after no-trade observation establishes measured complete-sweep p95<=60seconds, including source latency, indicator/receipt persistence and all required armed/catalyst coverage. Incomplete/error intervals count as failures, not omitted fast samples. Proposed minimum observation:five full sessions and at least100 complete sweeps, stratified opening/original/midday/late; no real or primary-paper trades during measurement. More samples if p95 uncertainty crosses60s. This observation protocol is proposed; the60s gate is approved.

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
[ASSUMED: proposal] Subscription size is count(unique(pool ∪ arms ∪ open-position instruments)), not pool+5 when arms are already members. Worst disjoint case N+5 plus a retained position and manual additions, bounded by deduped initial45–70-member pool (25–50 systematic plus up to20 catalysts). Historical REST requests are not WebSocket instrument subscriptions. Reconnect/warm-up and missed ticks hold primary entries; never mix incomplete socket bars with historical bars silently.

