# Intent traceability — Phase 1 test checkpoint

[RAN_TEST] Full-suite attempt timed out; no completed application-test counts. No row reaches TESTED from this attempt.
[READ_CODE] Historical evidence is preserved in Phase 0 log/PR16; current decision IDs use Mayur's seventeen-item register, superseding Phase 0 IDs.
[ASSUMED] No design was written at this checkpoint. Actual Render state: unverifiable by Codex; no DEPLOYED claims.
[READ_CODE] Existing implementation rows below are carried forward Phase 0 source observations, not new implementation or current test proof. Current session source re-read is limited to cloud_app.py::health/status and forward_paper_ledger.py::transition entry checks.

| Item | Status | Evidence path / named test | Evidence type | Last updated | Scope |
|---|---|---|---|---|---|
| PI-1 | NOT_STARTED | src/daily_universe_refresh.py::build_daily_universe; src/universe_scanner.py::run_universe_scan | READ_CODE | 2026-11-01 | Liquidity/band/restriction holds exist; same-day publication conflicts with day-before operational build. |
| PI-2 | NOT_STARTED | src/universe_scanner.py setup-window guard; src/run_universe_research.py::execute_cycle | READ_CODE | 2026-11-01 | Full eligible snapshot rows scanned; no separate user-selected pool verified; 09:45–11:30 differs from 09:15–14:35. |
| PI-3 | NOT_STARTED | src/static/cockpit.html inspected | ASSUMED | 2026-11-01 | Cockpit shortlist exists; phone-push delivery/heartbeat not verified. |
| PI-4 | NOT_STARTED | src/paper_choice_routes.py::ChoiceCommand; src/paper_choice.py::choose/catalog; tests/test_paper_choice.py::test_stale_or_closed_window_choice_cannot_be_saved (read only) | READ_CODE | 2026-11-01 | Single read-only choice, no entry/SL override fields, no symbol-specific TradingView link. |
| PI-5 | NOT_STARTED | src/paper_choice.py::workspace; src/paper_trade_management.py::manage_bar | READ_CODE | 2026-11-01 | Selection held; inactive library exists. PR15 controller is proposed per docs/API metadata, not read as implementation evidence this session. |
| PI-6 | NOT_STARTED | src/paper_engine.py::sell journal append | READ_CODE | 2026-11-01 | Replay costs/P&L journal exists; inspected replay journal has no MFE/MAE fields; complete persistent journal unverified. |
| PI-7 | NOT_STARTED | Targeted main-branch search: manual_catalyst returned no hits | ASSUMED | 2026-11-01 | Persistent catalyst memberships, suspension/revalidation and separate journal not verified. |
| HC-PREVIEW | IMPLEMENTED | src/cloud_app.py::health/status; src/paper_choice.py::workspace | READ_CODE | 2026-11-01 | PREVIEW_ONLY / execution false in inspected source; actual Render settings unverifiable by Codex this session. |
| HC-NO-REAL-ORDERS | IMPLEMENTED | src/cloud_app.py; src/paper_choice_routes.py | READ_CODE | 2026-11-01 | Inspected endpoints are preview/data/choice; no runtime files changed; no whole-repo absence claim. |
| HC-NO-SECRETS | NOT_STARTED | This session docs-only scan; see AUDIT_PACKET.md | ASSUMED | 2026-11-01 | Diff scan is limited evidence; full repository secret absence unverified. |
| HC-NO-DEPLOY | IMPLEMENTED | This PR changes docs/audit/* only | READ_CODE | 2026-11-01 | No Render operations or deployments performed this session. |
| HC-LONG-ONLY | IMPLEMENTED | src/forward_paper_ledger.py::transition; tests/test_forward_paper_ledger.py::test_invalid_entry_fails_without_creating_account (read only) | READ_CODE | 2026-11-01 | Positive quantity, stop below limit, BUY entry. Tests not run this session. |
| HC-RISK-9800 | IMPLEMENTED | src/forward_paper_ledger.py::transition; tests/test_forward_paper_ledger.py::test_exact_inclusive_risk_cap_and_separate_no_leverage_gate (read only) | READ_CODE | 2026-11-01 | Hard ledger cap includes fee_budget. Tests not run this session. |
| HC-ONE-FILL | IMPLEMENTED | src/forward_paper_ledger.py::transition/apply; tests/test_forward_paper_ledger.py::test_flat_account_still_remembers_filled_daily_entry (read only) | READ_CODE | 2026-11-01 | Per-account daily entry state plus DB advisory serialization; no standalone unique daily-fill constraint; tests not run. |
| HC-NO-LEVERAGE | IMPLEMENTED | src/forward_paper_ledger.py::transition; tests/test_forward_paper_ledger.py::test_exact_inclusive_risk_cap_and_separate_no_leverage_gate (read only) | READ_CODE | 2026-11-01 | Entry notional plus budget checked against cash; tests not run. |
| HC-NO-CRON-CHANGE | IMPLEMENTED | docs-only checkpoint diff; no Render/config operations | READ_CODE | 2026-11-01 | Session scope only |
| HC-LEGACY-ENTRYPOINTS-UNTOUCHED | IMPLEMENTED | docs-only checkpoint diff; src/run_daily.py and root render.yaml unchanged | READ_CODE | 2026-11-01 | Complete reference inventory deferred |
| D-001 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-002 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-003 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-004 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-005 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-006 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-007 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-008 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-009 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-010 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-011 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-012 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-013 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-014 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-015 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-016 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |
| D-017 | NOT_STARTED | docs/audit/DECISIONS.md current register; docs/design pending | ASSUMED | 2026-11-01 | Approved requirement; neither design nor implementation completed this checkpoint |

[ASSUMED] No hard invariant is certified by a completed current test run. The five-arm cap remains a required future feature, not a passing invariant.
