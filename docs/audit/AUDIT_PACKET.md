# Audit packet — 2026-11-01 / Phase1 review round2
## a. Session summary
[ASSUMED] BAD NEWS: local baseline UNKNOWN; actual Render state unverifiable by Codex; no application test/market analysis this round.
[READ_CODE] Seven design docs revised/added for C0 resting bracket; old next-close primary/receipt cutoff/top100 superseded.
[READ_CODE] Parent b82089ed61fbf925b6052c09c820a7fec6c21839; branch codex/phase1-review-round2; application base main79a2d3086c8aea660dc31068e2758db1f7332808.
[READ_CODE] D-003/D-005/D-006 explicitly amended; D-018..023 from Mayur; no Codex proposal marked approved.
[READ_CODE] Phase2 NOT STARTED; no PR closed/merged, no deployment/Render/cron/broker action.

## b. Safety invariants
[READ_CODE] PASS diff-only: PREVIEW_ONLY untouched; no app/broker-order path/client/endpoint/credential added.
[RAN_TEST] PASS limited scan:13 proposed Markdown files,zero credential/token/private-URL pattern matches.
[ASSUMED] UNVERIFIED: repository-wide secret absence; runtime PREVIEW_ONLY/Render settings not checked.
[ASSUMED] UNVERIFIED by current tests: literal9800/L-Q risk,long-only,one daily fill,capital980000/no leverage,five arms,limit formula.
[READ_CODE] These invariants have named future mutation targets; revised DB constraints/bracket NOT implemented.
[READ_CODE] PASS scope: no deployment/config/cron/workflow/Render change; run_daily.py/root render.yaml untouched.
[ASSUMED] Stop failure can exceed9800; no guaranteed maximum realized-loss claim.

## c. Traceability delta
[READ_CODE] PI1..7/current D1..23 DESIGNED only; new C0/bracket tests not claimed TESTED.
[READ_CODE] Added capital/window/entry-cutoff/closure target rows; old implementation evidence not reused as new-model proof.
[READ_CODE] Superseded proposal bundles P-003/P-004/P-006; new implementation-base/filter/override/stop-model proposals remain proposed.

## d. Deviations, risks, assumptions, shortcuts
[ASSUMED] Primary OHLC low<Q pessimistically gives STOP_NOT_FILLED despite a possible earlier valid S fill; sensitivity required.
[ASSUMED] Confirming mid-bar needs post-confirmation fine data or explicit ambiguity hold; full prior high cannot prove later trigger.
[ASSUMED] Late receipt can reconcile an eligible resting14:25 window, not create a new postcutoff order.
[ASSUMED] Paper contingent trigger sizing may not map to a broker resting fixed-quantity order; future live blocker.
[ASSUMED] Multiple external resting orders can fill before cancellation; paper DB uniqueness is not broker mutual exclusion.
[ASSUMED] Cancel failure/halts may delay exit beyond15:00; retain critical exposure and breach, never imaginary flat.
[ASSUMED] C0 filters,2.5%maxdistance,tick defaults,override limits/stop OHLC rule await Mayur; buffer values placeholders.
[READ_CODE] Clone's recorded getaddrinfo-thread error does not prove root cause; no new diagnosis or retry this round.

## e. Unverified claims
[ASSUMED] No fresh CI/local test, historical-data analysis,selected-buffer result,live fill or phone-delivery proof.
[ASSUMED] Prior main CI539/browsers is historical documentary evidence, not this session RAN_TEST.
[ASSUMED] Dhan capability/static-IP/product/cutoff/stop fields not checked as current facts; pre-live checklist only.
[ASSUMED] Intrabar order/path/exact MFE-MAE may be unknown from5m bars; bounds/cohorts recorded.
[ASSUMED] Clean checkout not yet supplied; afternoon performance and scale-up p95 not measured.

## f. Test results
[ASSUMED] Application tests:NOT RUN (design-only); command none; counts/skips/duration N/A.
[RAN_TEST] functions.exec doc validator:allowed13 Markdown paths;append-only log;packet<=120lines;coverage28 rows;IDs/proposal status.
[RAN_TEST] Document arithmetic fixtures verified for three limits and risk quantities/comparison; NOT implementation tests.
[RAN_TEST] Targeted private-key/GitHub-token/JWT/bearer/credential-assignment/private-URL pattern scan:0matches.
[READ_CODE] No test code or dependency added; future test names in REPLAY_ANALYSIS_AND_TEST_PLAN.md.

## g. Numbered open questions
[ASSUMED: proposed, awaiting Mayur] 1. Keep C0 EMA/VWAP/RVOL/15m filters and prior3width denominator close(-1C)?
[ASSUMED: proposed, awaiting Mayur] 2. Accept max(T-S)/T2.5% pending sensitivity analysis?
[ASSUMED: proposed, awaiting Mayur] 3. Confirm one-tick T/S defaults?
[ASSUMED: proposed, awaiting Mayur] 4. Confirm stop-limit rather than plain-limit semantics?
[ASSUMED: proposed, awaiting Mayur] 5. Accept bounded overrides and conservative low<Q no-fill model with alternate sensitivity?
[ASSUMED] Buffer calibration/clean checkout remain pending; no Phase2 or deployment requested.

## h. Suggested next step / auditor first paths
[ASSUMED] Audit round2 design,answer default questions,supply clean checkout; Phase2 needs separate approval/baseline.
[READ_CODE] First5:TIME_AND_EXECUTION.md;LIFECYCLE_AND_ATOMICITY.md;SETUP_AND_UNIVERSE.md;REPLAY_ANALYSIS_AND_TEST_PLAN.md;../audit/DECISIONS.md (design/ paths unless prefixed).

## Coverage map — paths relative to docs/design/; coverage means designed, NOT tested
| Phase1 item | Document and section |
|---|---|
| [READ_CODE] a Lifecycle | LIFECYCLE_AND_ATOMICITY.md — Event envelope and transitions |
| [READ_CODE] b Time windows | TIME_AND_EXECUTION.md — Cutoff by exchange candle window |
| [READ_CODE] c Shelf life/noise | LIFECYCLE_AND_ATOMICITY.md — Selection contract; JOURNAL_ALERTS_RECOVERY.md — Telegram |
| [READ_CODE] d Selection | LIFECYCLE_AND_ATOMICITY.md — Selection contract and override bounds |
| [READ_CODE] e Multi-arm/SQL | LIFECYCLE_AND_ATOMICITY.md — Database guarantees and same-candle ties |
| [READ_CODE] f Limit/AON/sizing | TIME_AND_EXECUTION.md — Resting entry; Protective stop; Sizing |
| [READ_CODE] g Replay correction | TIME_AND_EXECUTION.md — Replay correction; REPLAY_ANALYSIS_AND_TEST_PLAN.md |
| [READ_CODE] h Precedence/halt | TIME_AND_EXECUTION.md — Sizing/precedence; JOURNAL_ALERTS_RECOVERY.md — Failure matrix |
| [READ_CODE] i Exact setup | SETUP_AND_UNIVERSE.md — Side-by-side change map; Exact preserved calculations |
| [READ_CODE] j Shadow | JOURNAL_ALERTS_RECOVERY.md — Shadow tracking without selection bias claims |
| [READ_CODE] k Catalysts | SETUP_AND_UNIVERSE.md — Persistent manual catalysts |
| [READ_CODE] l TradingView | JOURNAL_ALERTS_RECOVERY.md — TradingView links and test cases |
| [READ_CODE] m Journal | JOURNAL_ALERTS_RECOVERY.md — Round2 additions; Authoritative schemas |
| [READ_CODE] n Scaling | SETUP_AND_UNIVERSE.md — Scaling; Hybrid universe/p95 gate |
| [READ_CODE] o Supervision/failures | JOURNAL_ALERTS_RECOVERY.md — Independent supervision; Failure matrix |
| [READ_CODE] p Telegram | JOURNAL_ALERTS_RECOVERY.md — Telegram alert contract; stop-failure critical row |
| [READ_CODE] q Flow | README.md — Updated flow |
| [READ_CODE] r PR drift/Render | ../NEXT_WORK_PLAN.md; ../PROJECT_HANDOFF.md — latest checkpoint |
| [READ_CODE] R2-1 Strategy comparison | SETUP_AND_UNIVERSE.md — Side-by-side change map |
| [READ_CODE] R2-2 Fill/cutoff/risk | TIME_AND_EXECUTION.md — all execution sections |
| [READ_CODE] R2-3 Same-candle atomicity | LIFECYCLE_AND_ATOMICITY.md — transitions; Database guarantees |
| [READ_CODE] R2-4 Replay measurement | REPLAY_ANALYSIS_AND_TEST_PLAN.md — Buffer and selection evidence; Stop sensitivity |
| [READ_CODE] R2-5 Overrides | TIME_AND_EXECUTION.md — Sizing on stop limit overrides and precedence |
| [READ_CODE] R2-6 Acceptance restored | ../NEXT_WORK_PLAN.md — Restored acceptance checks |
| [READ_CODE] R2-7 Sole base | LIFECYCLE_AND_ATOMICITY.md — Authoritative Phase2 base |
| [READ_CODE] R2-8 Clone/setup | BASELINE_AND_REFERENCES.md — Clone failure explanation and clean checkout handoff |
| [READ_CODE] R2-9 Mutation/new tests | REPLAY_ANALYSIS_AND_TEST_PLAN.md — Phase2 tests-first protocol |
| [READ_CODE] R2-10 Audit coverage | ../audit/AUDIT_PACKET.md — this coverage map |
