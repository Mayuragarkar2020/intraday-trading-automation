# Baseline evidence, test design and protected legacy references

## Baseline status and source identity

[READ_CODE: CI-reported] Pinned main 79a2d3086c8aea660dc31068e2758db1f7332808; workflow test-phase-1; https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41290657216 completed SUCCESS. Test job: 539 passed, 3 warnings, 41.97s, no skipped count in summary; PostgreSQL18 service configured. Chromium job: cockpit and paper browser scripts passed. This is independent CI-reported evidence, not local RAN_TEST.
[READ_CODE: prior-session test record] Existing directory is not a Git repository. Commands git rev-parse --show-toplevel, git status --short --branch and git log --oneline --branches --not --remotes -5 failed. Therefore branch/status/uncommitted/unpushed are unavailable, not clean. Comparison against recorded PR15 codex/human-paper-controller 9ec22efae49a633c6f8cba09f78ac41b204de739: sixteen differing files, forty-seven missing files, four extra non-generated files. Exact lists in PROGRESS_LOG session3; no reset/clean/stash/checkout/delete.
[READ_CODE: prior-session test record] Separate git clone of origin/main to baseline-main-20261101 failed with getaddrinfo() thread failed to start. No faithful local checkout established. Old workspace was not used for another pytest run. Original manifest/log files remain intact.
[READ_CODE: prior-session test record] Probe: pytest-timeout absent, Playwright absent, Chromium cache absent; pg_isready/docker commands unavailable. Existing PostgreSQL service not established or contacted; no test credentials obtained/used.
[ASSUMED] Local baseline UNKNOWN. Main CI baseline CI-reported PASS. No claim for PR15 or the mixed directory. Proposed Phase2 requires approved design and exact starting-source baseline from reproducible CI/local evidence; cannot borrow another branch's result.

| Segment | Intended command | Current outcome/count/duration |
|---|---|---|
| [ASSUMED] a Collection | python -m pytest --collect-only -q | not runnable locally: verified checkout unavailable; counts N/A; not run |
| [ASSUMED] b Pure unit | python -m pytest <reviewed-pure-node-list> -q --timeout=10 --timeout-method=thread --durations=20 | not runnable locally: checkout/plugin/list unavailable; N/A; not run |
| [ASSUMED] c PG concurrency | python -m pytest <reviewed-pg-node-list> -q --timeout=30 --timeout-method=thread --durations=20 | not runnable locally: checkout/service/plugin unavailable; N/A; not run; rely on pinned CI |
| [ASSUMED] d Chromium | python scripts/check_cockpit_browser.py; python -m scripts.check_paper_browser | not runnable locally: checkout/Playwright/Chromium unavailable; N/A; not run; rely on pinned CI |

[READ_CODE] Angle-bracket node lists are unexecuted protocols, not literal completed commands. CI's actual command is python -m pytest -q. Local unavailable segments have no test counts or measured test duration.
[READ_CODE: prior-session test record] Prior session full-suite command python -m pytest -q --basetemp=.test-phase1-baseline-20261101 timed out after180s, output only two dots. This session did not rerun that mixed snapshot.
[ASSUMED] No exact slow/hanging test name is known; do not infer it from alphabetical order. CI lacked --durations and timing per test, so no top20 slow list can be invented. Prior Windows TestClient reports are hypotheses, not a new diagnosis.

## Clone failure explanation and clean checkout handoff

[READ_CODE] Prior recorded native Git error is getaddrinfo() thread failed to start. The recorded process failed before a clean checkout existed; no original files were reset/cleaned/stashed/checked-out/deleted.
[ASSUMED] Interpretation: Git/libcurl's resolver could not start a DNS helper thread. The exact root cause is UNKNOWN: sandbox/process/thread limits or host runtime restrictions are plausible; the message is not proof of a bad repository, invalid credentials or ordinary DNS “name not found”. No diagnosis or resolver/thread experiment ran this round.
[ASSUMED: proposal] Mayur supplies a NEW clean checkout, not an overwrite of the mixed directory. Verify git rev-parse --show-toplevel; git branch --show-current; git status --porcelain=v1; git rev-parse HEAD; git rev-parse origin/main; and git log --oneline origin/main..HEAD. Compare HEAD/origin/main with the agreed pinned implementation SHA; inspect intended origin identity with credentials redacted. Any mismatch/uncommitted content is reported before action; no reset/clean/stash command.
[ASSUMED: proposal] Single Phase2 base is origin/main79a2d3086c8aea660dc31068e2758db1f7332808 (PR14 HumanChoicePaperLedger), subject to rechecking current main when checkout is provided. PR13/15 reference-only, no merge/closure. Docs branch is not an alternate application base.
[ASSUMED: proposal] Reproduce CI in an isolated Python3.11 environment with reviewed pinned requirements and test-only timeout dependency; PostgreSQL18 for concurrency; Playwright/Chromium for browser scripts. No credentials in repo. Run collection, explicit pure tests, PostgreSQL and browser segments separately under reviewed per-test/process budgets; capture exact SHA/commands/counts/durations. No environment installation/change or test retry now.
[ASSUMED] Baseline for supplied clean checkout remains UNKNOWN until verified; previous main CI evidence is historical, not a new run and not proof for PR15/this future implementation.

## Proposed test architecture (design only)

[ASSUMED: proposal] Split explicit pure, API/TestClient, SQLite-persistence, PostgreSQL-concurrency, browser, and opt-in external-market suites. Pure means no filesystem/network/database/browser; source AST/dependency review identifies exact nodes before commands are promised. Avoid broad -k not postgres pretending every remaining test is pure.
[ASSUMED: proposal] Collection process budget30s; pure per-test10s/process120s; API/SQLite per-test15s/process180s; PG per-test30s/process180s; browser each script process120s. Use pytest-timeout where supported and a supervising process budget; collect --durations=20 and -vv during diagnosis, optionally -o faulthandler_timeout=10. Install/CI modifications would be later approved implementation, not made here.
[ASSUMED: proposal] A hang record must name last STARTED node, elapsed time, timeout mode/platform and stack dump, distinguishing setup/teardown. Report every segment independently and don't let one process hang hide others. Missing PG/browser prerequisites mean NOT_RUNNABLE, not test skips/passes.
[ASSUMED: proposal] Phase2 smallest slice: pure lifecycle/replay adapter only, tests first. Required invariant tests pin literal9800 cost-inclusive cap, positive BUY/SL side, one daily fill and five-arm cap so changing configured invariants makes tests fail. Two same-candle armed candidates must yield deterministic highest-ADV single fill regardless of arrival order. Pure “race” is an interleaving/replay test, not proof of SQL concurrency.
[ASSUMED: proposal] Gap test: same eligible trigger candle O>L, even with later return inside L, is CANCELLED/GAPPED_THROUGH, zero fill and no auto-rearm; manual new confirmation requires fresh validation. Other tests cover proposed cutoff, AON anomaly, overridden prices, stop/EMA/BE precedence and idempotent recovery. PG race/constraint test is separately designed in LIFECYCLE_AND_ATOMICITY.md and cannot be represented as a pure-module test.
[ASSUMED: proposal] No new test, module, dependency, workflow, broker path or deployment is created in Phase1. Test designs do not count as TESTED traceability.

[ASSUMED] Round2 mutation/signal/resting-stop/cutoff test targets are authoritative in REPLAY_ANALYSIS_AND_TEST_PLAN.md; older illustrative tests here do not authorize the superseded next-candle-close model.

## Every literal legacy reference at pinned main

[READ_CODE: prior-session test record] Targeted reference inventory used main's recursive Git tree metadata, SHA-verified157 locally available blobs (raw/LF-normalized), and fetched only66 missing/different blobs through GitHub. It searched UTF-8 content for literal run_daily or render.yaml; outputs were only matches. This avoids reading the full repository into conversation context. All required remote blobs were readable. This is exact-literal scope, not proof about aliases/external service settings or later branches.
[READ_CODE] Five matches at pinned main:
| Path | Line | Reference |
|---|---:|---|
| [READ_CODE] tests/test_fail_closed.py | 1 | from src.run_daily import main |
| [READ_CODE] README.md | 40 | Older entrypoints such as src/run_daily.py and the root render.yaml describe |
| [READ_CODE] deploy/render-preview.yaml | 2 | # Do NOT auto-deploy. This file is deliberately not the root render.yaml. |
| [READ_CODE] docs/cloud_worker_rollout.md | 3 | This deployment definition is **opt-in** in `deploy/render-preview.yaml`. The original root `render.yaml` and the separate `trading-automation` service are not modified. |
| [READ_CODE] render.yaml | 8 | startCommand: python -m src.run_daily |
[READ_CODE] src/run_daily.py itself contains main returning2/NOT_READY and no literal self-reference. Root render.yaml invokes it. No file is archived/edited/deleted. Proposed design/audit documents add explanatory references; they do not create another runtime entrypoint. Historical branch references are not included in the pinned-main operational count.

## Render dashboard read-only checklist

[ASSUMED: proposal] Actual state is **unverifiable by Codex** this session. In the intended workspace, inspect each relevant service:
1. [ASSUMED] Repository, branch and currently deployed commit/deploy ID, distinguishing web, research cron and similarly named older scaffold services.
2. [ASSUMED] Service type, build command and start command. Flag python -m src.run_daily or NOT_READY exit2; do not replace commands in this phase.
3. [ASSUMED] Blueprint association and Blueprint path: root render.yaml versus deploy/render-preview.yaml/deploy/render-worker.yaml; whether any old Blueprint still manages an active resource.
4. [ASSUMED] Cron schedule and its timezone convention; most recent invocation exit/logs; verify time coverage independently of TZ environment display.
5. [ASSUMED] Auto-deploy setting and pending builds. No “docs-only means safe auto-deploy” assumption; this PR is not merged or deployed by Codex.
6. [ASSUMED] Runtime flags and dependencies are read-only checks; verify execution remains disabled without revealing/copying secret values, tokens or internal connection URLs.
[ASSUMED: proposal] Report a screenshot or service metadata with secrets hidden only if needed for later operation. No archive/delete/deploy/change approval is requested with this checklist.
