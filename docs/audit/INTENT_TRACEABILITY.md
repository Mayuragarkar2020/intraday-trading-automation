# Intent traceability — Phase 1 design proposal

[READ_CODE] Updated2026-11-01; source main 79a2d3086c8aea660dc31068e2758db1f7332808; proposed docs on codex/phase1-design.
[ASSUMED] **Local baseline UNKNOWN** (separate clone failed; no segmented local tests). Phase2 not started and requires design approval plus exact-source reproducible baseline. Actual Render state **unverifiable by Codex**.
[READ_CODE: CI-reported] Current-main test-phase-1 run41290657216 SUCCESS,539 passed and both browser checks. This is not RAN_TEST and does not promote future design to TESTED.
[READ_CODE] DESIGNED means a reviewable proposal exists, not approved/implemented. No new application implementation or current local application-test evidence.
| Item | Status | Evidence path / test | Evidence type | Last updated | Limits |
|---|---|---|---|---|---|
| PI-1 | DESIGNED | docs/design/SETUP_AND_UNIVERSE.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| PI-2 | DESIGNED | docs/design/SETUP_AND_UNIVERSE.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| PI-3 | DESIGNED | docs/design/JOURNAL_ALERTS_RECOVERY.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| PI-4 | DESIGNED | docs/design/LIFECYCLE_AND_ATOMICITY.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| PI-5 | DESIGNED | docs/design/TIME_AND_EXECUTION.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| PI-6 | DESIGNED | docs/design/JOURNAL_ALERTS_RECOVERY.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| PI-7 | DESIGNED | docs/design/SETUP_AND_UNIVERSE.md | READ_CODE | 2026-11-01 | Proposed; source/session/performance evidence incomplete |
| D-001 | DESIGNED | docs/design/LIFECYCLE_AND_ATOMICITY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-002 | DESIGNED | docs/design/LIFECYCLE_AND_ATOMICITY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-003 | DESIGNED | docs/design/LIFECYCLE_AND_ATOMICITY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-004 | DESIGNED | docs/design/TIME_AND_EXECUTION.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-005 | DESIGNED | docs/design/TIME_AND_EXECUTION.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-006 | DESIGNED | docs/design/TIME_AND_EXECUTION.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-007 | DESIGNED | docs/design/TIME_AND_EXECUTION.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-008 | DESIGNED | docs/design/SETUP_AND_UNIVERSE.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-009 | DESIGNED | docs/design/SETUP_AND_UNIVERSE.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-010 | DESIGNED | docs/design/JOURNAL_ALERTS_RECOVERY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-011 | DESIGNED | docs/design/TIME_AND_EXECUTION.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-012 | DESIGNED | docs/design/TIME_AND_EXECUTION.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-013 | DESIGNED | docs/design/JOURNAL_ALERTS_RECOVERY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-014 | DESIGNED | docs/design/JOURNAL_ALERTS_RECOVERY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-015 | DESIGNED | docs/design/JOURNAL_ALERTS_RECOVERY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-016 | DESIGNED | docs/design/SETUP_AND_UNIVERSE.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| D-017 | DESIGNED | docs/design/LIFECYCLE_AND_ATOMICITY.md; docs/audit/DECISIONS.md | READ_CODE | 2026-11-01 | Mayur-approved intent; engineering details proposed, not implemented/tested |
| HC-PREVIEW | IMPLEMENTED | src/cloud_app.py::health/status; docs-only diff | READ_CODE | 2026-11-01 | Existing source mode only; not current runtime proof |
| HC-NO-REAL-ORDERS | IMPLEMENTED | docs-only diff; docs/design/README.md | READ_CODE | 2026-11-01 | No order path touched; no whole-repo absence claim |
| HC-NO-SECRETS | NOT_STARTED | proposed diff secret-pattern scan in AUDIT_PACKET | RAN_TEST | 2026-11-01 | Diff scan only; whole-repo secret absence unverified |
| HC-NO-DEPLOY | IMPLEMENTED | docs-only PR diff; no Render operation | READ_CODE | 2026-11-01 | Session scope, no deployment proof |
| HC-NO-CRON-CHANGE | IMPLEMENTED | docs-only PR diff | READ_CODE | 2026-11-01 | No cron/workflow/config edit |
| HC-LEGACY-ENTRYPOINTS-UNTOUCHED | IMPLEMENTED | docs/design/BASELINE_AND_REFERENCES.md inventory; docs-only diff | READ_CODE | 2026-11-01 | src/run_daily.py/root render.yaml unchanged |
| HC-LONG-ONLY | IMPLEMENTED | src/risk_engine.py::size_long; ledger positive BUY guard; existing tests/test_risk_engine.py | READ_CODE | 2026-11-01 | Existing implementation; not locally RAN_TEST |
| HC-RISK-9800 | IMPLEMENTED | src/risk_engine.py; existing ledger cap; tests/test_forward_paper_ledger.py::test_exact_inclusive_risk_cap_and_separate_no_leverage_gate | READ_CODE | 2026-11-01 | Named test not run locally this session; future cost model proposal |
| HC-ONE-FILL | IMPLEMENTED | existing ledger used_entry_dates; docs/design/LIFECYCLE_AND_ATOMICITY.md | READ_CODE | 2026-11-01 | Existing application guard; proposed SQL unique event constraint not implemented |
| HC-NO-LEVERAGE | IMPLEMENTED | src/risk_engine.py; existing ledger cash guard | READ_CODE | 2026-11-01 | Existing implementation; no local test proof |
| HC-FIVE-ARM | DESIGNED | docs/design/LIFECYCLE_AND_ATOMICITY.md proposed CHECK1..5/unique slots | READ_CODE | 2026-11-01 | Feature NOT IMPLEMENTED; no cap/race test passed |
