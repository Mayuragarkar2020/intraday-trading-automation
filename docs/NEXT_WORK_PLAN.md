# Next work plan — Phase 1 design review

[READ_CODE] Updated2026-11-01. Read PROJECT_HANDOFF.md latest checkpoint, docs/audit/AUDIT_PACKET.md and docs/design/README.md. Current approved intent is Mayur's D-001..017 in docs/audit/DECISIONS.md; older single-choice/window assumptions are conflicts, not authority.

## Source, documented deployment and verification

[READ_CODE] Current-main baseline inspected: 79a2d3086c8aea660dc31068e2758db1f7332808. Latest handoff documents approved web PR14 at ceaaf577c8e30e4713da19176828b1b43b3a0226, deploy dep-dbjcdlc9v7es739n1hs0; research cron PR12 at6d6e8152da96da2c575a59e0b980448b774d059b, deploy dep-dbjbnf67bikc73f03i8g.
[ASSUMED] Those are historical documented deployment checkpoints, NOT fresh proof. Actual Render state is **unverifiable by Codex**. This corrects the former current-web PR9 statement; PR9 is historical.
[READ_CODE] PR15 is proposed inactive controller work; it does not implement the newly approved five-arm/all-day/stop-limit/AON contract unchanged. PR13's automatic winner prototype is not an approved replacement for human confirmation. PR10 remains deferred according to handoff.
[READ_CODE: CI-reported] Current main test-phase-1 run41290657216 succeeded (539 tests, both browser checks). Local baseline UNKNOWN because separate clone failed and original workspace is mixed/unversioned. No test run on original workspace this session.

## Next checkpoint

[ASSUMED: proposal] Review docs/design/README.md and numbered engineering proposals, then independent audit of limit semantics, cutoff, DB atomicity, exact rules and supervised recovery. All design is proposed, not implementation or activation.
[ASSUMED: proposal] Phase2 ONLY after Mayur explicitly approves Phase1 AND an exact-source reproducible baseline exists for implementation. Then tests-first pure lifecycle/replay slice; no deployment, cron/config change, or broker order path.
[ASSUMED: proposal] Separate PG constraint/concurrency and actual market/source/alert/supervision validation remain required before any forward-paper release request. Reviewed calendar ends6November; no automatic extension or afternoon performance validation.
[ASSUMED: approved constraint] PREVIEW_ONLY; no real-money orders/secrets; long-only, INR9,800 maximum planned cost-inclusive risk, one daily fill, no leverage. Do not edit/archive src/run_daily.py or root render.yaml. No Render/deploy/cron change without explicit approval.
