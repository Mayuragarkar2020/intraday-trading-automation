# Next work plan — Phase1 round2 review, NOT Phase2

[READ_CODE] Latest universe contract:automatic all10agreed gates;manualT-1 CSV withband-only admission andpersistentidentifier;capacity75=50automatic+25manual. D030..036 supersede old same-filter/manual20cap/25-systematic and same-day-add assumptions. See UNIVERSE_AND_POOL_CONTRACT.md.

[READ_CODE]2026-11-01 approval update: Mayur answered “all yes” to five round2 questions. D-024..029 approved filter/width scope,maxdistance,tick defaults,stop-limit semantics,override bounds and conservative stop model. Exact buffer calibration,clean checkout baseline and Phase2 authorization remain pending. No application/production change.

[READ_CODE] Source main79a2d3086c8aea660dc31068e2758db1f7332808; docs proposal stacks on round1 PR18. Current strategy/decisions in docs/design/README.md and docs/audit/DECISIONS.md supersede older three-bar/no-C0, next-close/receipt-cutoff defaults.
[ASSUMED] Actual Render state **unverifiable by Codex**. Historical documentary checkpoint: webPR14 ceaaf577c8e30e4713da19176828b1b43b3a0226; research cronPR12 6d6e8152da96da2c575a59e0b980448b774d059b. No current runtime proof. Prior main CI539/both browsers is historical CI-reported, not this session RAN_TEST.
[ASSUMED] Local baseline UNKNOWN; Mayur will supply clean checkout. No clone/test retry this round. Review baseline instructions and explicit error uncertainty before Phase2.
[ASSUMED: design choice] Single Phase2 base is origin/main/PR14 HumanChoicePaperLedger foundation. PR13/15 stay open, reference-only; no merge/closure. Any selective reuse requires explicit review/tests/provenance.
[ASSUMED: constraint] PREVIEW_ONLY; no broker/real-money path,secrets,deploy,Render/cron changes. Long-only,capital980000,planned cost-inclusive L-Q risk<=9800,one filled entry/day,no leverage,<=5 arms; scan09:15–14:35,entry candle START<14:30,closure15:00; protected legacy files untouched.

## Next checkpoint

[ASSUMED] Review round2 docs and numbered open questions. Phase2 requires Mayur's explicit design approval and verified exact-source baseline in supplied clean checkout. No implementation/deployment approval is bundled. Buffer/stop parameters remain placeholders until empirical analysis; afternoon efficacy not validated.
[ASSUMED] Detailed future tests/real-data analysis are in docs/design/REPLAY_ANALYSIS_AND_TEST_PLAN.md. Reviewed calendar remains through6November only, not extended here.

## Restored acceptance checks — Phase2 and later test targets ONLY

[ASSUMED: future target] Human confirmation required; selecting nothing produces no trade. Preserve exact selected stock/setup/proposal/override; advisory ranking cannot introduce unconfirmed stocks.
[ASSUMED: future target] C0 closes STRICTLY above preceding3highs; equality/one-tick boundaries; four contiguous current bars; tick T/S from C0/prior4; C0 filters/prior3width defaults audited.
[ASSUMED: future target] Reject stale/revised/wrong-session/unknown tick/source or already-broken selection;15min expiry; pre-entry low<=S invalidates; no pre-confirmation or backdated evidence; cutoff based on exchange open with receipt stale guard.
[ASSUMED: future target] Cost-inclusive L-Q risk literal9800,capital980000,long-only/no leverage,one daily filled entry and five-arm literal caps are mutation-protected; frozen limit formula has independent numeric fixtures. Trigger-risk comparison is journaled.
[ASSUMED: future target] Same-bar resting trigger/fill, O>L GAPPED_THROUGH with zero fill/no chase/no automatic re-arm, exact final14:25 vs ineligible14:30 candle boundaries, all-or-nothing/anomalies.
[ASSUMED: future target] Two arms same candle deterministic ADV20 then securityID; retries/concurrent writers/restart produce one fill; DB unique fill/five slots; atomic bracket/other-arm cancellation/outbox; pending/open/filled-day prevents invalid replacement/arming.
[ASSUMED: future target] Protective S/Q resting fills, gap belowQ/low-cross ambiguity STOP_NOT_FILLED, no assumed cap on realized gap loss, stop-cancel-confirm-exit races cannot create short exposure; same-candle protective loss pessimism.
[ASSUMED: future target] Initial SL immutable;5m EMA exit before1.5R; BE modification next bar and fee/stop-limit aware; no target; halt/nontradable/rejected exits remain pending; early flatten and persistent15:00 breach/late recovery.
[ASSUMED: future target] Feed/DB/worker outage recovery, missed bars, authoritative event/projection reconciliation, no synthetic flat/fill, restart with multiple arms, independent clock/supervision and Telegram failures remain visible.
[ASSUMED: future target] Immutable decision/fill/stop journal reconciles cash/cost/P&L/netR; selected/unselected/cancelled/hidden shadow cohorts; original vs override, source/config/rule/model/time buckets, MFE/MAE uncertainty/excess-loss tagging.
[ASSUMED: future target] ManualT-1CSV/band-only admission/identifier lineage;50auto25manualranking/availablehistory/N0andindicatorholds;persistence/suspend-revalidate/reminder; hidden postcutoff setups never cockpit/push; chart symbol M&M encoding/link only.
[ASSUMED: future target] Authentication, stale-tab/double-click/lock-clearing/mobile browser behavior; Telegram alive/qualified/armed/cancelled/entered/exited/critical/heartbeat events and outbox idempotence.
[ASSUMED: later validation] Separate PG constraint/concurrency and browser/service tests only with prerequisites; exact commands/counts/durations; no pure test labelled PG proof. No-trade observation of actual75-slot/cohort load,p95<=60s for confidence/further scale;no throughput measurement yet. Genuine source/market/session validation precedes any release request; stop-failure buffer analysis and future broker preflight are not already validated.

[READ_CODE] Latest future acceptance additions are in REPLAY_ANALYSIS_AND_TEST_PLAN.md:manual stock outsideautomaticprice/history/liquiditygates,100manualtop25,T-1serverboundary,nosamedayentry,label throughout,availablehistorylookback,cohortdedup,short-historyindicatorholds.
[ASSUMED] Open choices:T-1calendar vs trading-session interpretation;zero-completed-session IPO liquidity rank;IPOshort-historysetup/RVOLwarm-up and future armedtie fallback. No Phase2 begun.
