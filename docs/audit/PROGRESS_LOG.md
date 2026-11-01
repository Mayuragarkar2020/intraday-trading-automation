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


## 2026-11-01 — Phase 1 / session 2 / initial full-suite checkpoint (BLOCKED)

[RAN_TEST] BAD NEWS FIRST: the full-suite attempt timed out after 180 seconds with only two progress dots and no pytest summary. Completed pass/fail/skip counts are UNKNOWN, not zero and not passing. The wrapper terminated the subprocess; pytest produced no terminal summary. No second full-suite run was made.
[RAN_TEST] Exact test command, working directory repo: `python -m pytest -q --basetemp=.test-phase1-baseline-20261101`. Invocation used Python subprocess.run with stdout/stderr combined into phase1-baseline-pytest.log and timeout=180. Wrapper shell command was a PowerShell here-string piped to python. Result: subprocess.TimeoutExpired; pytest exit code unavailable; wrapper exit code 0 reflects reporting only, NOT test success.
[READ_CODE] The local log contains only `..`; no failing assertion or failing test name can be attributed. The stuck test was not identified. Local run is not proof for main or the PR15 head.
[RAN_TEST] Git-blob SHA inventory comparison against PR15 commit 9ec22efae49a633c6f8cba09f78ac41b204de739 found a mixed local workspace: source/test mismatches include src/dhan_chart_reconciliation.py, src/forward_research_signal.py, src/paper_entry_selection.py, src/static/cockpit.html, tests/test_forward_paper_ledger.py, tests/test_forward_research_signal.py, tests/test_paper_entry_selection.py, tests/test_run_universe_research.py, tests/test_universe_scan_api.py and tests/test_universe_scanner.py. Other tracked docs/config/workflow paths are missing locally. The comparison accepted raw or CRLF-normalized Git blob hashes. It did not modify application files.
[ASSUMED] Earlier sessions recorded Windows TestClient hangs; this session has not diagnosed whether the same cause produced this timeout. No such cause is asserted as verified.

### Goal, phase and commit range

[READ_CODE] Goal: begin Phase 1 design-only work, first run and record the full suite, then stop at checkpoints. Phase 0 accepted by Mayur. This session stopped at the initial test checkpoint before design because the run was incomplete and the local baseline was not clean.
[READ_CODE] Branch codex/phase1-test-checkpoint; parent 2cd3fd0e129d3b686c8211b91d06c201e192b779 from the Phase 0 audit branch (PR16), preserving all earlier audit entries. Commit range 2cd3fd0e129d3b686c8211b91d06c201e192b779..codex/phase1-test-checkpoint; resolve the PR head for the immutable endpoint. No main-branch write or merge.
[READ_CODE] Read docs/PROJECT_HANDOFF.md, docs/NEXT_WORK_PLAN.md and all four docs/audit files first. Audit files were absent on main and read from codex/phase0-intent-audit. Source claims limited to targeted current-main health/status and ledger-entry guard reads.
[READ_CODE] Actual Render state: unverifiable by Codex. No Render calls, production deployment, cron change or broker call occurred.

### What was done / files changed

[READ_CODE] Appended this log; updated docs/audit/DECISIONS.md with Mayur's D-001..017; updated docs/audit/INTENT_TRACEABILITY.md; regenerated docs/audit/AUDIT_PACKET.md. Only those four docs changed.
[READ_CODE] CORRECTION to Phase 0 numbering: Phase 0 assigned fifteen different D IDs before Mayur supplied the current seventeen-ID register. Historical identifiers in DECISIONS.md are explicitly renamed P0-D-001..015; historical decision text/provenance is retained and current D-001..017 comes from Mayur's latest request. This namespace correction is explicit; no Codex proposal was marked approved.
[ASSUMED] Historical archive proposal is superseded by Mayur's instruction to leave src/run_daily.py and root render.yaml untouched. Both remain untouched. No docs/design files were written.
[READ_CODE] A metadata manifest was saved as scratch phase1-manifest.json outside repo for the source comparison; a pytest log and basetemp were generated locally. None is part of this docs-only PR.

### Reference inventory / deferred work

[READ_CODE] Local tracked-file literal search found tests/test_fail_closed.py:1 importing src.run_daily. It cannot establish every repository reference because the workspace is incomplete.
[READ_CODE] GitHub indexed searches for run_daily and render.yaml returned zero items WITH incomplete_results=true. This is NOT evidence of no references.
[ASSUMED] Complete exact reference inventory and Render dashboard checklist remain deferred. Next inventory must cover root render.yaml, deploy manifests, workflows, README/docs/tests and references to both filename and module form; distinguish current branch from historical audit mentions.
[ASSUMED: dashboard checklist, not settings proof] Check each relevant Render service's repository/branch/commit, service type, build/start command, cron schedule/timezone, Blueprint association/path, auto-deploy setting and most recent deploy/logs for NOT_READY/exit 2. Read only; do not change settings or disclose secret environment values.
[READ_CODE] NEXT_WORK_PLAN's PR9 vs handoff's PR14 drift was observed but not corrected at this checkpoint. Actual state remains unverifiable by Codex.
[ASSUMED] Phase 1 lifecycle, cutoff, stop-limit, exact rule/warm-up spec, pool scaling, journal, alerting/supervision and migration design all deferred until this checkpoint is reviewed. No Phase 2 tests/code written.

### Safety, tests, deviations and next action

[READ_CODE] PREVIEW_ONLY/execution false remain in inspected main src/cloud_app.py::health/status. Ledger source checks positive long entry, daily-used date, risk and unlevered cash; no current completed tests certify those invariants. Five-arm feature remains unimplemented per Phase 0 evidence, not retested here.
[RAN_TEST] Targeted proposed-doc scan and structure validation: four allowed Markdown paths only; packet under 120 lines; no private-key/token/JWT/bearer/credential-assignment/private-URL pattern matches. This does not certify whole-repository secret absence.
[ASSUMED] Deviation/uncertainty: full suite attempted on an unverified local snapshot before the inventory comparison completed; it timed out. Do not promote this attempt to a branch baseline or reuse historical CI counts.
[ASSUMED] Stop per checkpoint instruction; ask whether to prepare an isolated, verified main snapshot and retry the suite before design. The requested one full-suite attempt was used; no automatic retry. Do not alter either protected legacy entrypoint.
