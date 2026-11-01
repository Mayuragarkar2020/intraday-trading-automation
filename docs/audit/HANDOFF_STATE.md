# Handoff state — 2026-11-01 IST
[READ_CODE] BLOCKER: the local Git work-tree defect exists and MUST be resolved before Phase 2. Earlier Codex diagnostics at C:\dev\intraday-trading-automation reported inside-work-tree=true, git-dir=.git, core.bare=false, empty GIT_DIR/GIT_WORK_TREE, but status/diff failed: “fatal: this operation must be run in a work tree”. Explicit work-tree and fsmonitor overrides also failed. Root cause UNKNOWN; no repair attempted.
[READ_CODE] Read repository branch codex/phase1-review-round2 at 2ba36d09afd02bc266cb61cd78c9c392a0a69af3 through the GitHub connector; exact required head. No local Git commands or application tests run in this handoff.
[READ_CODE] Labels: READ_CODE = inspected repository or attributed task/transcript evidence; RAN_TEST by Mayur = supplied human-run result, not Codex execution; ASSUMED = unverified interpretation/proposal. Approval does not establish implementation, testing or deployment.
## 1. Purpose and operating model
[READ_CODE; D-001,D-047; Mayur briefing] Mayur is a working professional and owns every decision; Codex acts only within his authorized scope.
[READ_CODE; D-001,D-005] The system surfaces qualified setups; Mayur chooses candidates. If he selects nothing, nothing trades.
[READ_CODE; D-001,D-045] Confirmation freezes prices, full quantity and fees, then arms a paper stop-limit intent.
[READ_CODE; D-013–D-015,D-021] After confirmation the system enters, protects, manages, exits and journals without further action from Mayur; faults block new trades or retain visible recovery exposure.
[READ_CODE; Mayur briefing] The independent architect sees only repository audit records and pasted material. Unwritten actions and assumptions are invisible to the auditor.
## 2. Pipeline — SPEC_CURRENT.md section at each stage
[READ_CODE; D-008,D-030] Automatic universe — §Universe and pool: EQ; price ₹300–5,000; 20 completed sessions with positive volume; traded value mean≥₹100Cr, median≥₹50Cr, latest≥₹75Cr, latest/mean≥0.75, minimum last five≥₹30Cr; exclude restricted/unknown and 2%/5% bands; revalidate before 09:15.
[READ_CODE; D-016,D-032,D-042,D-043] Manual universe — §Universe and pool: persistent T-1 CSV, user identifier/note and separate view; waive automatic price/history/liquidity gates; require regular rolling-settlement intraday square-off eligibility, not suspended, verified exclusion of 2%/5% bands; unknown holds; daily checks, visible suspension, 30-day reminder.
[READ_CODE; D-020,D-034,D-035,D-039] Pool — §Universe and pool: up to 50 automatic +25 manual; liquidity ranking, available-history mean for short histories; zero-history IPO CSV-priority lane with flexible five-slot allocation; 75 is capacity, not measured throughput; no-trade complete-sweep p95≤60s evidence required.
[READ_CODE; D-005,D-009,D-024,D-040] Scan/qualify — §Signal and cohorts: 5m C0 close strictly above prior three highs; C0 EMA10>EMA20, close above both/session VWAP, RVOL≥1.2, completed 15m trend; prior-three width≤2.5%; separate IPO substitutes; scan 09:15–14:35.
[READ_CODE; D-001,D-004,D-010,D-017,D-028] Surface/select — §Selection, sizing and atomicity; §Time and evidence: cockpit/Telegram/chart link, confirmed bounded override, quote<T and tick/SL/freshness/risk checks; known at/after 14:30 is hidden/shadow. Earlier hiding is only an auditor proposal.
[READ_CODE; D-022,D-026,D-045] Arm — §Selection, sizing and atomicity: T=high(C0)+tick; S=minLow(C0..-3C)-tick; freeze T/S/L/Q, full q and fees; L-Q risk plus fees≤₹9,800; cash≤₹980,000; lifetime 15 minutes; pre-entry low≤S invalidates.
[READ_CODE; D-002,D-003,D-006,D-044] Trigger/enter — §Entry and protection: resting BUY stop-limit, L=ceil_tick(T+max(0.15%T,3 ticks)), placeholder; open>L cancels GAPPED_THROUGH; one winner, others atomically cancelled; paper all-or-nothing.
[READ_CODE; D-019,D-021,D-027,D-029] Protect/manage — §Entry and protection: resting SELL stop-limit, Q=floor_tick(S*(1-1%)), placeholder; conservative open<Q/low<Q failure policy; STOP_NOT_FILLED recovery; no profit target; 5m EMA10-close exit and 1.5R cost-breakeven modification.
[READ_CODE; D-011,D-013,D-018,D-023,D-047] Exit/recover — §Time and evidence; §Entry and protection: last eligible fill interval 14:25–14:30; cancel untriggered arms at 14:30; close by 15:00; cancel-confirm-reconcile before exit; halt/failure waits for valid post-intent price.
[READ_CODE; D-010,D-014,D-015,D-032] Journal/shadow — §Journal, alerts and recovery: authoritative events, derived JSON, costs/versions/MFE/MAE/selection age/user reason/source/cohort; unselected/cancelled/hidden alternatives shadow; restart reconciles events.
## 3. Hard invariants — current enforcement versus planned tests
[READ_CODE] Targeted source/test reads: src/risk_engine.py, src/forward_paper_ledger.py, src/cloud_app.py; tests/test_risk_engine.py, test_forward_paper_ledger.py, test_paper_entry_selection.py, test_paper_choice.py. No tests executed by Codex.
| Invariant | Current code/test evidence | Current-strategy gap / planned test |
|---|---|---|
| [READ_CODE; D-047] PREVIEW_ONLY | cloud_app health/status: execution_enabled=False, mode=PREVIEW_ONLY | Actual runtime/deployment UNVERIFIED; no activation |
| [READ_CODE; D-022,D-047] ₹9,800 including costs | risk_engine.size_long default capital×fraction; test_risk_includes_costs; ledger RISK_CAP=9800; test_exact_inclusive_risk_cap_and_separate_no_leverage_gate | New ARM-time L-Q calculation not enforced today; planned test_cost_inclusive_limit_to_stop_limit_cap_9800; mutation proof not run |
| [READ_CODE; D-047] ₹980,000 / no leverage | risk_engine cash cap / test_cash_cap_lowers_quantity; ledger unlevered cash check / inclusive-risk test above | Entry-fee-inclusive arm cash policy pending; planned test_capital_980000_no_leverage |
| [READ_CODE; D-047] Long only | size_long requires 0<stop<entry; ledger requires positive q and sets BUY; test_invalid_entry_fails_without_creating_account covers negative/zero q and invalid stop | Planned test_only_long_positive_buy_entry; no new-strategy mutation proof |
| [READ_CODE; D-002] One filled entry/day | ledger used_entry_dates; test_flat_account_still_remembers_filled_daily_entry; size_long/test_prevent_second_trade | New multi-arm DB uniqueness not enforced today; planned test_one_filled_entry_per_ist_day, test_postgres_simultaneous_fill_atomicity |
| [READ_CODE; D-002] At most five arms | Legacy test_concurrent_manual_choices_reserve_only_one_current_stock covers one choice, NOT five arms | Five-arm model not enforced today; planned test_five_armed_hard_cap |
| [READ_CODE; D-006,D-007,D-012] Bounded entry, no chase, AON | Briefing records legacy replay max(open,trigger) and partial-fill conflict | New resting stop-limit/AON not enforced today; planned test_entry_buffer_formula_v2_fraction_floor_rounding, test_gap_through_cancels_without_rearm |
| [READ_CODE; D-004,D-018,D-047] Scan/entry/exit windows | Ledger invalid-entry test rejects 11:30:01: old-window conflict; no current end-to-end 15:00 proof | New windows not enforced today; planned test_last_eligible_fill_candle, test_confirmation_delay_last_c0_close; cannot guarantee tradable exit |
| [READ_CODE; D-023,D-047] No broker/secrets/deploy/cron/Render/legacy edits | Handoff changes one audit Markdown path only; no source/config mutation | Whole-repository secret absence/runtime state not certified; no engineering authorization |
## 4. State matrix — current strategy, not legacy equivalence
[READ_CODE] DESIGNED includes approved intent and explicitly proposed details. Legacy baseline does not validate the new strategy. DEPLOYED is unverifiable by Codex for every component; no current Render-settings proof.
| Component | Current state and evidence | Implementation/testing limit |
|---|---|---|
| [READ_CODE] Signal | DESIGNED; SPEC §Signal | Briefing: old three-bar detector lacks strict C0 breakout; new rule not IMPLEMENTED/TESTED |
| [READ_CODE] Entry | DESIGNED; SPEC §Entry | Legacy max(open,trigger)/partials are not the new resting model; not TESTED |
| [READ_CODE] Stop | DESIGNED; SPEC §Entry | New Q/STOP_NOT_FILLED bracket not IMPLEMENTED/TESTED |
| [READ_CODE] Sizing | DESIGNED; SPEC §Selection | Legacy risk_engine/ledger IMPLEMENTED; baseline covers legacy; new ARM-time L-Q not IMPLEMENTED/TESTED |
| [READ_CODE] Five-arm and daily fill | DESIGNED; SPEC §Selection | Legacy daily-fill protection IMPLEMENTED/tests exist; new five-slot/atomic-winner DB constraints not IMPLEMENTED/TESTED |
| [READ_CODE] Universe | DESIGNED; SPEC §Universe | Earlier audit describes legacy receipts/screens; full current policy not proven IMPLEMENTED/TESTED |
| [READ_CODE] Pool | DESIGNED; SPEC §Universe | 75/50+25 selection and measured p95 gate not IMPLEMENTED/MEASURED |
| [READ_CODE] Manual route | DESIGNED; D-042,D-043 | Current CSV window/tradability/identifier journey not IMPLEMENTED/TESTED |
| [READ_CODE] IPO profile | DESIGNED; D-039–D-041 | Provisionally accepted; indicators/allocation not IMPLEMENTED/TESTED; efficacy unknown |
| [READ_CODE] Alerts | DESIGNED; SPEC §Journal | Telegram/daily alive/critical delivery not proven IMPLEMENTED; email only a pending auditor proposal |
| [READ_CODE] Supervision | DESIGNED; D-014/P-008 | Independent watchdog/restart mechanism UNVERIFIED; no operational proof |
| [READ_CODE] Journal | DESIGNED; SPEC §Journal | Legacy ledger events IMPLEMENTED; new complete cohort/MFE/MAE/ARM fields not proven IMPLEMENTED/TESTED |
## 5. Decision map — approved, proposed, pending auditor findings
[READ_CODE] Approved by Mayur in DECISIONS: D-001–017 core flow/windows/guards; D-018–023 exchange time/bracket/L-Q/neutrality; D-024–029 filters/distance/ticks/overrides/stop rule; D-030–038 universe/CSV/pool/IPO design; D-039–041 provisional IPO; D-042–047 upload/minimal gate/ties/ARM/live deferral/constraints. Latest amendments govern; buffers remain placeholders.
[READ_CODE] Current proposals: P-002 recovery details; P-007 DB mechanics; P-008 watchdog; P-009 shadow; P-010 base; P-018 CSV details; P-019 ranking details; P-024 freshness; P-025 participation; P-026 reservations/partial-bar/priority details. Referencing them in SPEC does not approve them.
[READ_CODE] Superseded proposals: P-001, P-003–006, P-011–017, P-020–023. Latest append-only CORRECTION governs P-005/P-013/P-020/P-023; accepted TTL/stop-rule parts have separate D decisions.
[READ_CODE: Mayur-supplied auditor report] All seven items below remain PENDING AUDITOR PROPOSALS/findings awaiting Mayur; they are not registered decisions, new P-IDs or authority to act:
[ASSUMED: PENDING AUDITOR 1] Auditor assesses P-026 summed paper cash reservations as contrary to D-046 and potentially reducing five arms to three/four; proposes per-arm cash only, no cross-arm reservation, a counterfactual journal flag; live blocking stays pre-live. No measured arm count or approved resolution.
[ASSUMED: PENDING AUDITOR 2] Hide/no alert for C0 after 14:20 in bar-only mode; shadow reason NO_FULL_ELIGIBLE_CANDLE. Current SPEC still allows surfacing before 14:30; no visibility change made.
[ASSUMED: PENDING AUDITOR 3] Require priority on all IPO-flagged CSV rows at upload, reject missing; equal priorities use ascending security ID. N0 pool priority already required by D-039; broader upload/tie validation remains pending.
[ASSUMED: PENDING AUDITOR 4] Design email fallback for STOP_NOT_FILLED/watchdog critical alerts; no credentials/code. Current channel is Telegram only; no fallback implemented.
[ASSUMED: PENDING AUDITOR 5] Quote≤5s and candle≤90s remain provisional freshness placeholders; P-024 is not approved.
[READ_CODE: auditor finding 6 / CORRECTION] AUDIT_PACKET “local baseline UNKNOWN” is stale after Mayur's human-run result below. Historical failed attempts remain true. Only this handoff records the correction; other files intentionally unchanged.
[ASSUMED: PENDING AUDITOR PROCESS 7] Mayur will create one new PR from codex/phase1-review-round2 to main and close PRs16–19 as superseded. Codex takes no creation/merge/closure action on that process today.
## 6. Top ten risks and unverified claims — ranked
[READ_CODE] 1. Local Git work-tree defect blocks Phase 2; root cause unknown; a successful baseline does not prove current clean status.
[READ_CODE] 2. New C0/resting bracket/ARM quantity/five-arm lifecycle is not implemented; legacy baseline cannot certify it.
[ASSUMED] 3. Failed stop/halts can exceed ₹9,800 and 15:00; conservative OHLC cannot prove real queue/path.
[ASSUMED] 4. P-026 cash reservation conflicts with the auditor's paper interpretation; do not silently shrink arms or waive cash checks.
[ASSUMED] 5. Late setup visibility versus partial-candle evidence is unresolved; the post-14:20 bar-only hiding rule is pending.
[ASSUMED] 6. Fees, slippage, participation, ticks and source contracts remain unpinned; unknown must not mean zero/default success.
[ASSUMED] 7. IPO priority validation/ties and experimental RVOL/HTF can skew selection; efficacy unvalidated.
[ASSUMED] 8. Telegram-only critical alerts and independent restart/watchdog remain unverified; email fallback is unapproved.
[ASSUMED] 9. NSE tradability/band sources are documented-only; IPO TFT exclusions and 75-stock sweep p95 remain unverified.
[ASSUMED] 10. Live cash blocking/external simultaneous fills are unresolved; paper DB uniqueness cannot prevent broker double fills; live multi-arm deferred.
## 7. File, PR and environment map
[READ_CODE] Canonical: docs/design/SPEC_CURRENT.md; approval authority: latest appendices in docs/audit/DECISIONS.md. PARAMETER_REGISTER.md and PHASE2_PLAN.md list inputs/gates. Execution/lifecycle/recovery/setup/universe/IPO/replay design files are detail; AUDITOR_BRIEFING.md, AUDIT_PACKET.md and PROGRESS_LOG.md are dated history, not overrides.
[READ_CODE] GitHub open PR snapshot: draft stack16→17→18→19; draft13/15 reference-only; PR1/10 also open outside this design stack. PR19 input head 2ba36d09. No PR created, merged or closed in this session.
[RAN_TEST by Mayur; supplied 2026-11-01, NOT Codex] Baseline main79a2d3086c8aea660dc31068e2758db1f7332808; Windows Python3.12, no virtual environment; CI uses3.11. Command: $env:PYTHONUTF8='1'; python -m pytest -q --basetemp=C:\dev\pytest-tmp --durations=10 =>504 passed,35 skipped,0 failed,0 errors,53.49s,total539.
[RAN_TEST by Mayur; supplied] All35 skips are PostgreSQL-only tests across test_forward_capture, test_forward_paper_ledger, test_forward_research_signal, test_paper_api, test_paper_choice, test_paper_entry_selection, test_paper_trade_management, test_universe_receipts, test_universe_scanner, test_universe_store. Same-commit CI:539 passed,both browser checks passed. Human pytest proves that legacy non-PG baseline; PG/browser evidence comes from CI, not that command. Other environments could exercise them, but this local run did not.
[RAN_TEST by Mayur; supplied] Earlier environmental failures: default pytest-temp PermissionError (262 errors); Windows cp1252 UnicodeEncodeError in tests/test_research_csv.py::test_cockpit_javascript_syntax, subprocess text mode without explicit encoding. Windows command MUST use PYTHONUTF8=1 and --basetemp outside repo. No repair/code change made here.
## 8. Prohibitions and Phase 2 gates
[READ_CODE; D-047] No Phase2/engineering/application/broker code; no secrets/deployment/cron/Render changes; never edit/archive src/run_daily.py or root render.yaml; no PR merge/closure; only Mayur approves. Do not run the full test suite today.
[READ_CODE; D-047] Before Phase2: resolve local work-tree defect; verify clean exact-base checkout; retain/reconcile baseline evidence for chosen base; pin slice1 parameters/fees/ticks/decimal fixtures; obtain Mayur answers where policy blocks and explicit “start Phase2”. Baseline exists for79a2d308, not blanket certification of other bases/runtime/new rules.
[READ_CODE] Proposed sequence: pure signal/prices/ARM sizing/tests; OHLC simulator; lifecycle; PostgreSQL constraints; replay analysis. P-010 proposes main/PR14 foundation; PR13/15 are not approved alternate bases.
## 9. Contradictions/stale statements and dated session record
[READ_CODE] CORRECTION2026-11-01: packet/briefing “local baseline UNKNOWN” predates Mayur's verified human baseline and is stale. The work-tree defect is separate; no historical failed run rewritten.
[READ_CODE] Old briefing mixed-tie/T-1/trigger-sizing/band-only statements are superseded by D-042–045; its addendum/latest DECISIONS identify history. Detail precedence notices do not make obsolete wording current.
[READ_CODE] Old P-005/P-013/P-020/P-023 “proposed” rows conflict with latest correction dispositions; read appendices. P-026 cross-arm cash and late visibility are challenged, not superseded by unapproved auditor proposals.
[READ_CODE] 15:00 closure is a constraint/target, not guaranteed execution in a halt/stop failure; named planned tests do not exist merely because listed. Source PREVIEW_ONLY status is not actual Render evidence.
[READ_CODE] Session2026-11-01: read six ordered primary documents plus targeted legacy risk/test sources to identify present enforcement; publication uses GitHub tree/commit/leased branch-ref update, only docs/audit/HANDOFF_STATE.md, branch codex/phase1-review-round2. No local work-tree mutation.
[READ_CODE] Instruction conflict: “Do not touch any other file” versus final PROGRESS_LOG append. Kept one-file limit; this dated record does NOT claim PROGRESS_LOG/AUDIT_PACKET/DECISIONS updated. No auditor proposal approved or acted on.
[ASSUMED] Final immutable commit SHA and CI status are reported after publication in chat, not self-embedded. Await Mayur/auditor prompts; stop without beginning the next task.
