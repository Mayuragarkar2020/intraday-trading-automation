# PR #8 research recorder activation — 31 October 2026

Mayur explicitly approved the recorder-only merge/deploy, capture flag and
longer existing cron schedule in this chat. No approval covers PR #9 or
forward simulated orders, live orders, or a revised flatten policy.

## Exact deployed state

- PR #8 merged commit: 69a0c31ec3b4a8a492414b09b8422f774bc50a96.
- Research cron: crn-dbimqnbbc2fs73ap21vg; confirmed My Workspace
  tea-da6sf5qfngtc73c8jfi0; Singapore; existing 0.5c-512mb plan.
- Deploy dep-dbivtvnf3r2c73ej3l7g reached live at 14:45:48 UTC (20:15:48 IST).
- Schedule */5 3-10 * * 1-5 UTC; command python -m src.run_scheduled_research.
- FORWARD_CAPTURE_ENABLED=true was verified in the Dashboard; Dhan and DB
  variable keys remain present, with their secret values masked.
- Auto-deploy remains off. No new service or compute-plan change.
- Main tree was inspected before deploy: recorder files match the reviewed
  blobs; src/forward_paper_ledger.py is absent. Web was not redeployed.
- Updating the environment through MCP itself triggered an intermediate deploy
  of the then-current documentation checkpoint 87fbe74063656954fe2527a79a5cab2578ba2159
  (dep-dbivto4s728c738f9ibg). It was superseded by the intended merged recorder
  build above. Do not assume env updates are save-only even with auto-deploy off.

## Verification and limits

PR #8's handoff-only merge conflict was resolved by retaining current main's
handoff/plan. Source implementation was unchanged. Head
9bbe49d58ed5a0663acf63365e18f5e3739177ce passed 327 Python/API/PostgreSQL tests
and both Chromium suites in run 41211474796 before merge.

One manual smoke invocation, crn-dbimqnbbc2fs73ap21vg-1793458049, started at
14:47:30 UTC and finished successfully at 14:47:40 UTC. Runtime logged:

```json
{"status": "MARKET_CLOSED", "execution_enabled": false}
```

This proves the deployed cron starts and exits safely on Saturday. It does not
prove any live fetch, Monday universe publication, credential validity or
PostgreSQL capture persistence. The first reviewed session is 2 November;
calendar currently expires after 6 November. Observation and persistence must
be inspected during an actual eligible market session.

The read-only Render SQL connector could not reach PostgreSQL because its
external IP allowlist is empty. It was left closed. Do not claim SQL rows were
inspected; use a supported internal access path for later verification.

Rollback: disable capture flag and restore */5 3-6 * * 1-5; env updates can
redeploy, so inspect exact source first. Keep immutable observations.
Automatic forward paper trading remains NOT READY. PR #9 stays draft/inactive.
