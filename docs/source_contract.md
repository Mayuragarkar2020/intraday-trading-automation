# Phase 1 verification contract

Official source inventory: NSE CM UDiFF Common Bhavcopy Final; NSE security file; price band complete list and price band changes; surveillance reports; DhanHQ detailed instrument master.

https://www.nseindia.com/all-reports
https://www.nseindia.com/static/market-data/price-bands-surveillance-actions
https://dhanhq.co/docs/v2/instruments/

The availability of these reports does not establish their column schema or effective-date semantics. Before production, test each parser on an actual up-to-date official file, archive a source hash, and establish full-market completeness.

The restriction_inputs module accepts normalized reviewed controls only. Missing records HOLD; a blank surveillance record is not automatically an ALLOW. No live NSE restriction parsing is claimed.

The scheduled production entrypoint continues to exit NOT_READY and never places trades.
