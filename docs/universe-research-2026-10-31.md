# NSE universe research — verified download, 31 October 2026

This branch builds a dated research shortlist and displays it in the cockpit. It does not activate the daily production universe, enlarge the running RELIANCE scanner, alter database settings or enable orders.

## Live validation result

Twenty official NSE CM UDiFF ZIP archives, 1–30 October 2026, were downloaded and parsed successfully on 31 October. The explicitly listed dates omit weekends and the 2/20 October holidays in NSE capital-market circular CMTR71775. This is a reviewed research date list, not an implemented exchange-calendar service or proof that every subsequent calendar update has been captured.

| Stage | Count |
|---|---:|
| EQ records on 30 October | 2,703 |
| Full 20-session histories | 2,570 |
| Incomplete histories held out | 133 |
| Complete histories failing liquidity/price rules | 2,461 |
| Liquidity candidates | 109 |
| Unique Dhan mappings among liquidity candidates | 109 |
| Current-reference research candidates | 106 |
| Approved for trading | 0 |

Thresholds remain the repository's hypotheses: price INR 300–5,000; 20-session average turnover >= INR 100 Cr; median >= 50 Cr; latest >= 75 Cr; latest/average >= 0.75; minimum turnover over latest five sessions >= 30 Cr; positive volume every session.

ESDS, LALITHAA and LIQUIDBEES show 5% in the downloaded price-band reference. They are excluded from the 106-name reference research pool. LIQUIDBEES is also absent from the NSE equity-share list. NSE EQ bhavcopy series alone is insufficient to identify ordinary shares.

The Dhan master has a unique NSE/E/EQ security ID for all 109 candidates. The 106 reference candidates also match NSE equity-list ISIN and symbol and have Dhan ASM_GSM_FLAG=N, category NA and buy/sell indicator A. This is broker reference evidence, not independent effective-dated NSE surveillance clearance. "No Band" is preserved as source text and never converted to 10% or 20%.

## Artifacts and provenance

- [Full dated snapshot](../research/2026-10-30/universe.json): source hashes, URLs, metrics, 109 liquidity candidates, review outcomes, and all 133 incomplete histories.
- [CSV](../research/2026-10-30/candidates.csv): all 109 rows, including the three exclusions.
- [Explicit sessions](../research/2026-10-30/sessions.txt).
- Intended research target: 2 November 2026. This does not verify target-date eligibility or declare the pool live.
- Downloaded archives were processed in temporary directories. Raw archives and credentials were not committed.

Official references:
- https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf
- https://www.nseindia.com/static/market-data/securities-available-for-trading
- https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv
- https://www.nseindia.com/static/regulations/daily-price-bands-reports
- https://nsearchives.nseindia.com/content/equities/sec_list.csv
- https://dhanhq.co/docs/v2/instruments/
- https://images.dhan.co/api-data/api-scrip-master-detailed.csv

The current-reference CSVs do not contain an independently verified effective date. Each reference manifest explicitly retains effective_date_verified=false.

## Reproduce

Use a disposable CI workspace or a cloud development environment with requirements.txt installed. Download the 20 explicit dates using the existing downloader:

```sh
python -m scripts.download_20_sessions --dates-file research/2026-10-30/sessions.txt --output-dir data/raw/nse --manifest output/nse_source_manifest.json
curl --fail --location https://images.dhan.co/api-data/api-scrip-master-detailed.csv --output data/raw/dhan.csv
curl --fail --location https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv --output data/raw/equity.csv
curl --fail --location https://nsearchives.nseindia.com/content/equities/sec_list.csv --output data/raw/bands.csv
python -m scripts.build_universe_research --dates-file research/2026-10-30/sessions.txt --raw-dir data/raw/nse --target-date 2026-11-02 --dhan-master data/raw/dhan.csv --equity-master data/raw/equity.csv --price-bands data/raw/bands.csv --output output/universe_research.json
python -m pytest -q
```

The CLI accepts explicit dates and does not invent missing sessions. It validates every file's actual trade date and hash. Missing/wrong-date sources fail the run; incomplete individual histories are counted and held out. Output replaces an existing report only after successful processing. A failed run leaves an earlier output file untouched; consumers must always inspect its embedded asof_date and target_date before use.

Current-reference filtering requires all three reference inputs together. Changed future reference files can change the observed reference pool. They must not be used as historical backtest eligibility. Historical source ZIP hashes allow comparison against the saved snapshot.

## Cockpit behavior and approval boundary

GET /api/universe-research requires the existing cockpit token. It reads the committed dated JSON; it does not contact the broker or database, trigger research or submit orders. The table shows as-of/target dates, all 109 candidates and each exclusion/hold. The approved tradable count remains zero.

To release: merge the reviewed branch, then manually deploy only intraday-cockpit-preview, whose automatic deploys are disabled. Verify /health, authenticated access, the 109/106 counts and disabled execution after deploy. No new service or database change is needed.

Remaining work before trading eligibility: effective-dated NSE security/band/surveillance checks; complete exchange-calendar validation including exceptional sessions; corporate-action handling; Dhan candle timestamps, continuous-session eligibility and chart reconciliation. The existing scheduled scanner remains RELIANCE-only.

## Validation

The builder and reference tests passed locally in a disposable runtime (19 tests). The cockpit JavaScript parsed successfully. GitHub Actions runs the entire repository suite on the pull request; the final review should use its latest commit result.
