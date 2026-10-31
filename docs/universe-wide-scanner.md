# Full-universe scanner - proposed research release

31 October 2026. Keep the workflow simple: daily liquid universe, completed
five-minute setup scans, then the separately developed paper trade manager.

## What this change does

- Reuses the existing daily universe and its liquidity thresholds. Excludes
  2%/5% bands, keeps unknown bands/identity issues held, and preserves existing
  surveillance exclusions. No Band remains distinct from a fixed 20% band.
- Scans every selected research candidate with the existing EMA10/EMA20,
  VWAP, relative-volume, completed 15-minute confirmation and consolidation
  setup detector. Entry/SL calculations and trading policy are unchanged.
- Fetches/validates twenty reference sessions once per universe revision and
  instrument, with a persistent immutable cache. Warms missing references
  between 08:30 and 09:40; each completed five-minute setup cycle needs only
  current-session prices for cached instruments. Warm-up does not create setups.
- Uses the existing pre-market publication before 09:15. After that time,
  missing same-day publication holds; no late universe rebuild is introduced.
- Scans during 09:45-11:30. Current candles must include the opening sequence
  and the common cycle close, received no more than 90 seconds after that
  close. Missing/stale/invalid indicator inputs hold that stock.
- Keeps explicit per-stock outcomes and coverage counts. One bad stock does
  not suppress other stocks; auth/429 failures stop further broker requests.
  An incomplete scan is never reported as full coverage. Snapshot retries
  return the original result; a later five-minute cycle can recover.
- Keeps each cycle bounded: 180-second request budget, plus an in-flight
  request/processing time. Requests are sequential with at least 0.3 seconds
  between starts. Slow initial warm-up can span pre-market cycles. This is not
  a throughput guarantee. Shared-credential consumers must be coordinated.
- Persists full-pool results separately. Authenticated /api/latest-scan serves
  them when present, including selected-stock holds and coverage. Otherwise
  it falls back to the existing RELIANCE snapshot. Warm-up snapshots are never
  displayed as setup scans. The cockpit shows complete/incomplete coverage.

The dated saved 109-candidate snapshot selects 103 research candidates, leaves
two identity holds and four exclusions. A software test sends all 103 through
the real detector using synthetic candle prices; this is not live coverage.

## Trade mechanics confirmed with Mayur

EMA10-close exits remain active before 1.5R as well as after it. The 1.5R
threshold additionally requests cost breakeven; it does not enable the EMA
exit for the first time. This preserves the existing trade-manager code.
No position sizing, entry, initial stop, exit timing or paper/live execution
policy is changed by this scanner release.

## Scope and limits

Every result is research-only; execution_enabled=false and forward_paper_ready=false.
Timestamp labels remain the existing open-label research assumption. Prior
sessions may have 72 or 75 contiguous bars, without certifying dated CAS
classification. Unknown/irregular shapes hold. No daily per-stock screenshot
task is introduced. Official session/reference verification remains necessary
before automatic paper or real execution, not a manual step for each scan.

Reviewed calendar currently covers 2-6 November only. No weekend or special
session is inferred. Source prices, costs, timeliness, rate-limit headroom and
full-pool performance need actual-session validation before execution use.
The read-only SQL connector cannot access the externally closed production
database; do not open it merely to inspect results. Use application status
and an approved internal access path for persistence verification.

## Proposed activation - separate approval required

Same existing web/cron/database; no new paid service or changed cron schedule.
Merge this reviewed release, deploy it to the existing web service and research
cron, and set UNIVERSE_SCAN_ENABLED=true on the cron only. Keep auto-deploy off
and retain FORWARD_CAPTURE_ENABLED=true. The existing RELIANCE recorder stays
separate; it does not become an all-symbol recorder or paper executor.

The flag is absent/disabled by default, preserving the current cron path. More
stocks mean more broker requests and billable runtime; no cost estimate or
market-throughput claim is made. Recorder and scanner share credentials with
any manual diagnostics; a 429 visibly holds coverage rather than retrying fast.

PR #9 ledger/signal source and PR #10 additional chart-comparison UI are not
included or approved by this release. No paper order or broker order is added.
Rollback: disable the new flag and deploy the intended reviewed revision;
inspect any env-update-triggered deploy. Retain stored evidence. The older
web build can be restored separately if required.

## Validation

Tests cover the real saved pool selection with synthetic prices, 72/75-bar
reference shapes, exact dates, gaps, bad OHLC/volume, stale/missing candles,
cache/restart/idempotency, narrow/unknown bands, duplicate mappings, request
spacing/budget, auth/429 holds, database failure, concurrent PostgreSQL commits,
pre-market warm-up, opt-in dispatch and authenticated cockpit coverage.
See the review PR for exact-head CI results. This release is not deployed.

Broker rate-limit reference checked: https://dhanhq.co/docs/v2/ (Data APIs).

