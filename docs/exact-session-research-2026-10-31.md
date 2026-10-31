# Exact-session research guard — 31 October 2026

## Problem and resulting behavior

The existing scheduled RELIANCE research chose the latest 20 complete Dhan sessions. If an expected recent session was missing or truncated, it could silently use an older complete session instead. It also did not bind its input to the dated universe snapshot.

The revised scheduler checks the committed universe before contacting Dhan or opening the scan store. The snapshot target date must equal today's IST date; the chosen symbol must have a unique matching Dhan ID and remain in the research pool. Excluded stocks and identity-conflict holds cannot enter this path. This grants research-input readiness only, never trading eligibility.

The pipeline now requires exactly 20 explicit dates. Every one must have a complete candle session. Missing/truncated dates return INCOMPLETE_REFERENCE_HISTORY; older sessions cannot replace them. Unexpected observed sessions within the reference interval also stop processing. Those failures do not initialize or write the scan store.

Successful research rows explicitly retain execution_enabled=false, timestamp_verified=false, session_classification_verified=false, eligibility_verified=false and chart_reconciled=false. reference_dates_matched=true means only that all supplied dates matched complete candle data.

## Frozen snapshot expiration

The currently committed snapshot targets **2 November 2026**. The revised scheduler will reject it on other dates with UNIVERSE_SNAPSHOT_DATE_MISMATCH. It will not silently extend the 103-name pool into subsequent sessions. Before a later scan, the universe and its references must be rebuilt for that session. Automatic daily universe refresh is not implemented in this change.

This expiration is deliberate. The change does not certify the calendar as complete or infer that weekdays necessarily traded. The 20 reference dates retain official bhavcopy source hashes and positive row counts.

## Closing-auction investigation

NSE's current published CAS page says continuous trading for non-CAS securities lasts until 15:30, while CAS starts at 15:15 for eligible securities. These correspond to 75 and 72 five-minute continuous-session candles respectively.

Official reference: https://www.nseindia.com/static/products-services/closing-auction-session

The dated NSE MII security master for 30 October was retrieved successfully. It contains ElgbltyClsgAuctnSsn. All 103 research candidates match the EQ symbol and ISIN uniquely: 85 have source value 1 and 18 have value 0. RELIANCE matches security ID 2885 with value 1.

[Observation and source hash](../research/2026-10-30/cas-master-observation.json) preserve these findings. These values are not inferred from the price-band labels.

The current CAS page references circular NSE/CMTR/73845 for the security-master format, but the direct PDF URL returned 404 during this investigation. The precise field-value contract has therefore not been independently read from that circular. No automated classification approval is claimed, and per-date historical classification has not been collected. The pipeline's existing 72-bar RELIANCE expectation remains a research assumption and is explicitly flagged unverified. Broadening the scanner requires resolving this gate rather than applying 72 to every stock.

## Scope and release

Only the existing RELIANCE research path is updated. The cockpit display and its 103-candidate count stay as currently deployed. No order code, service creation, database schema change, credential change or clock schedule change is included.

After approval, merge and manually deploy **intraday-session-research only**. The cockpit does not need redeployment for this change. Confirm the intended commit and check that weekend runs remain closed. On 2 November, confirm exact reference-date matching or the appropriate hold. On subsequent days, a stale committed universe must hold until a refreshed snapshot is supplied.

The new tests cover excluded/held symbols, Dhan ID mismatches, duplicate candidates, invalid source hashes, expired snapshots, missing/truncated reference sessions, older-session substitution and unexpected dates. No production changes have been made while preparing this branch.
