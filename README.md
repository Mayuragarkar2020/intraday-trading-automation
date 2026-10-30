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
