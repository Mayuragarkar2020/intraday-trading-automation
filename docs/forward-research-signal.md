# Receipt-bound research signal journal - inactive source work

31 October 2026. Source in src/forward_research_signal.py; not deployed or
connected to the research cron, web app, uploaded diagnostics or ledger.

The existing historical scanner persists research rows without a durable
receipt/source/universe binding. Such rows cannot be treated as live signals.
This separate library reads a committed recorder observation and its original
universe revision directly from the shared research database. It computes the
scanner result from that observation's exact current candles and preserves
the full normalized candidate inputs with immutable hashes and timestamps.

## Integrity checks

- Fixed RELIANCE/2885; fresh complete observation; source hash and each stored
  candle identity match. First-seen timestamps cannot be in the future.
- Reconnect batches with late first-seen candles are held. The latest three
  setup candles must each have been first observed within 90 seconds of close.
- Universe payload/evidence hashes and index dates match; same-day publication
  predates observation; research input gate and exact reviewed calendar pass.
- Exactly twenty prior sessions, each matching the current 72-bar research
  assumption, correct dates/opening/alignment and finite valid OHLC. Historical
  normalized prices remain supplied research inputs, not independently verified
  broker-source evidence. At most 2 MB of reference inputs are accepted.
- Five-minute current candles cannot be supplied by the caller. Higher-timeframe
  aggregates and EMA warmup inputs are derived inside the module. Scanner output
  cannot be supplied by the caller. A post-computation clock defines known_at;
  it must be aware and within 90 seconds of both receipt and latest close.
- Full inputs, result and receipt/source/reference hashes are journaled together.
  PostgreSQL advisory locks or SQLite immediate transactions serialize writers.
  One immutable signal record per symbol/close prevents recomputation using
  revised reference prices. Retries return the original known_at/result.

## Scope and remaining gates

Every result has execution_enabled=false, forward_paper_ready=false,
reference_prices_verified=false and session_contract_verified=false. Even an
ARMED result is research evidence, not order eligibility. No order adapter or
runtime integration exists. A caller may fetch a prior record on retry; it
must never turn an old journal result into a newly actionable trade event.

Before execution: establish dated, independently verified session/timestamp
and reference-price contracts; preserve broker reference-price acquisition
evidence; define the trusted worker's actual receipt/clock boundary; bind
eligible signal IDs transactionally to orders; add simulator and recovery;
approve the resulting runtime release separately. This source work does not
authorize a policy change or make automatic paper trading complete.

Tests use explicitly synthetic committed database fixtures to check integrity;
they are not evidence that actual market observations have been captured.
The PostgreSQL fixture uses a unique temporary schema in the CI test database
to avoid colliding with the recorder's independent tests.

