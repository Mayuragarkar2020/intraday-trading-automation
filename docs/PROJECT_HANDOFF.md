# Intraday Trading Automation — authoritative project handoff

## Phase1 review round2 — 1 November 2026

[READ_CODE] Round2 design supersedes round1: authoritative C0.close>prior3high signal, proposed one-tick C0/prior4 prices, resting entry/protective bracket, same-candle fill, cutoff by fill-candle START<14:30 and initial25–50 pool with measured no-trade p95<=60s scale gate. See docs/design/README.md and amended D-005/D-018..023.
[ASSUMED] Defaults/filter scope/distance/override and calibrated limit buffers remain proposed/placeholder awaiting Mayur. STOP_NOT_FILLED may lose beyond9800; no guaranteed maximum-loss claim.
[ASSUMED] Phase2 single design base is origin/main79a2d308/PR14 foundation; PR13/15 remain open reference-only. No application/test/broker path or deployment/config change; no Phase2. Actual Render state **unverifiable by Codex**; older recorded webPR14/cronPR12 checkpoints below are historical, not new proof.
[READ_CODE] Local baseline remains UNKNOWN from prior clone failure. No new local/CI test run this round; Mayur supplies clean checkout; exact-source baseline and explicit design approval required before Phase2.

## Phase 1 design review checkpoint — 1 November 2026

[READ_CODE] Source pinned main 79a2d3086c8aea660dc31068e2758db1f7332808. Phase0 accepted; Phase1 design-only proposal is in docs/design/README.md. Latest user-approved decision register D-001..017 supersedes older single-choice,11:30-cutoff,partial-fill assumptions. See audit packet for evidence limits.
[ASSUMED] Actual Render state is **unverifiable by Codex** this session. Last documented approved web release is PR14 at ceaaf577c8e30e4713da19176828b1b43b3a0226 / dep-dbjcdlc9v7es739n1hs0; research cron PR12 at6d6e8152da96da2c575a59e0b980448b774d059b / dep-dbjbnf67bikc73f03i8g. NEXT_WORK_PLAN now uses the same documentary checkpoint; older PR9 web statements below are historical.
[READ_CODE: CI-reported] Current-main test-phase-1 run41290657216 SUCCESS:539 tests and both Chromium scripts passed. This is not a local run. Separate clone failed; local baseline UNKNOWN; original workspace unchanged and not used for another test run.
[ASSUMED: proposal] Design covers five confirmed arms, close-detected/next-candle stop-limit paper entries, AON, DB daily-fill constraint, hybrid universe, exact current rules, shadow/MFE/MAE/Telegram and supervision. Precise limit/cutoff/TTL/pool choices are proposed, not silently approved.
[READ_CODE] No application/test/workflow/Render/cron change; protected legacy entrypoints untouched. No Phase2 begun. PR15 remains a previous proposal, not the design's deployed implementation.
[ASSUMED: next step] Independent design review, resolve numbered proposals, then explicit Phase1 approval and exact-source baseline before Phase2. No production action is bundled.

## Current checkpoint — 1 November 2026 (supersedes older release status)

Mayur approved PR #14's web-only release. It is merged at
ceaaf577c8e30e4713da19176828b1b43b3a0226 and Render confirms web deploy
dep-dbjcdlc9v7es739n1hs0 LIVE. No repeat merge/deploy is required.
Research cron remains PR #12 at 6d6e8152da96da2c575a59e0b980448b774d059b,
dep-dbjbnf67bikc73f03i8g LIVE. Both auto-deploy settings remain off.
This turn independently confirmed Render deployment state; a fresh public HTTP
health check could not resolve/retrieve the endpoint, so no new HTTP success
is claimed. No production mutation was made during this continuation.

PR #15: https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/15
Branch codex/human-paper-controller, tested source head
9ec22efae49a633c6f8cba09f78ac41b204de739.
CI run 41277228486 completed successfully: 565 tests passed, one skipped;
both Chromium browser suites passed. Live-source smoke was skipped.
It remains DRAFT / UNAPPROVED / UNDEPLOYED. Do not confuse PR #14 approval
with authority to deploy or enable this controller.

The controller binds the exact saved human choice to prospective paper entry,
initial SL, EMA10-close exits before 1.5R, additional cost breakeven, 14:50
flatten requests, 15:00 closure/breach accounting, recovery and derived completed
trade journals. Per-order cost/slippage/tick/participation assumptions are pinned.
The optional chosen-stock feed/worker defaults OFF; actual source/reference
verification remains false. Synthetic cleared fixtures prove software behavior,
not actual market readiness. See docs/human-paper-controller.md on PR #15.

Next: inspect 2 November actual same-day universe, complete pool coverage and
receipt timing; resolve independently verified timestamp/session/reference
production and then validate the chosen-stock full-session feed. Do not set
clearance flags true to bypass evidence. Any forward-paper production release
and activation require a separate concrete approval after readiness review.
No actual automatic forward-paper session or live-money trading is complete.
Calendar ends 6 November. No subagents. No background work between chat turns
except already deployed services.

## Human-choice cockpit ready for approval — 1 November 2026

PR #14: https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/14
Exact head 620bc0e824c8ec542ecd87d3927dbcc7c97ac55f passed 539 full
Python/API/PostgreSQL tests and both Chromium suites (run 41274461258).
It is draft/unapproved/undeployed. The current release proposal is existing WEB
SERVICE ONLY, with no cron/config/schedule/compute change or trading activation.

The main screen is shortlist -> Mayur's stock choice -> trade status/journal.
It includes a read-only plan review, advisory ranking, durable choice, withdrawal,
stale-tab/concurrency protection and an immutable choice-to-entry guard. Manual
sizing and diagnostic tools are under Advanced. Saved choices remain SELECTED_HELD;
no automatic paper or broker executor is connected by this release. The next
implementation priority is connecting that exact approved choice to the verified
full-session paper manager and automatic journal. Do not substitute PR #13's
automatic liquidity winner. Existing rule/risk/closure limits remain unchanged.

Final validation used GitHub CI after the local execution environment became
unavailable; all code/context is preserved in GitHub. Production recheck confirmed
web PR #9 and cron PR #12 still live with auto-deploy off. Do not re-request prior
PR #12 approval or deploy PR #14 without its separate web-release approval.


## 1 November 2026 — human stock choice is the primary workflow

Mayur clarified: the system shortlists setups; HE chooses which stock to trade;
the system then handles rule-based entry, trade management and post-trade journal.
Liquidity ranking is advisory, never authority to auto-select a different stock.
This supersedes older automatic-winner assumptions. Read AUTOMATION_OBJECTIVES.md
and the rewritten NEXT_WORK_PLAN.md. PR #13 remains draft and must not be merged/
activated unchanged; it must be integrated behind the exact human-choice guard.

Current source proposal: branch codex/human-choice-cockpit. It adds a shortlist/
read-only plan review, saved stock choice, replace/withdraw before an order,
position/fill/decision journal and a pinned paper account. Authenticated POST saves
only a decision, not an order. Source/runtime readiness stays held. A future
HumanChoicePaperLedger verifies the exact choice/stock/setup/entry/SL/size/time
under the same writer lock as an entry; no choice means no entry. PR #10 excluded.

Production is unchanged: web PR #9 at d724f82f48a6588acb92770f7a78246355e77b6a;
cron PR #12 at 6d6e8152da96da2c575a59e0b980448b774d059b with receipt flag.
No automatic paper/live runtime is active. Proposed next production scope after
exact-head tests: existing WEB ONLY. No cron/config/compute/schedule change or
trading activation. Choice tables initialize on authenticated user writes only.

The local Windows workspace disconnected during final checks. All latest source
is being preserved in GitHub; use exact-head CI for verification. Earlier local
63-pass/20-skip checks preceded the final choice-hash/no-choice tests. Do not
claim the final head passed locally. Actual data readiness and full forward
paper management still require verified sources and runtime integration. Keep
source work focused on the user journey while market observations are pending.


## Tested inactive bridge checkpoint — 1 November 2026

PR #13: https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/13
Exact head 4d59fa1eef0b6ddfae17e9582cb86a9dec7ed59f passed 515 full
Python/API/PostgreSQL tests and both Chromium suites in run 41272813266.
It is draft/unapproved/undeployed. Full interval assembly now reads all selected
instruments from complete committed cycles; incomplete coverage holds. The
working setup is the most recent ARMED receipt known before the breakout bar
opens. Both receipt IDs survive ranking/reservation; later receipt fills and
EMA exits preserve source lineage and restart/cash/audit identities. Computed
EMA precision and legacy batch fingerprints are preserved. Duplicate workers
reuse only already committed decisions; changed inputs/costs conflict.

Successful trade-path tests use explicitly synthetic future clearance fixtures.
Actual current producers cannot write those verified receipt/universe formats,
and real research sources remain held without ledger writes. This is not
automatic forward paper completion or permission to set verification flags true.

PR #12 remains LIVE on the research cron (6d6e8152da96da2c575a59e0b980448b774d059b,
dep-dbjbnf67bikc73f03i8g), with the approved receipt flag configured. Web remains
at PR #9; execution is disabled. No PR #13 runtime was activated or deployed.

Next essential external evidence is the 2 November market session. Inspect actual
same-day universe, full-pool coverage, first-seen/source timing and storage growth;
then resolve timestamp/session/reference contracts and implement independently
verified source producers. A full-session position feed, pinned account and cost/
liquidity assumptions, independent clock scheduling and actual validation still
precede any proposed runtime activation. Calendar ends 6 November. Do not assume
automatic readiness on Monday. No work runs between chats except deployed services.
No further production mutation is requested by this checkpoint.


## 1 November 2026 — PR #12 approved and receipt recorder deployed

Mayur approved PR #12 merge, existing RESEARCH CRON deployment and
UNIVERSE_RECEIPTS_ENABLED=true. Merged source
6d6e8152da96da2c575a59e0b980448b774d059b; deploy dep-dbjbnf67bikc73f03i8g is LIVE.
The merge-style environment update returned success and triggered that exact
deployment; no redundant deployment was triggered. No existing secrets were
read/replaced. Existing schedule */5 3-10 * * 1-5 UTC, command, 0.5c-512mb plan and
auto-deploy off were rechecked. Existing capture/universe flags were preserved.
The web remains at PR #9, d724f82f48a6588acb92770f7a78246355e77b6a,
dep-dbjbh93bc2fs73cbijl0. No web deploy or automatic paper/live activation occurred.

Exact PR #12 head c78a74277f582e3782b1624ed8531c8356d3c491 passed 493 full
Python/API/PostgreSQL tests and both browser suites (run 41271663974).
Actual weekday recording, timely coverage, row growth and DB capacity remain
unobserved. Do not claim that a Sunday deploy established receipt operation.
Read docs/universe-receipts-activation-2026-11-01.md.

Source progress: draft PR #13, codex/persisted-paper-bridge, adds an INACTIVE
persisted setup/breakout -> interval ranking/reservation -> receipt-time management
bridge. It assembles all selected instruments from complete stored cycles,
preserves receipt lineage and original decisions, and retains precise derived
EMA values and legacy batch fingerprints. Current real source/universe flags
still hold; future-clearance fixtures are not actual verification. Inspect the
latest PR head and CI. This source is not approved/deployed; no runtime is wired.

Next essential operational evidence is the 2 November market session: same-day
universe, complete pool coverage, timely/held receipts, source/session/reference
contracts and storage growth. Verified-source producers, full-session position
feed and independent clock/runtime wiring remain required before any execution
activation. Calendar ends 6 November. PR #10 remains deferred. Older PR #12
pending-approval statements below are historical and superseded here.


## 1 November 2026 — PR #12 receipt evidence ready for production approval

PR #9's approved web-only release is live at d724f82f48a6588acb92770f7a78246355e77b6a
(deploy dep-dbjbh93bc2fs73cbijl0); health/auth checks passed. The research cron is
still at PR #11 and has not been redeployed or reconfigured.

Next review: https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/12
Branch codex/universe-receipt-evidence; exact tested head
c78a74277f582e3782b1624ed8531c8356d3c491. CI run 41271663974 passed
493 Python/API/PostgreSQL tests and both Chromium suites. Local targeted checks:
69 passed, three PostgreSQL-only skipped. See docs/universe-receipt-evidence.md
on that branch. Source records immutable full-pool current candles/first-seen
times, reference-cache/input hashes, computed scanner output and post-scan known_at.
Revisions, injected inputs, retries, rollback, restart and concurrency are tested.
Backfilled setup windows hold; timely evidence still leaves all four verification
flags and forward_paper_ready/execution_enabled false. No order adapter/runtime.

CONCRETE APPROVAL PENDING: merge PR #12, deploy existing RESEARCH CRON ONLY,
enable UNIVERSE_RECEIPTS_ENABLED=true there. No web deploy, new service, extra
broker requests, schedule/compute/command change or automatic paper/live activation.
Keep existing capture/universe flags true and auto-deploy off. Adds CPU work and
PostgreSQL writes/retention; actual throughput/coverage/capacity remain unproven.
Read-only database-size inspection was blocked by the existing empty external
allowlist; no network access setting was changed. Do not weaken it for this work.

After approval/deployment: inspect actual 2 November same-day universe, full-pool
coverage, receipt first-seen/timing/row growth and source holds. Then build the
trusted persisted signal adapter and session/reference clearance from evidence.
Calendar still ends 6 November. PR #10 remains deferred. No later production or
automatic execution approval is implied by approval of the PR #9 web release.


## 1 November 2026 — PR #9 approved and deployed to web only

Mayur approved PR #9 merge and the EXISTING WEB SERVICE ONLY deployment.
Merged revision d724f82f48a6588acb92770f7a78246355e77b6a; Render deploy
dep-dbjbh93bc2fs73cbijl0 is LIVE. Health returned 200, PREVIEW_ONLY,
execution_enabled=false; unauthenticated POST /api/paper/replay returned 401.
Exact PR head 0e0983c6134eafdc0c7b5508ae6ff88c4df99795 passed 473
Python/API/PostgreSQL tests and both Chromium suites (run 41270974677).
The CSV export regression in the earlier CI run was fixed before approval.

Replay's 15:00 completed-closure deadline and ten-minute flatten lead are now
in web source. The ledger, signal journal, ranking and persistent receipt-time
manager are deployed as inactive libraries; NO forward-paper runtime is enabled.
The cron remains at PR #11, 5b9693c657f1475c1a1fd4a9c3a6a8749621eece,
dep-dbj1j37b9u1s73cq1vg0. No cron/config/schedule/compute change was made.
Auto-deploy remains off; PR #10 remains deferred/unmerged/undeployed.
Authenticated replay saving after this deployment is not agent-verified.

Next source work: full-universe persisted receipt evidence and a trusted signal
adapter. Existing scan results/hashes are insufficient first-seen evidence;
current research verification flags stay false. Actual market operation is still
unobserved. 2 November remains research validation; calendar ends 6 November.
Later releases and any automatic execution require separate approval.
Read docs/paper-web-activation-2026-11-01.md. Older draft/pending statements below
are historical and superseded by this checkpoint.


## 1 November 2026 — inactive deadline and persistent manager source

PR #9 now proposes replay v2: force_exit is a completed-closure deadline, default
15:00 IST, capped at 15:00. Flatten attempts start ten minutes earlier. Partial,
unfilled or late exits stay visible; late recovery retains the deadline breach.
Old stored replay runs are immutable; the engine-version change creates new IDs.

An inactive receipt-time simulator connects ranked entry reservations to durable
fills, initial/cost-breakeven stops, EMA10 exits before 1.5R, partial/rejected exits,
clock-driven flatten requests and persistent breach state. Its fill model is
NEXT_TIMELY_CLOSE_AT_RECEIPT, distinct from historical replay next-open fills.
A signal/order decision cannot use an earlier bar. Gaps cannot generate fills.
Clock events request/cancel/flag exposure but cannot manufacture closing prices.
All effects of one bar are journaled atomically; retries/concurrent workers and
restart audit are tested. Source attestations are caller declarations until a
trusted adapter verifies them; current research sources MUST remain held.

Local checks: 139 passed, four PostgreSQL-only skipped. Exact-head CI must be
checked on the current PR head; do not reuse the former 447-test result.
No runtime/API/cron imports the simulator. No production changes or activation.
The verified signal adapter, authoritative session/reference contracts and actual
full-universe operation remain incomplete. Calendar still ends 6 November.
Next: inspect CI, verify actual 2 November research operation and evidence, bind
trusted persisted signals/receipts, then obtain approval for a concrete release.


Updated: 31 October 2026 (IST). Read this first when resuming.
Owner: Mayur Agarkar. Private repository: https://github.com/Mayuragarkar2020/intraday-trading-automation

## Latest decision and resume checkpoint — 15:00 IST closure

Mayur confirmed on 31 October 2026: **all positions must be closed by 15:00 IST
(Asia/Kolkata)**. This is a completed-closure deadline, not permission to wait
until 15:00 to start an exit. It supersedes the former 15:15 strategy default
and the earlier pending exit-time question. Implement prospective exits early
enough for the chosen execution model; never backdate a fill or report an
unfilled/partially filled position as closed. Any failure to flatten by the
deadline must remain visible as outstanding exposure and a deadline breach.
Exact execution lead time/retry mechanics remain engineering work, not a newly
agreed trading rule. Existing replay code still uses its old default until a
reviewed source change; this documentation update does not change runtime.

Continuity summary:
- Daily liquid NSE universe; exclude 2%/5% bands, hold unknown band/identity
  data and preserve surveillance exclusions. No daily manual chart checks.
- Scan completed 5m bars using the existing EMA10/20, VWAP, relative-volume,
  15m confirmation and range conditions; entry above range high plus buffer,
  initial stop below range low minus buffer, later eligible breakout required.
- INR 980,000 capital, maximum INR 9,800 planned risk inclusive of estimated
  costs, long only, one filled entry/day and no leverage.
- Working ranking: highest 20-day average traded value among valid breakouts
  in the same 5m interval; policy remains replaceable for future ranking factors.
- EMA10-close exits remain active before 1.5R. At 1.5 price R additionally
  request cost breakeven. No fixed target. All exposure closed by 15:00 IST.
- PR #11 is deployed at 5b9693c657f1475c1a1fd4a9c3a6a8749621eece on existing
  web and research cron. Auto-deploy off; no paper/live execution. Actual
  full-pool market coverage, warm-up and persistence still require observation.
- PR #9 remains draft/unapproved/undeployed: inactive ledger, receipt-bound
  signal journal and ranked prospective reservations. Head
  91bd84736364ea1cc420fd21184b57db2b1033dd passed 447 Python/API/PostgreSQL
  tests and both browser suites in run 41222564313. Local: 79 passed,
  3 PostgreSQL-only skipped. Source holds, immutable retries, concurrency,
  rollback and no-backdated-fill checks passed; actual broker readiness unproven.
- PR #10 remains optional/deferred/unapproved; do not make it a prerequisite.
- Next: implement/test the 15:00 closure rule on the inactive paper branch,
  connect persistent trade management and trusted full-universe signals,
  then prepare a concrete release for approval. Verify market data/session
  contracts and actual operation; current research attestations remain false.
- Next reviewed session: 2 November 2026; reviewed calendar ends 6 November.
  Extend reviewed coverage before expiry. Do not promise automatic paper trades.
- Keep source/tests/context in GitHub, use Context Mode for bulk analysis,
  keep communication simple, and continue until real input/approval is needed.
  No production deployment, configuration change or paper/live activation is
  authorized by this context-recording request. No subagents; no credential exposure.

Older dated checkpoints below retain historical evidence. This latest decision
supersedes their statements that exit timing or the liquidity ranking awaits input.

## Current activation — PR #11 live

Mayur approved and PR #11 is merged/deployed to existing web and research cron.
Exact revision 5b9693c657f1475c1a1fd4a9c3a6a8749621eece. Web deploy
 dep-dbj1j2c9v7es738sh79g and cron deploy dep-dbj1j37b9u1s73cq1vg0 are LIVE.
UNIVERSE_SCAN_ENABLED=true is configured on cron only. Auto-deploy remains off,
with the existing schedule/compute/command retained. No paper/live execution.
PRs #9/#10 are still excluded/unapproved. Read docs/universe-scanner-activation-2026-10-31.md.

Web health and unauthenticated API protection passed; full-pool market coverage,
warm-up, persistence and an actual #11 cron invocation remain unobserved. The
manual browser smoke check could not be safely launched; do not claim it ran.
Next reviewed market session is 2 November; calendar still ends 6 November.

Accepted working ranking rule (31 October): among simultaneous valid breakouts
in the same five-minute interval, prefer highest twenty-day average traded value.
Mayur may add ranking factors later; keep policy separate from accounting and
trade management. This acceptance does not activate forward paper execution.

## Current priority — simplified automation workflow

Latest direction from Mayur on 31 October: keep engineering focused on the
liquid daily universe, full-pool setup scanning and the agreed paper trade
manager. Read docs/AUTOMATION_OBJECTIVES.md. No daily manual chart checks are
required for every stock. Do not expand diagnostics as the default next task.

PR #11 (codex/universe-wide-research) is the next concrete release proposal.
Head 874680b4860506106add2e965c66917d6d928121 passed 365 Python/API/PostgreSQL
tests and both Chromium suites in run 41219670517. It was approved and is now merged/deployed; see the activation checkpoint above. Activation requires separate approval for existing web + research
cron deploys and UNIVERSE_SCAN_ENABLED=true on the cron only. Keep the existing
schedule/compute plans, auto-deploy off and capture flag true. More full-pool
requests/runtime; no new service. No paper/live orders or PR #9 source.

PR #10 remains optional/unapproved and is not a prerequisite for universe or
scanner research work. Do not merge/deploy it automatically. PR #9 remains
inactive paper-ledger/signal development, separate from this scanner release.
This latest priority supersedes older 'next decision = PR #10' statements below.

## Resume order and source of truth
1. Read this file, docs/AUTOMATION_OBJECTIVES.md, then docs/NEXT_WORK_PLAN.md.
2. Inspect current main, open PRs #9, #10 and #11, CI and actual Render deploy/settings. Reconcile changes since this checkpoint before acting.
3. Use current source and dated evidence over older README text, chat memory or general trading memories.
4. Read docs/forward-feed-capture.md on branch codex/forward-feed-capture (PR #8); that document is not on main at this checkpoint.
5. Use Context Mode for bulk code/log processing, indexed retrieval and concise summaries. Never index credentials.

## Working agreement and approval boundary
- Continue authorized implementation/testing autonomously; stop for genuinely missing input or production approval.
- Mayur requires approval before production changes. PRs #5, #6 and #7 were approved, merged and deployed.
- Mayur approved PR #8 recorder merge/deploy, capture flag and extended cron schedule on 31 October 2026. It is merged and deployed; see the activation checkpoint below. PR #9 remains unapproved/inactive.
- No existing approval authorizes real-money orders, automatic forward paper execution or later releases. The 15:00 closure policy is agreed for implementation; deployment still needs separate approval.
- Keep source, tests, evidence and continuity in GitHub. Temporary local copies are disposable; do not depend on Mayur's computer.
- No subagents unless expressly authorized. Never expose credentials or ask for tokens in chat.
- Do not extract cockpit tokens from browser/page memory. User can unlock the UI using the existing token.
- Render auto-deploy is OFF. Documentation commits do not deploy. Before any manual deployment inspect the exact main commit and confirm only approved changes will ship.
- Current policy differs from older personal trading memories. Do not substitute NIFTY 200, two trades/day, 0.75% risk or fixed 2R targets.

## Current state at a glance
| Area | Verified state |
|---|---|
| Cockpit | Live: https://intraday-cockpit-preview.onrender.com/ |
| Web release | PR #11; commit 5b9693c657f1475c1a1fd4a9c3a6a8749621eece |
| Render web deploy | dep-dbj1j2c9v7es738sh79g — live |
| Safety | /health returned 200, mode PREVIEW_ONLY, execution_enabled=false |
| Protected comparison | Unauthenticated POST returns 401; new UI button exists |
| Paper module | Deterministic replay/failure injection; NOT automatic forward paper trading |
| Scanner coverage | Full-pool research scanner deployed; actual market-session coverage unobserved |
| Chart check | User-reported exact API/chart OHLC match for one historical RELIANCE candle |
| Forward recorder | PR #8 approved, merged and deployed on existing cron; actual weekday capture unobserved |
| Monday 2 November | Research/data-validation target; do not promise automatic paper trades |

The web deployment was rechecked through Render after PR #7. Later documentation
commits can make main newer than that live release without changing production.

## Render resources
Confirmed workspace: tea-da6sf5qfngtc73c8jfi0 (My Workspace).
- Web: srv-dbicbu1srm7s73ds0o30, intraday-cockpit-preview, Singapore, branch main, auto-deploy off.
- Research cron: crn-dbimqnbbc2fs73ap21vg, intraday-session-research, Singapore, auto-deploy off.
- Current cron schedule: */5 3-10 * * 1-5 UTC; command python -m src.run_scheduled_research; FORWARD_CAPTURE_ENABLED=true. Application gate 08:30–15:25 IST, capture gate 09:20–15:25.
- PostgreSQL: dpg-dbicbq8ae00c73bqrp6g-a, Singapore, PostgreSQL 18, 1 GB. External access closed.
- SCAN_DATABASE_URL is an internal secret. Dhan/cockpit credentials remain in existing secret mechanisms.
- No new paid service was created for paper replay or proposed capture.
- Do not touch the older suspended Oregon trading-automation service.
- Web-only releases #5–#7 did not redeploy the research cron. Inspect the cron's actual deployed source before any future release; do not assume it equals current web/main.

## Universe and calendar
- Dated evidence: research/2026-10-30/. Twenty exact official NSE sessions from 1–30 October; T-1 boundaries and source hashes preserved.
- 109 liquidity candidates: 103 research candidates, 2 identity holds, 4 exclusions. None is trading-cleared.
- Holds: TECHM, SHRIRAMFIN (corporate-action/ISIN conflicts).
- Exclusions: LIQUIDBEES, LALITHAA (low band); ESDS, WELCORP (ASM).
- HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE means research only.
- Static snapshot intended session: 2 November 2026.
- Daily premarket refresh and immutable PostgreSQL universe snapshots were deployed in PR #4.
- First eligible scheduled publication is expected Monday 2 November at 08:30 IST, subject to successful source fetches/job execution. Saturday deployment did not demonstrate it.
- Reviewed daily-refresh calendar covers target sessions 2–6 November only. Review/extend before expiry; never infer special sessions.
- From 09:15, missing same-day refresh holds instead of starting a late rebuild. Prior/advance publications do not count as today's publication.
- Authenticated /api/universe-research.csv exports the 103 research candidates with explicit source/target/mode.
- Read docs/daily-universe-refresh-2026-10-31.md and source before changing refresh/scheduling.

## Locked implemented trading and replay policy
- Capital INR 980,000; planned risk 1% inclusive of estimated costs, capped at INR 9,800.
- Long-only; one daily filled entry; no leverage.
- EMA10-close exits apply to completed post-entry candles BEFORE 1.5R too (Mayur explicitly chose to keep current code on 31 October). At 1.5 price R also request cost breakeven. No fixed 2R take profit.
- Entry window 09:45–11:30 IST. Agreed policy: all positions closed by 15:00 IST. Existing replay code still has a 15:15 request default pending implementation; costs/slippage/tick size/volume participation remain explicit assumptions.
- Costs are declared simulation assumptions, not verified broker charges or live approval.
- Later-bar entry only; stop-first ambiguity; stop changes next bar; EMA exit next open.
- IOC partial entry remainder cancelled; exit remainder stays pending. Gap losses may exceed planned risk.
- A flatten request is not a guaranteed fill. With no later executable bar, position remains unresolved.

## Cockpit and paper replay
Views: Overview, Scanner, Universe, Paper lab, Diagnostics.
- Universe separates pool/holds/exclusions; includes evidence, search/sort/pagination and authenticated CSV.
- Synthetic/uploaded diagnostics never populate stored research scanner.
- Lock clears token, private inputs/results/history; response guards reject stale sessions.
- Sources: src/paper_models.py, paper_engine.py, paper_scenarios.py, paper_store.py, paper_routes.py; src/static/cockpit.html.
- Usage and limitations: docs/paper-trading-lab.md.
- Endpoints: GET /api/paper/scenarios; POST /api/paper/replay; GET /api/paper/runs; GET /api/paper/runs/{run_id}; GET /api/paper/runs/{run_id}/trades.csv.
- Bounded finite input; one reviewed normal 2026 session; at most 25 plans/75 bars each; 2 MB body cap.
- Missing/duplicate/future/out-of-order/cross-session replay data fails closed.
- Supplied EMA/reference declarations remain unverified. This is replay, not live-feed forward trading.
- Identical normalized inputs plus engine version reuse an immutable content-addressed run.
- Costs, cash, realised partial-exit P&L and remaining-position estimated P&L reconcile.
- Paper schema initializes on first persisted replay, not deployment. Stateless mode is disclosed if no DB; DB errors safely return 503.
- Authenticated production replay persistence has NOT been demonstrated to the agent. Never claim a saved production run without verification.
- PR #6 CI: 281 Python tests and both Chromium suites passed; 14 controlled scenarios are software checks, not strategy results.

## Chart reconciliation — completed scoped check
Mayur supplied the Dhan RELIANCE NSE regular 5m chart for 30 October 2026,
09:15 IST (UTC+5:30), then ran the authenticated production comparison and pasted:

| Hypothesis/raw timestamp IST | Open | High | Low | Close | Result |
|---|---:|---:|---:|---:|---|
| OPEN / 2026-10-30 09:15 | 1170.4 | 1174.6 | 1162.7 | 1164.3 | Exact chart match |
| CLOSE / 2026-10-30 09:20 | 1163.7 | 1166.0 | 1163.1 | 1163.6 | No match |

- Provenance: user-supplied chart and user-pasted output from production UI; not an agent-observed authenticated response or retained raw broker payload.
- Supports open-labelled timestamps for ONE historical RELIANCE candle. Does not establish all-symbol/all-session conventions, daily CAS classification or live-feed health.
- PR #7 added authenticated POST /api/dhan-chart-reconciliation and Diagnostics → Reconcile RELIANCE chart → Compare with Dhan historical data.
- Source: src/dhan_chart_reconciliation.py. Fixed RELIANCE security ID 2885 and padded historical fetch.
- Report remains ONE_HISTORICAL_CANDLE_ONLY, timestamp_convention_verified=false, cas_eligibility_verified=false, forward_paper_ready=false.
- PR #7 tested source 0e33358d419d53bdb4e05067588c7be759f4e79b: 303 Python tests plus both Chromium suites passed.
- CI: https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41194685872

## Session/CAS issues still unresolved
- Earlier startup audit FETCHED_AUDITED, orders_enabled=false, timestamp_verified=false.
- Padded fetch recovered 3 sessions of 72 candles for 28–30 October; recovery came from wider requests, not synthetic fill.
- Historical scanner WAIT is not a trade.
- Existing scheduled research assumes open timestamps and 72 bars; broader assumptions stay unverified.
- Saved research/2026-10-30/cas-master-observation.json: ElgbltyClsgAuctnSsn=1 for RELIANCE; 85 pool names have 1, 18 have 0. Field interpretation/effective daily history still require verification.
- Official overview: https://www.nseindia.com/static/products-services/closing-auction-session
- Official archive: https://www.nseindia.com/static/reports/closing-auction-session-historical-data
- Broker reference: https://dhanhq.co/docs/v2/historical-data/
- Reconcile applicable NSE circulars, effective dates and per-symbol/day classification before codifying session policy. A Saturday mock-trading circular is not evidence of a normal live session.
- For a 15:15 continuous-session end, 72 bars end at 15:15 close. A 15:15 next-open flatten cannot assume a subsequent executable bar.
- Earlier flatten (for example 15:10) is a PROPOSAL only. Keep partial/unfilled exits unresolved; do not manufacture auction fills or silently alter the locked exit policy.

## PR #8 — approved recorder; activation verified 31 October
URL: https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/8
Branch: codex/forward-feed-capture
Tested source head: 81999fd81c7430070301d45dcfcd8f190a9bddac.
Documentation-only synchronization may advance the branch after this checkpoint;
recheck current head/CI before any merge.

Implemented:
- src/forward_capture.py: current-session candle observations, first-seen timestamps, source hashes, missing/stale/late markers, immutable candles and observation transactions.
- src/run_forward_capture.py: opt-in finite RELIANCE recorder; binds same-day universe revision and exact twenty reviewed reference dates; clocks observation AFTER fetch.
- src/run_scheduled_research.py: default morning behavior retained; extended capture window only if FORWARD_CAPTURE_ENABLED=true.
- tests/test_forward_capture.py: duplicate/concurrent writers, restarts, conflicts, rollback, clock/reference gates, stale/gap/reconnect cases, decimal-encoding equivalence and PostgreSQL concurrency.
- Tables: forward_research_candles and forward_research_observations; created only on actual capture.
- A revised candle rolls the whole observation back. 100 and 100.0 canonicalize equally.
- Conservative capture cutoff 15:15 is research scoping, not verified daily CAS classification or an approved flatten rule.
- NO simulated orders, fills or forward account ledger. Capture does not complete automatic paper trading.

Validation:
- 327 Python tests passed including PostgreSQL 18 concurrency; both Chromium suites passed.
- CI: https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41195680196
- Local targeted tests: 23 passed; PostgreSQL exercised in CI.
- Local Windows TestClient hangs at asyncio socketpair under sandbox; use CI evidence for API/browser coverage rather than claiming local success.
- Local pytest temporary-directory restrictions were avoided with a new workspace basetemp.

Approved request (Mayur answered on 31 October 2026; activation details below):
Merge/deploy PR #8 to the EXISTING RESEARCH CRON, enable
FORWARD_CAPTURE_ENABLED=true, and extend schedule from */5 3-6 * * 1-5 to
*/5 3-10 * * 1-5 UTC. Command unchanged. Additional invocations/runtime cost;
no additional paid service. Keep auto-deploy off. No web deploy is needed
for the recorder-only code. Those approved production settings are now active; see the exact deployment checkpoint below.
Render cron/deploy skills, settings and intended merged commit were checked;
the recorder build is live. Actual
weekday observation/persistence must be checked separately.
Rollback proposal: disable capture flag and restore previous schedule;
retain immutable evidence.

## Remaining automatic paper milestone and timing
Read docs/NEXT_WORK_PLAN.md for the work order and acceptance criteria.
Remaining: verified feed/session contracts; immutable signal-to-order binding;
separate persistent paper account/order/fill/position ledger; simulated entries,
stops, EMA/flatten exits; restart/concurrency recovery; realistic declared
cost/slippage/partial-fill handling; full-session observability and failure tests;
approved release and actual market-session validation.
Prior estimate communicated to Mayur: 2–3 focused working days for implementation,
then 3–5 live trading sessions for validation. Planning estimate only, not a
deadline, background-work commitment, or guarantee. Expand if gates uncover issues.
Monday 2 November is a data-recording/validation target, contingent on approval
and operational success, not promised automatic paper trading.
No work continues between chat turns unless an explicit automation/service does it.

## Context Mode and continuity
- Earlier handoff reported ineffective Context Mode use and zero savings; do not rewrite that historical fact.
- Context Mode IS now used for bulk source retrieval/indexing, selected excerpts and filtered test output.
- Runtime statistics estimate avoided context volume, not billing savings or immunity from chat limits.
- GitHub handoff is durable authority; Context Mode local index, chat history, node/CUA bindings and local test copies are not.
- Browser verification previously failed: in-app tab creation returned a session mismatch; native Chrome inspection stopped because current URL could not be determined safely. Do not bypass safeguards.
- User can run authenticated Diagnostics; never recover tokens from browser memory.
- New-chat starter: "Continue Intraday Trading Automation. Read docs/PROJECT_HANDOFF.md and docs/NEXT_WORK_PLAN.md first. Use Context Mode for bulk analysis. Continue until you need my input or approval; do not make unapproved production changes."

## Earlier checkpoint — inactive ledger foundation (before PR #8 activation)

31 October 2026: draft https://github.com/Mayuragarkar2020/intraday-trading-automation/pull/9
Branch codex/forward-paper-ledger, stacked on PR #8; tested source head
03106d39fd82ec00b5372e51323b54fb25d6371e. Neither PR has been approved or merged.
Read docs/forward-paper-ledger.md on that branch (not present on main).

- Added an inactive accounting library: atomic account projection and immutable
  command/result journal; idempotent retries, serialized concurrent writers,
  daily filled-entry guard, partial IOC entry cancellation, persistent partial/
  rejected exits, restart/audit recovery and exact cash/cost-basis/P&L identity.
- Orders/fills/position are logical JSON projection records; there are not yet
  separate relational order/fill tables. Review projection retention/growth
  before activation. Pin the eventual runtime account ID to prevent resets.
- Caller-supplied source/signal declarations are NOT verified feed bindings.
  No runtime imports the ledger; no API, cron, executor, broker-order call or
  production DB write was added. Session/source gates, breakeven/EMA10 execution
  and actual-market validation remain outstanding. Automatic paper NOT READY.
- Local targeted tests: 110 passed, 2 PostgreSQL-only checks skipped.
- Exact-head CI: 372 Python/API/PostgreSQL tests passed; both Chromium suites
  passed. https://github.com/Mayuragarkar2020/intraday-trading-automation/actions/runs/41210571449
- Same-day production recheck: cockpit health 200, PREVIEW_ONLY,
  execution_enabled=false; web still 4504ecfa5325aa1bc85ab2120954d6b05c319b58.
  Cron still 0ce3cdb340d268c397f7adbd905a30a5f4e8edb7,
  deploy dep-dbiqu8oae00c73ceuksg; schedule */5 3-6 * * 1-5 UTC.
  Both auto-deploy settings off. No production changes were made.
- PR #8's recorder-only activation request remains pending. Approval of #8
  must not include #9. If #8 is approved, merge/deploy only recorder source
  plus documentation; do not deploy the ledger branch. Keep #9 draft until
  trusted session/signal/executor integration is reviewed and tested.
- This main-branch documentation checkpoint does not merge either proposal
  or deploy anything. Before the next release recheck actual main and cron.

## Current activation checkpoint — supersedes earlier pending statements

Mayur approved PR #8 on 31 October 2026. It is merged and deployed to the existing
research cron: 69a0c31ec3b4a8a492414b09b8422f774bc50a96,
dep-dbivtvnf3r2c73ej3l7g (live). Capture flag true, extended schedule and auto-deploy
off were verified. One successful Saturday smoke run returned MARKET_CLOSED
with execution_enabled=false. Actual weekday capture/persistence remains
unobserved. Read docs/forward-capture-activation-2026-10-31.md for evidence,
including the environment-update intermediate build and SQL access limitation.
The web remains at PR #7. PR #9 remains draft/unapproved/undeployed; no forward
paper executor or broker ordering was activated. Earlier pending statements
in historical checkpoints describe the earlier time, not current authorization.

## Latest inactive-source checkpoint — receipt-bound signals

PR #9 is now based on main and includes both the accounting ledger and an
inactive research signal journal. Exact tested head:
1a529075c68e43bb2e40c207aaadf0b1d5b0805c. Full CI: 390 Python/API/PostgreSQL
tests plus both Chromium suites passed in run 41213273260. Local targeted
checks: 127 passed, 3 PostgreSQL-only skipped. Read docs/forward-research-signal.md
on codex/forward-paper-ledger; no runtime imports either new module.

The new journal reads committed recorder observations and the original universe
revision, checks hashes, dates, calendar and first-seen timeliness, derives
scanner inputs and freezes full normalized input/result evidence and post-scan
known_at. Conflicting recomputation and reconnect/backfill signals hold. It
always reports forward_paper_ready=false and execution_enabled=false because
reference-price provenance and session contracts are still unverified.
No ledger/order adapter, simulator runtime or production integration is added.

Added dated official NSE CAS evidence: RELIANCE appears in the 30 October
CAS archive. Read docs/session-contract-checkpoint-2026-10-31.md and
research/2026-10-30/cas-session-observation.json. This narrows that day's CAS
uncertainty; it does not certify future dates, all reference days, or broker
candle labels. Originals 73845/74466 remain unread via available PDF retrieval.
Next user-dependent evidence: independent Dhan regular five-minute closing
candle view for RELIANCE on 30 October (last and preceding candle, time/OHLC).
No revised flatten time is approved. Keep open/partial exposure unresolved.

## Latest chart input — closing screenshots received

Mayur supplied the requested two Dhan RELIANCE NSE five-minute screenshots
on 31 October 2026. Visible labels/OHLC on 30 October (IST):
- 15:05: O 1161.30, H 1163.50, L 1160.50, C 1163.30.
- 15:10: O 1163.30, H 1163.90, L 1158.40, C 1159.00.
15:10 appears as the last visible chart candle. No closing-candle API match
has yet been observed. Raw screenshots are in the chat; exact transcription
is in research/2026-10-30/reliance-closing-chart-observations.json.

PR #10 (codex/closing-chart-comparison) prepares a separate web-only authenticated
comparison for these two fixed observations, with a Diagnostics button and
raw target-day timestamp metadata. It preserves the original 09:15 comparison.
It does not deploy PR #9, modify the cron, certify session/CAS/forward readiness
or change exit timing. Inspect current head/CI and obtain separate approval
before merge/deploy to the existing web service only. User input fulfilled the
screenshot request; it did not authorize a new production release.

PR #10 exact tested source: e89b32bbaf72ab1ab4334caf795b0c84579e2141.
CI run 41214406739: 346 Python/API/PostgreSQL tests and both Chromium suites
passed. Local pure checks: 39 passed, 2 API tests deselected for the known
Windows TestClient sandbox limitation. The tests use fixtures, not actual
broker data. PR #10 remains OPEN/UNAPPROVED/UNDEPLOYED. Proposed release scope:
existing web service only; no cron deployment/config change and no PR #9
ledger/signal source. After approval and verified deploy, the user can run
Diagnostics → Compare closing candles with Dhan and retain the actual result.

## Full-universe scanner source checkpoint (PR #11)

The existing saved 109-candidate snapshot selects 103 research candidates,
two identity holds and four exclusions. The new runner sends each selected
stock through the existing detector; narrow/unknown bands and existing holds
cannot become scan successes. Tests use synthetic broker prices, not actual
103-symbol broker coverage or a throughput demonstration.

Reference history is cached per universe revision/security ID, warmed before
09:40, then each setup cycle fetches current candles. Complete/incomplete
coverage is persisted; invalid/stale data and auth/429 failures visibly hold.
The cockpit latest-scan path reads full-pool cycles when present, preserving
the existing RELIANCE fallback and excluding warm-up from setup displays.
No public order endpoint or trade-manager logic is changed. Research timestamp/
session assumptions and normal 72/75-bar reference shapes do not become
execution clearance. The reviewed calendar still ends on 6 November.

Production is unchanged by this source work. Both auto-deploy settings and
the existing cron schedule were rechecked. Local targeted validation: 62 passed,
2 PostgreSQL-only skipped, 1 API test deselected for known Windows TestClient
sandbox behaviour; full CI passed above. Read docs/universe-wide-scanner.md
on codex/universe-wide-research for exact activation scope and limits.

## Latest inactive-source checkpoint — accepted ranking

PR #9 now includes versioned liquidity ranking and prospective paper-entry
reservations. Head 91bd84736364ea1cc420fd21184b57db2b1033dd. Local targeted checks:
79 passed, 3 PostgreSQL-only skipped. Exact-head CI run 41222564313 passed
447 Python/API/PostgreSQL tests and both Chromium suites. Live-source smoke
was skipped; these checks do not establish actual broker/market coverage.
Read docs/paper-entry-selection.md on codex/forward-paper-ledger. Ranking evidence
and the order commit atomically; retries/concurrency preserve one reservation.
Selection after an interval cannot backdate fills into it. Current research
sources remain unverified and held. No runtime imports or production changes.
PR #9 remains draft/unapproved/undeployed; PR #10 remains deferred.

Exit policy resolved: Mayur requires all positions closed by 15:00 IST.
Implement this on the inactive paper branch with prospective fills and visible
unresolved exposure on failure; existing code and production remain unchanged.
