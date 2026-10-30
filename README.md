# Intraday Trading Automation

Private NSE EQ T-1 liquidity-universe project. **Scaffold only; no live screening or order placement.**

## Locked trading constraints
- Capital: INR 980,000; maximum planned risk INR 9,800 inclusive of estimated trading costs
- Long-only; at most one trade per trading day; manual execution via DhanHQ
- All eligible NSE EQ stocks, initially priced INR 300 to 5,000
- Liquidity thresholds are configurable hypotheses, not validated optimal settings

## Current implementation
- `config/universe.yaml`: starting screening thresholds and failure policies
- `src/run_daily.py`: deliberately exits with status 2 / `NOT_READY` until real ingestion, mapping, restrictions and quality checks are implemented
- `tests/test_fail_closed.py`: safeguards this behavior
- `render.yaml`: proposed weekday 13:00 UTC (18:30 IST) cron service; do **not deploy as production** until ingestion is working

## Next milestones
1. Implement official NSE source acquisition, schema and freshness validation, and Dhan instrument reconciliation.
2. Implement rolling 20-session rupee turnover, volume metrics and effective-dated restrictions.
3. Backtest and verify T-1 decisions; preserve source hashes and configuration versions.
4. Add PostgreSQL persistence and only then activate scheduled Render execution.

No credentials or live trading secrets belong in GitHub.

## Ingestion milestone (not production-ready)

`src/ingestion.py` parses manually downloaded NSE CM UDiFF CSV or single-CSV ZIP files with strict column and date checks. `src/screening.py` calculates provisional 20-session liquidity metrics. Run `python -m scripts.inspect_nse YYYY-MM-DD path/to/report.csv` to inspect a local file. These are unverified against a live official sample; full target-date screening requires 20 actual NSE exchange sessions, verified security master, effective restrictions, and Dhan mapping. Unit tests have been committed but have not been executed by GitHub CI. The Render entrypoint remains intentionally `NOT_READY`.

## Eligibility integration milestone

`src/eligibility.py` implements a **manual-reviewed transitional** eligibility gate and conservative Dhan ISIN mapping. Actual NSE security/price-band/surveillance reports are **not yet ingested automatically**, and the Dhan master header assumptions require verification on a real downloaded file. Reviewed YES is explicitly `ELIGIBLE_MANUALLY_REVIEWED`, not production-cleared. The Render entrypoint still fails closed and no automatic universe is published.

## Historical NSE downloader (implemented, CI validated with fixtures)

Run `python -m scripts.download_20_sessions --dates-file session_dates.txt --output-dir data/raw/nse` with exactly 20 verified NSE trading session dates, ascending. Archives are checked using the NSE UDiFF parser and source hashes are saved. A complete live 20-session download and independent NSE trading-calendar validation have not yet been performed. Synthetic CI tests are not evidence of successful live historical screening. Production Render remains inactive.
