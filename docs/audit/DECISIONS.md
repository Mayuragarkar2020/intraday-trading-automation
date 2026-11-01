# Decision register

[READ_CODE] Created during Phase 0 on 2026-11-01; approval attribution below refers to Mayur's current request, not inferred consent from old chats.
[ASSUMED] Rationale paraphrases the stated intent; it does not add implementation permission. All implementation links below identify existing partial/conflicting code or explicitly pending design.

| ID | Date | Decision | Who decided | Rationale | Status | Evidence / implementation |
|---|---|---|---|---|---|---|
| P0-D-001 | 2026-11-01 | [ASSUMED: user requirement] Selection means the user confirmed a setup. | Mayur | User-defined meaning; older SELECTED_HELD conflicts. | approved | [READ_CODE] src/paper_choice.py; Phase 1 design pending |
| P0-D-002 | 2026-11-01 | [ASSUMED: user requirement] Confirming a selection arms the stock. | Mayur | No additional manual handoff step. | approved | [READ_CODE] src/paper_choice.py (conflict); Phase 1 pending |
| P0-D-003 | 2026-11-01 | [ASSUMED: user requirement] Hard cap: five simultaneously armed stocks. | Mayur | Bound operational load and exposure candidates. | approved | [READ_CODE] Phase 1 pending |
| P0-D-004 | 2026-11-01 | [ASSUMED: user requirement] First armed stock to break out takes the single daily entry. | Mayur | Only user-confirmed candidates may compete. | approved | [READ_CODE] src/forward_paper_ledger.py (partial); Phase 1 pending |
| P0-D-005 | 2026-11-01 | [ASSUMED: user requirement] On a fill, cancel all other armed stocks atomically and alert the user. | Mayur | Prevent multiple competing entries. | approved | [READ_CODE] Phase 1 pending |
| P0-D-006 | 2026-11-01 | [ASSUMED: user requirement] No new arming after the daily fill. | Mayur | Preserve one filled entry per day. | approved | [READ_CODE] src/paper_choice.py (single-choice restriction only) |
| P0-D-007 | 2026-11-01 | [ASSUMED: user requirement] Same-candle ties: highest 20-day average traded value. | Mayur | User-selected tie rule; no alternative proposed. | approved | [READ_CODE] src/paper_choice.py (advisory sort only); Phase 1 pending |
| P0-D-008 | 2026-11-01 | [ASSUMED: user requirement] Latest entry is 14:30 IST; measurement convention remains a Phase 1 proposal. | Mayur | User-set cutoff; do not reinterpret candle label as fill time. | approved | [READ_CODE] src/forward_paper_ledger.py (11:30 conflict) |
| P0-D-009 | 2026-11-01 | [ASSUMED: user requirement] Scanner stops after 14:35 IST. | Mayur | User-set scan window ends at 14:35. | approved | [READ_CODE] src/universe_scanner.py (11:30 conflict) |
| P0-D-010 | 2026-11-01 | [ASSUMED: user requirement] Every entry is a limit order. | Mayur | Bound the accepted entry price. | approved | [READ_CODE] src/paper_engine.py (conflict); src/forward_paper_ledger.py (limit guard) |
| P0-D-011 | 2026-11-01 | [ASSUMED: user requirement] Open beyond the allowed limit cancels that setup as GAPPED_THROUGH, with no fill. | Mayur | No gap chasing. | approved | [READ_CODE] src/paper_engine.py (conflict); Phase 1 pending |
| P0-D-012 | 2026-11-01 | [ASSUMED: user requirement] Never chase with a market entry or reprice the entry order. | Mayur | Preserve the confirmed entry envelope. | approved | [READ_CODE] src/paper_engine.py (conflict); Phase 1 pending |
| P0-D-013 | 2026-11-01 | [ASSUMED: user requirement] Never re-arm automatically. | Mayur | A cancelled setup needs a new explicit user decision. | approved | [READ_CODE] Phase 1 pending |
| P0-D-014 | 2026-11-01 | [ASSUMED: user requirement] Post-14:30 setups through 14:35 are hidden from cockpit and alerts but stored for shadow analysis. | Mayur | Separate trading eligibility from research evidence. | approved | [READ_CODE] Phase 1 pending |
| P0-D-015 | 2026-11-01 | [ASSUMED: user requirement] All positions closed by 15:00 IST; unfilled exposure must remain visible. | Mayur | User's closure requirement; no manufactured flat state. | approved | [READ_CODE] src/paper_models.py; src/paper_trade_management.py |

[ASSUMED: Codex proposal; NOT approved] P-001: archive src/run_daily.py and root render.yaml together after checking external references. Do not delete yet; neither file was changed. Evidence: [READ_CODE] run_daily exits 2 with NOT_READY; render.yaml invokes it.
[ASSUMED: Codex proposal; NOT approved] P-002: handle mid-position faults as visible unresolved exposure plus protective recovery; do not promise flat during feed/DB outages, halts or circuits. Detailed mechanics await Phase 1.


## CORRECTION / supersession — 2026-11-01, Phase 1 test checkpoint

[READ_CODE] Phase 0 assigned fifteen D identifiers before Mayur supplied the current authoritative seventeen-ID register. Historical table identifiers above are now explicitly P0-D-001..015 to avoid collisions; their text and historical approval provenance are retained. Current D-001..017 below are approved by Mayur in this session's request. This is a recorded namespace correction, not a silent change in trading rules.
[ASSUMED] Exact implementation/config values still described as proposals in a decision are not automatically approved. No design or application implementation was added at this checkpoint.
[ASSUMED] The historical archive suggestion P-001 is superseded by Mayur's current instruction: do not archive or edit src/run_daily.py or root render.yaml. Neither path was touched. Reference inventory/dashboard checklist remain pending.

| ID | Date | Decision | Who decided | Rationale | Status | Implementing links / evidence |
|---|---|---|---|---|---|---|
| D-001 | 2026-11-01 | [ASSUMED: user requirement] Selected means a confirmed setup; armed means watching for breakout; confirmation arms it. | Mayur | User-defined selection contract. | approved | [READ_CODE] docs/design/LIFECYCLE_AND_ATOMICITY.md; design proposal only, implementation pending |
| D-002 | 2026-11-01 | [ASSUMED: user requirement] Hard cap five simultaneous arms; first breakout takes daily entry; other arms cancelled atomically as SUPERSEDED_BY_FILL with alert; no arming after fill. | Mayur | Bound exposure and preserve human candidate selection. | approved | [READ_CODE] docs/design/LIFECYCLE_AND_ATOMICITY.md; design proposal only, implementation pending |
| D-003 | 2026-11-01 | [ASSUMED: Mayur round2 amendment] Same-candle ties use highest frozen20-day average traded value, then ascending security ID; version ARMED_BAR_ADV20_SID_V1. | Mayur | Approved deterministic liquidity ranking. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; docs/design/LIFECYCLE_AND_ATOMICITY.md; design only |
| D-004 | 2026-11-01 | [ASSUMED: user requirement] Latest entry 14:30; scanner ends 14:35; later setups hidden from cockpit/alerts but shadow-recorded. | Mayur | Separate research from trading eligibility. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| D-005 | 2026-11-01 | [ASSUMED: Mayur round2 amendment] AMENDED round2: C0 five-minute close strictly above prior3highs establishes signal; confirmation arms resting stop-limit intent and entry can fill in that same later eligible trigger candle. C0+15min lifetime; pre-entry low<=S invalidates. T=highC0+one tick and S=minLow4-one tick are now approved defaults (Mayur2026-11-01). | Mayur | Prevent look-ahead and pre-decision fills. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; docs/design/LIFECYCLE_AND_ATOMICITY.md; design only |
| D-006 | 2026-11-01 | [ASSUMED: Mayur round2 amendment] Resting stop-limit entry; placeholder L=ceil_tick(T+max(0.15%T,3ticks)); final buffer selected from replay evidence. Open>L cancels GAPPED_THROUGH, no market chase or repricing. Mayur confirmed stop-limit rather than plain-limit on2026-11-01. | Mayur | Bound fill price; exact formula not yet approved. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; docs/design/LIFECYCLE_AND_ATOMICITY.md; design only |
| D-007 | 2026-11-01 | [ASSUMED: user requirement] No automatic re-arm after GAPPED_THROUGH; manual reselection allowed only while setup valid and before cutoff. | Mayur | Retain explicit user control. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| D-008 | 2026-11-01 | [ASSUMED: user requirement] Hybrid universe: provisional previous evening, revalidate before 09:15, scan only final validated list; failure/late revalidation means scan nothing new. | Mayur | Fail closed on uncertain eligibility. | approved | [READ_CODE] docs/design/SETUP_AND_UNIVERSE.md; design proposal only, implementation pending |
| D-009 | 2026-11-01 | [ASSUMED: user requirement] Same setup rules 09:15–14:35; identify old-window warm-up assumptions, tag time buckets; afternoon results are not validated. | Mayur | Separate approved intent from unproven performance. | approved | [READ_CODE] docs/design/SETUP_AND_UNIVERSE.md; design proposal only, implementation pending |
| D-010 | 2026-11-01 | [ASSUMED: user requirement] Telegram alerts with daily alive message and visible unreachable-channel behavior. | Mayur | Make alert failure observable. | approved | [READ_CODE] docs/design/JOURNAL_ALERTS_RECOVERY.md; design proposal only, implementation pending |
| D-011 | 2026-11-01 | [ASSUMED: user requirement] Untriggered arms auto-cancel at cutoff as CUTOFF_REACHED and alert. | Mayur | No stale armed state beyond entry window. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| D-012 | 2026-11-01 | [ASSUMED: user requirement] Paper fills are all-or-nothing; partial suggestions are anomalies. | Mayur | Approved paper execution simplification. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| D-013 | 2026-11-01 | [ASSUMED: user requirement] Circuit/halt with exposure: hold, alert immediately, exit first valid tradable price; never invent a fill. | Mayur | Acknowledge non-tradable exposure. | approved | [READ_CODE] docs/design/JOURNAL_ALERTS_RECOVERY.md; design proposal only, implementation pending |
| D-014 | 2026-11-01 | [ASSUMED: user requirement] Open-position downtime over about ten minutes triggers alert/flag; recover flat at next valid price; define independent detection/restart supervision. | Mayur | No fictitious outage exit; supervision remains unverified. | approved | [READ_CODE] docs/design/JOURNAL_ALERTS_RECOVERY.md; design proposal only, implementation pending |
| D-015 | 2026-11-01 | [ASSUMED: user requirement] Database event journal is authoritative; JSON account projection derived/rebuildable; reconcile disagreements on restart. | Mayur | Recover from authoritative events. | approved | [READ_CODE] docs/design/JOURNAL_ALERTS_RECOVERY.md; design proposal only, implementation pending |
| D-016 | 2026-11-01 | [ASSUMED: user requirement] About twenty persistent manual catalysts until removed; daily revalidation, visible suspension on failure, thirty-day reminder. | Mayur | Controlled persistent discretionary additions; exact cap to be specified. | approved | [READ_CODE] docs/design/SETUP_AND_UNIVERSE.md; design proposal only, implementation pending |
| D-017 | 2026-11-01 | [ASSUMED: user requirement] Entry/SL overrides allowed within tick, long-side SL, cost-inclusive INR9,800 risk and freshness limits; original and override journaled. | Mayur | Validated user discretion. | approved | [READ_CODE] docs/design/LIFECYCLE_AND_ATOMICITY.md; design proposal only, implementation pending |


## Phase 1 engineering proposals — 2026-11-01

[READ_CODE] D-001..017 remain approved by Mayur at intent level. The values/mechanics below are Codex proposals, not approved decisions. Historical P-001 archive suggestion remains superseded by Mayur's explicit do-not-edit/archive instruction.

| ID | Date | Proposal | Who decided | Rationale | Status | Design link |
|---|---|---|---|---|---|---|
| P-003 | 2026-11-01 | [ASSUMED] Stop-limit buffer=max(0.15% of trigger,3 effective ticks), rounded up; next-candle-close/AON model and conservative ambiguity guards | Codex proposal | Bound modeled price without optimistic gap chasing | superseded | docs/design/TIME_AND_EXECUTION.md |
| P-004 | 2026-11-01 | [ASSUMED] Entry receipt timestamp<=14:30; strict primary visibility before cutoff; late receipt never backdated | Codex proposal | Precise cutoff under source-label/latency ambiguity | superseded | docs/design/TIME_AND_EXECUTION.md |
| P-005 | 2026-11-01 | [ASSUMED] TTL15min; latest validation candle90s and quote5s; preview quantity re-sized at trigger | Codex proposal | Avoid stale handoffs | proposed | docs/design/LIFECYCLE_AND_ATOMICITY.md |
| P-006 | 2026-11-01 | [ASSUMED] Systematic top100 plus up to20 filtered persistent catalysts; membership cap includes suspended; no late primary final universe | Codex proposal | Bounded auditable coverage; fail closed | superseded | docs/design/SETUP_AND_UNIVERSE.md |
| P-007 | 2026-11-01 | [ASSUMED] Authoritative event unique daily-fill index, five numbered arm slots, session lock/fencing and atomic fill/cancel/outbox | Codex proposal | Database-backed guarantees, restart recovery | proposed | docs/design/LIFECYCLE_AND_ATOMICITY.md |
| P-008 | 2026-11-01 | [ASSUMED] Independent watchdog30s; warning90s; critical600s; Telegram alive08:55, absence09:05 visible; new-entry hold when alert channel unhealthy | Codex proposal | Explicit supervision and outage observability | proposed | docs/design/JOURNAL_ALERTS_RECOVERY.md |
| P-009 | 2026-11-01 | [ASSUMED] Protected shadow cohorts and optional explicitly extended-hours research model; never counted as primary trades | Codex proposal | Honest selection comparisons without hidden cutoff violation | proposed | docs/design/JOURNAL_ALERTS_RECOVERY.md |


## Round2 amendment record — 2026-11-01

[READ_CODE] Explicit correction: current D-003/D-005/D-006 rows amended from Mayur's round2 request; previous text retained below as historical R1 records. P-003 next-close bundle, P-004 receipt-cutoff and P-006 top100 initial pool superseded, not retroactively approved. Original user-approved hard caps remain unchanged.
[ASSUMED] Mayur approved the new direction; exact tick/filter/distance/override and buffer calibration defaults remain “proposed, awaiting Mayur” as requested.0.15%/1.0% are placeholders, not selected by evidence.

| ID | Date | Decision | Who decided | Rationale | Status | Evidence / design |
|---|---|---|---|---|---|---|
| D-018 |2026-11-01|[ASSUMED: user-approved] Fill candle START<14:30; receipt time only staleness/knowledge guard, not cutoff eligibility |Mayur|Avoid receipt-time rejection of eligible exchange window|approved|[READ_CODE] docs/design/TIME_AND_EXECUTION.md#cutoff-by-exchange-candle-window|
| D-019 |2026-11-01|[ASSUMED: user-approved] Protective resting stop model uses S or allowable gap open with adverse slippage; delayed-close only degraded-feed fallback; stop-limit no-fill cases override assumed fills |Mayur|Distinguish protection from optimistic candle-close fallback|approved|[READ_CODE] docs/design/TIME_AND_EXECUTION.md#protective-stop-limit-and-stop_not_filled|
| D-020 |2026-11-01|[ASSUMED: user-approved] Initial25–50 systematic pool plus catalysts; scale only after measured complete-sweep p95<=60s in no-trade observation |Mayur|Evidence-based capacity|approved|[READ_CODE] docs/design/SETUP_AND_UNIVERSE.md#hybrid-universe-and-pool|
| D-021 |2026-11-01|[ASSUMED: user strategy] Logical no-target bracket; failed stop enters STOP_NOT_FILLED,critical alert and next valid marketable recovery; realized loss may exceed9800 |Mayur|No fabricated protective fill or max-loss claim|approved|[READ_CODE] docs/design/TIME_AND_EXECUTION.md; stop-limit1% remains placeholder|
| D-022 |2026-11-01|[ASSUMED: user strategy] Size with worst modeled L minus stop LIMIT Q plus fees; also report risk on stop trigger S |Mayur|Risk includes bounded protective-limit price|approved|[READ_CODE] docs/design/TIME_AND_EXECUTION.md#sizing-on-stop-limit-overrides-and-precedence|
| D-023 |2026-11-01|[ASSUMED: user constraint] Broker-neutral intents only; no broker order code/endpoint/credential/client library; pre-live official documentation checks and cancel-confirm-exit race design |Mayur|No premature live coupling or duplicate sell|approved|[READ_CODE] docs/design/REPLAY_ANALYSIS_AND_TEST_PLAN.md; LIFECYCLE_AND_ATOMICITY.md|
| P-010 |2026-11-01|[ASSUMED] Phase2 single base origin/main79a2d308 (PR14 foundation); PR13/15 open reference-only |Codex proposal|Smallest baseline with exact human-choice guard|proposed|docs/design/LIFECYCLE_AND_ATOMICITY.md|
| P-011 |2026-11-01|[ASSUMED] Keep C0 filters and prior3width denominator close(-1C); max(T-S)/T2.5%; one-tick default buffers |Codex proposed defaults awaiting Mayur|Explicit strategy item7 defaults|superseded|docs/design/SETUP_AND_UNIVERSE.md|
| P-012 |2026-11-01|[ASSUMED] Override deltas max(0.10%T0,2ticks), still above highC0/below minLow4; separate overridden cohort |Codex proposal|Bound discretion to signal provenance|superseded|docs/design/TIME_AND_EXECUTION.md|
| P-013 |2026-11-01|[ASSUMED] Conservative low<Q protective no-fill model with continuous-touch sensitivity; candle-age90s/quote5s/AON-capacity policy |Codex proposal|Expose unknown path/liquidity and delayed detection|proposed|docs/design/TIME_AND_EXECUTION.md; REPLAY_ANALYSIS_AND_TEST_PLAN.md|

[READ_CODE] Prior round1 rows, unchanged in meaning; historical only (status superseded here, not new approvals):
| R1-D-003 | 2026-11-01 | [ASSUMED: user requirement] Same-candle ties use highest 20-day average traded value. | Mayur | Approved deterministic liquidity ranking. | superseded | [READ_CODE] docs/design/LIFECYCLE_AND_ATOMICITY.md; design proposal only, implementation pending |
| R1-D-005 | 2026-11-01 | [ASSUMED: user requirement] Detect breakout on five-minute close; model fill in following candle; define cutoff against open labels/close times. | Mayur | Prevent look-ahead and pre-decision fills. | superseded | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| R1-D-006 | 2026-11-01 | [ASSUMED: user requirement] Entries are stop-limit, with buffered limit about 0.1–0.2% or a few ticks; exact versioned formula is a Codex proposal; unfillable gap cancels as GAPPED_THROUGH; no market chase/repricing. | Mayur | Bound fill price; exact formula not yet approved. | superseded | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |


## Approval record — Mayur “all yes”,2026-11-01

[READ_CODE] Mayur approved all five numbered round2 review answers in PR19's review context. This supersedes awaiting-confirmation wording for those items only; D-005/D-006 current rows updated accordingly and P-011/P-012 superseded by user decisions below. Prior log/history retained. P-013's freshness/capacity details remain proposed; only its conservative stop-rule portion is approved by D-029. No Phase2,final buffer calibration,production action or additional hosting approval was given.

| ID | Date | Decision | Who decided | Rationale | Status | Evidence / design |
|---|---|---|---|---|---|---|
| D-024 |2026-11-01|[READ_CODE: user approval] C0 EMA10>EMA20,close above both/sessionVWAP,RVOL>=1.2,completed15m trend retained; prior3width<=2.5% divided by close(-1C).|Mayur|Explicit “all yes” to corresponding round2 question|approved|docs/design/SETUP_AND_UNIVERSE.md|
| D-025 |2026-11-01|[READ_CODE: user approval] Maximum accepted trigger-to-stop distance(T-S)/T<=2.5%; historical sensitivity still required.|Mayur|Explicit “all yes” to corresponding round2 question|approved|docs/design/TIME_AND_EXECUTION.md|
| D-026 |2026-11-01|[READ_CODE: user approval] Default T=highC0+one effective tick; S=minLow(C0,prior3)-one effective tick.|Mayur|Explicit “all yes” to corresponding round2 question|approved|docs/design/TIME_AND_EXECUTION.md|
| D-027 |2026-11-01|[READ_CODE: user approval] Entry/protective order semantics are stop-limit, not plain limit; buffer values remain placeholders.|Mayur|Explicit “all yes” to corresponding round2 question|approved|docs/design/TIME_AND_EXECUTION.md|
| D-028 |2026-11-01|[READ_CODE: user approval] Entry/SL override absolute deltas<=max(0.10%T0,2ticks),T>=highC0+tick,S<=minLow4-tick,with tick/freshness/risk/distance checks and own cohort.|Mayur|Explicit “all yes” to corresponding round2 question|approved|docs/design/TIME_AND_EXECUTION.md|
| D-029 |2026-11-01|[READ_CODE: user approval] Conservative primary protective OHLC model: low<Q or open<Q means STOP_NOT_FILLED; bound valid fills by Q and full capacity,report continuous-touch alternative sensitivity.|Mayur|Explicit “all yes” to corresponding round2 question|approved|docs/design/TIME_AND_EXECUTION.md|
