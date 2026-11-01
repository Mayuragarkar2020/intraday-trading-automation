# Progress log (append-only)

## 2026-11-01 — Phase 0 orientation / session 1

[READ_CODE] Baseline main: 79a2d3086c8aea660dc31068e2758db1f7332808. Audit branch: codex/phase0-intent-audit. Commit range: 79a2d3086c8aea660dc31068e2758db1f7332808..codex/phase0-intent-audit (resolve the PR head for an immutable endpoint).
[READ_CODE] Goal: compare the current repository with Mayur's latest intent and stop before Phase 1. Read PROJECT_HANDOFF.md first, then NEXT_WORK_PLAN.md, followed by targeted source/test paths; no repository-wide source dump.

### Bad news / conflicts first

[READ_CODE] NEXT_WORK_PLAN.md still says web PR9; the newer top checkpoint in PROJECT_HANDOFF.md says PR14. These are documentary claims, not fresh deployment evidence. Actual Render settings: unverifiable by Codex this session.
[READ_CODE] paper_choice.py persists one current SELECTED_HELD choice, not five armed setups; ChoiceCommand exposes no entry/SL override. Catalog/setup scanner use 09:45–11:30, not 09:15–14:35, and choice/ledger cutoff is 11:30, not 14:30.
[READ_CODE] paper_engine.py fills at slipped/tick-rounded max(bar.open, trigger); ReplayPlan has no limit-price field. It can chase a gap rather than cancel GAPPED_THROUGH. Replay journal inspected has no MFE/MAE columns. UI text still mentions a 15:15 flatten although ReplayRequest defaults to 15:00.
[READ_CODE] Full-universe path exists; RELIANCE-only is a fallback, not an accurate description of all scanner source. The current snapshot is published same-day despite historical input dates; no independently configured pool selector was found in inspected paths.
[READ_CODE] forward_paper_ledger serializes writers and persists an event journal/account projection, but daily entry uniqueness is a transition check in JSON, not a dedicated database unique daily-fill constraint. No five-arm schema was found in the inspected choice path.
[ASSUMED] A guarantee of flat exposure during a feed/DB outage, halt or circuit cannot be certified here. Detailed recovery/supervision and phone push need Phase 1; existing code keeps partial/unfilled exposure visible rather than proving closure.

### Work and evidence

[READ_CODE] Prepared the four mandatory audit files only; Phase 0's report-only rule was interpreted to allow the audit writes explicitly required in every phase. No implementation or design file was changed.
[READ_CODE] Seeded D-001 through D-015 from Mayur's stated decisions; all approved rows attribute approval to Mayur's current request. Codex archive/recovery suggestions remain proposed.
[READ_CODE] Existing tests inspected: tests/test_risk_engine.py::test_risk_includes_costs, test_cash_cap_lowers_quantity, test_prevent_second_trade, test_invalid_stops_and_costs; tests/test_forward_paper_ledger.py::test_exact_inclusive_risk_cap_and_separate_no_leverage_gate, test_flat_account_still_remembers_filled_daily_entry, test_postgres_concurrent_fills_and_restart; tests/test_paper_choice.py::test_concurrent_manual_choices_reserve_only_one_current_stock, test_stale_or_closed_window_choice_cannot_be_saved. None run this session.
[ASSUMED: external documentation, not code/runtime proof] Dhan official docs retrieved on 2026-11-01: https://dhanhq.co/docs/v2/live-market-feed/ documents five connections/user, 5,000 instruments/connection, 100/message; https://dhanhq.co/docs/v2/ documents Data APIs at 5 requests/second and 100,000/day. Account entitlement/use not tested. Unique pool+armed+position instruments share capacity; stocks already in the pool do not need duplicate subscriptions. Worst case on one connection with five disjoint armed stocks leaves 4,995 pool slots, before other subscriptions. This is capacity arithmetic, not a recommended operational pool size. Current scanner uses historical REST per instrument, not these WebSocket subscriptions; its 0.3-second spacing, cycle budget and latency determine practical coverage.
[READ_CODE] Existing chart affordance is generic https://tv.dhan.co/ plus copy-symbol; no symbol/5-minute TradingView URL in the inspected cockpit.
[ASSUMED: Codex proposal] Archive src/run_daily.py (NOT_READY exit 2) and root render.yaml (invokes it) together after checking external references; do not delete yet. Both untouched.

### Files changed

[READ_CODE] docs/audit/PROGRESS_LOG.md; docs/audit/DECISIONS.md; docs/audit/INTENT_TRACEABILITY.md; docs/audit/AUDIT_PACKET.md. All new: targeted GitHub reads returned 404 for these paths at the baseline.

### Tests and scans

[ASSUMED: not executed] Application tests: NOT RUN, report-only Phase 0. Exact application-test command: none. Pass/fail/skip counts: not applicable; no historical CI result promoted to current evidence.
[RAN_TEST] Documentation validation command: functions.exec JavaScript validator over auditDocs (exact validator recorded in this session's tool call). Assert four docs/audit Markdown paths and AUDIT_PACKET <=120 lines; scan all proposed contents for private-key markers, GitHub-style tokens, JWT-shaped values, bearer values, credential assignments and private/localhost URL patterns. Four files checked; zero pattern matches. This is a targeted diff scan, not full-repository secret assurance or an application test.
[READ_CODE] Read attempts for src/static/index.html and config/liquidity_policy.json returned 404; the actual cockpit path was identified and read. No conclusion was based on those missing paths. Existing audit paths also returned 404; no prior entries were overwritten.

### Not done / deviations / next checkpoint

[READ_CODE] No production deploy, Render operation, broker call, code/test/config edit, PR15 merge, Phase 1 design or Phase 2 implementation. No tests run; five-arm and current-intent race/gap contracts remain unproven.
[ASSUMED] Search absence (manual_catalyst returned no hits) is limited negative evidence; missing push/manual-catalyst implementation is not asserted as a whole-repository proof.
[ASSUMED] Docs-only audit writes are the sole exception to Phase 0 no-changes wording, because the same request mandates them every phase. If that interpretation deviates from intent, preserve this record and correct it by appending a CORRECTION entry.
[ASSUMED] Next checkpoint is the Phase 0 report. Stop for the user's continuation before writing docs/design/. Phase 2 still requires explicit Phase 1 approval. No questions reopen the decisions already made.
