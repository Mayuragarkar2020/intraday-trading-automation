# Transitional eligibility checks

This is not automatic NSE surveillance verification. Before production, parse and reconcile NSE security file, effective-next-session price-band file, and surveillance indicators.

Dhan detailed master documented at https://dhanhq.co/docs/v2/instruments/ . The local parser requires EXCH_ID, SEGMENT, ISIN, SERIES and SECURITY_ID; confirm with a fresh actual file before use.

Manually reviewed CSV schema: isin,target_date,eligible,reason. Target-date-missing records are HOLD. A manual YES produces ELIGIBLE_MANUALLY_REVIEWED, never a production clearance.

The scheduled job is deliberately inactive / NOT_READY.
