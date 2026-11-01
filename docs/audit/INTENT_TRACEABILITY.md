# Intent traceability

[READ_CODE] Phase 0, baseline main 79a2d3086c8aea660dc31068e2758db1f7332808, 2026-11-01. IMPLEMENTED means the named narrow guard exists, not the complete product or deployment. NOT_STARTED refers to the full requested contract even where partial old behavior exists.
[ASSUMED] No row is TESTED or DEPLOYED: no application test was run this session; actual Render settings are unverifiable by Codex this session. Historical CI counts are not this session's evidence.

| Item | Status | Evidence (path + named test where inspected) | Evidence type | Last updated | Gap / scope |
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
| D-001 | NOT_STARTED | src/paper_choice.py; Phase 1 design pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-002 | NOT_STARTED | src/paper_choice.py (conflict); Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-003 | NOT_STARTED | Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-004 | NOT_STARTED | src/forward_paper_ledger.py (partial); Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-005 | NOT_STARTED | Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-006 | NOT_STARTED | src/paper_choice.py (single-choice restriction only) | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-007 | NOT_STARTED | src/paper_choice.py (advisory sort only); Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-008 | NOT_STARTED | src/forward_paper_ledger.py (11:30 conflict) | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-009 | NOT_STARTED | src/universe_scanner.py (11:30 conflict) | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-010 | NOT_STARTED | src/paper_engine.py (conflict); src/forward_paper_ledger.py (limit guard) | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-011 | NOT_STARTED | src/paper_engine.py (conflict); Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-012 | NOT_STARTED | src/paper_engine.py (conflict); Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-013 | NOT_STARTED | Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-014 | NOT_STARTED | Phase 1 pending | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
| D-015 | IMPLEMENTED | src/paper_models.py; src/paper_trade_management.py | READ_CODE | 2026-11-01 | Partial older implementation only where noted; full current contract not certified; no tests run. |
