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

## Hybrid universe:route-aware eligibility

[READ_CODE] Latest Mayur instruction supersedes older same-filter manual admission and25–50 systematic pilot. Canonical details:UNIVERSE_AND_POOL_CONTRACT.md. Automatic admission uses ALL ten agreed historical/series/price/band-status gates;manual CSV admission uses only verified exclusion of2%/5% bands,with identity resolution needed to establish the stock/band.
[READ_CODE] Manual IPO/news/earnings names bypass automatic price/20-session/daily-liquidity/volume/restriction screening gates at universe admission. Trade/setup/quote/tick/risk/tradability remain separate checks;manual source is not permission for a fabricated indicator/fill.
[READ_CODE] User manual additions areT-1 ONLY via CSV;no same-day entry. Preserve uploaded identifier/note visibly in universe,pool,selection,arms,alerts and journal. Existing memberships persist until removal;automated daily band revalidation is not a new user entry.
[ASSUMED] Hybrid provisional evening/final pre09:15 source validation remains;CSV target-date timing interpretation (previous calendar vs previous trading day) awaits Mayur. Unknown identity/band stored pending,not asserted valid. Each route needs a validated final publication;automatic-history failures are not silently imposed as manual20-day gates. Shared band/identity/feed failures still hold affected names;no reclassification without validT-1upload.

## Fixed scanning cohorts

[READ_CODE] Capacity75:top50automatic by20D mean traded value plus top25manual by available daily average traded value. For manual historyN1..19 use available completed sessions;20+use latest20 proposed window. Use fewer if fewer candidates;100manual=>top25ranked,not a25-upload cap.
[ASSUMED] Stable tie numeric security ID;overlaps scanned once whileboth provenance flags/user identifier retained;do not lend unused quota or invent members to force75unique. Quota is approved,these exact counting details proposed.
[ASSUMED] Pool membership independent of indicator readiness:chosen short-history IPO can be monitored each5m with SETUP_DATA_HOLD. Current20-slot RVOL/EMA/15m warm-up rules are NOT automatically changed by universe/ranking exception. N0averageundefined =>visible RANK_PENDING_ZERO_HISTORY;alternative listing-day policy needs Mayur.
[READ_CODE] Scanning09:15–14:35 persists;75capacity not measured throughput. Prior no-trade complete-sweep p95<=60s evidence requirement remains before operational confidence/further scale-up. No hidden quota reduction ifperformancefails;explicit capacity/entry hold.
[ASSUMED] Manual persistence has no old20-membership cap;25manualSCANNED names versus100uploaded entries are different quantities. See contract for CSV field/schema/idempotency proposals and future tests.

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

[ASSUMED] Budget counts unique(pool UNION arms UNION retained positions);up to75 selected-cohort slots before overlap,not old45–70. Historical REST and WebSocket subscription capacities are different;no new quota/throughput measurement this session.
