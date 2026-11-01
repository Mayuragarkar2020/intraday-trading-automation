# Full-universe receipt evidence — proposed research-only release

1 November 2026. PR #9 was approved and deployed to the web only. The research
cron remains at PR #11. This proposal is separate and requires production approval.

## Problem and behavior

Existing full-pool research rows retain results/hashes but cannot prove which
setup candles were first seen on time. Opt-in UNIVERSE_RECEIPTS_ENABLED=true
records normalized current candles and first-seen times for each selected stock,
binds the immutable existing reference-cache hash, independently rebuilds 15m/EMA
inputs, scans, then freezes the input hash, output and post-scan known_at.
The post-scan timestamp precedes transaction commit; a future executor must sample
its actual decision clock after reading committed evidence, never infer an earlier
order from this field.

Two new tables, universe_receipt_candles and universe_receipt_signals, initialize
only on actual opt-in receipt processing. Candle identities include symbol,
security ID and close. Revised prices roll back an observation. Equivalent
Decimal spellings are not revisions. Retry/concurrent writers preserve one
receipt and its original known time; altered same-close inputs conflict. Reads
verify retained candle/first-seen/reference integrity. Injected 15m aggregates,
EMA warmup or historical prices cannot replace cached source inputs.

A first 09:45 fetch contains earlier candles as backfill. The last three setup
candles must each have been observed within 90 seconds of their close; initial
evidence therefore holds. With uninterrupted timely 09:45/09:50/09:55 observations,
the 09:55 record can become TIMELY_RESEARCH_EVIDENCE. Earlier indicator history
may be backfilled; it cannot generate earlier signals or fills. A gap/reconnect
again holds the affected three-candle setup window. This is research evidence,
not verified broker timestamp/session contracts or tradability.

All four source-clearance flags, forward_paper_ready and execution_enabled remain
false. A timely receipt never authorizes a paper entry. No ledger/account/order
adapter or simulated/live executor is activated. Source/market/session/reference
verification and actual full-pool throughput/coverage remain outstanding.

## Proposed activation boundary

After separate approval: merge the reviewed source and deploy the EXISTING
RESEARCH CRON ONLY, then enable UNIVERSE_RECEIPTS_ENABLED=true on that cron.
Keep UNIVERSE_SCAN_ENABLED=true, FORWARD_CAPTURE_ENABLED=true, existing schedule,
compute plan, commands and auto-deploy off. Do not deploy the web. No new service,
no broker order calls, no extra market-data requests. The journal adds source
reconstruction/scanner CPU work and PostgreSQL writes/retention.

Reviewed targets still end on 6 November. Do not extend the calendar blindly.
The recorder runs only through existing setup cycles; it is not a full-session
paper position feed. No receipt tables are created by the default disabled path,
by web deployment or by premarket reference warmup. Enabling midway does not
retrofit already saved scan cycles; recording begins on a later new cycle.

Local targeted validation: 69 passed, three PostgreSQL-only skipped. Full CI on the
current review head is required before release. Fixtures are not actual broker
coverage. PostgreSQL current size could not be queried: external access is
blocked. No allowlist/network change was made. Record actual row growth and
capacity once internal operational evidence is available; immutable evidence has
no deletion/retention job in this release.

Rollback: disable UNIVERSE_RECEIPTS_ENABLED and retain evidence. This is a proposal,
not an instruction to change settings without approval. No production change
for receipt recording has been made.
