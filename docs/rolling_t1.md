# Rolling T-1 deployment gate

V1 research archive is fixed to 2026-09-25. A daily schedule must not turn on before all fixed report filenames are parameterized and the next trading session is confirmed using an official NSE calendar.

Session-policy helper rejects future, pre-close and weekend target dates; it does not by itself prove exchange holiday/settlement schedules. The next trading session must be provided by a verified calendar.

Required before activation:
1. Parameterize historical as-of dates and all effective-date NSE F&O, complete band, band change, and surveillance sources.
2. Verify that each report is valid for the intended target session.
3. Persist source hashes and complete instrument-level diagnostics.
4. Confirm all applicable restriction codes, including broker restrictions, with source documentation.
5. Run a complete T-1 acceptance test with real files and independent audit.
6. Enable Render only once all conditions pass.

No automated orders. Existing trading-automation service must stay untouched.
