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
| D-016 | 2026-11-01 | [READ_CODE: Mayur amendment] AMENDED:Manual discretionary stocks persist until removal;T-1 CSV only,visible user identifier,band-only admission(no2%/5%),daily band revalidation/visible suspension,30day reminder;old20membership cap superseded. | Mayur | Controlled persistent discretionary additions; exact cap to be specified. | approved | docs/design/UNIVERSE_AND_POOL_CONTRACT.md |
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
| D-020 |2026-11-01| [READ_CODE: Mayur amendment] AMENDED:Initial scanning capacity75,up to50automatic+25manual,cohort liquidity ranking and available-history manual average;use fewer if unavailable. Measured no-trade complete-sweep p95<=60s remains validation/further-scale gate,not an already measured claim. |Mayur|Evidence-based capacity|approved| docs/design/UNIVERSE_AND_POOL_CONTRACT.md |
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


## Universe/pool definition checkpoint —2026-11-01

[READ_CODE] Mayur requested proper definition of the stock universe and scanning pool. This authorizes documentation refinement,not approval of the exact proposal below. Existing liquidity thresholds were reread in config/universe.yaml and screening.py;they are current defaults,not empirically certified strategy choices. No previous approved decision reopened.
| ID | Date | Decision | Who decided | Rationale | Status | Evidence/design |
|---|---|---|---|---|---|---|
| P-014 |2026-11-01|[ASSUMED] Initial systematic N25 within approved25–50 range;any increase gated by measured no-trade complete-sweep p95<=60s.|Codex proposal|Freeze an explicit initial observation size.|superseded|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| P-015 |2026-11-01|[ASSUMED] Automatically select eligible,data-ready U names by20D mean traded value descending,numeric security ID ascending;show readiness skips and all eligible-but-unscanned names.|Codex proposal|Separate liquidity/capacity selection from setup detection;no hidden sampling.|superseded|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| P-016 |2026-11-01|[ASSUMED] Scanning pool is deduplicated systematic UNION eligible manual catalysts;manuals do not bypass filters or silently consume systematic slots;benchmark total scanned load.|Codex proposal|Preserve user catalyst coverage/provenance with honest counts.|superseded|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| P-017 |2026-11-01|[ASSUMED] Freeze systematic membership preopen;no automatic intraday rotation;explicit catalyst revisions and visible data/status holds retain expected coverage denominator.|Codex proposal|Reproducibility and no silent degradation.|superseded|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
[ASSUMED] Ordinary-equity classification/readiness/count/freeze details remain proposed pending Mayur;no Phase2 or operational activation.


## Latest Mayur automatic/manual amendment —2026-11-01

[READ_CODE] Mayur expressly agreed all automatic gates and changed manual admission,pool quota/upload timing/provenance. D-016/D-020 amended;their prior text retained below. P-014..017 superseded as bundles because25-auto/same-filter manual/intraday-add assumptions conflict. Compatible technical details remain proposals,not retrospectively approved.
| ID | Date | Decision | Who decided | Rationale | Status | Evidence/design |
|---|---|---|---|---|---|---|
| D-030 |2026-11-01|[READ_CODE: user instruction] Automatic universe admission must satisfy all10agreed EQ/price300–5000/history20/turnover100,50,75Cr/ratio0.75/min5day30Cr/positivevolume/band-restriction gates using Dhan+NSE inputs.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| D-031 |2026-11-01|[READ_CODE: user instruction] Manual discretionary IPO/news/earnings universe admission viaCSV uses only verified exclusion of2%/5%band;automatic price/history/liquidity/volume/restriction-screening thresholds do not apply to manual admission.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| D-032 |2026-11-01|[READ_CODE: user instruction] Manual universe shown separately;uploaded user identifier retained across universe,pool,setup,selection,arm,trade and journal.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| D-033 |2026-11-01|[READ_CODE: user instruction] New manual universe entries only one day prior to target trading day;no same-day user additions.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| D-034 |2026-11-01|[READ_CODE: user instruction] Initial poolcapacity75:50automatic+25manual,ranked by liquidity;use whatever eligible/rankable number exists if less;scan each5min through14:35.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| D-035 |2026-11-01|[READ_CODE: user instruction] Manual pool rank uses average available daily liquidity when20completed sessions unavailable;no20session manual admission requirement.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| D-036 |2026-11-01|[READ_CODE: user instruction] Manual universe can contain100uploaded stocks;onlytop25manualscan slots selected.25isnotan upload/membership cap;old20cap superseded.|Mayur|Explicit automatic/manual universe and75-pool instruction|approved|docs/design/UNIVERSE_AND_POOL_CONTRACT.md|
| P-018 |2026-11-01|[ASSUMED] CSV target_session_date,symbol,user_identifier,reason_type,note;server commit-timeT-1 gate;default prior CALENDAR day pending interpretation|Codex proposal|Precise auditable import|proposed|UNIVERSE_AND_POOL_CONTRACT.md section3|
| P-019 |2026-11-01|[ASSUMED] Rank manual latest min(20,N)completed sessions includingzero days,stable numericSIDtie;dedup cohort overlaps,noquota lending or readiness-based hidden replacement|Codex proposal|Exact available-history ranking/counts|proposed|UNIVERSE_AND_POOL_CONTRACT.md section4|
| P-020 |2026-11-01|[ASSUMED] N0manual remains admitted ifbandvalid but rankpending;short-historyindicatorhold until separately approved IPOwarm-up/RVOL policy|Codex proposal|Do not invent liquidity/qualification|proposed|UNIVERSE_AND_POOL_CONTRACT.md section5|
[READ_CODE] Historical current-row text before this amendment (explicit superseded records):
| PRECSV-D-016 | 2026-11-01 | [ASSUMED: user requirement] About twenty persistent manual catalysts until removed; daily revalidation, visible suspension on failure, thirty-day reminder. | Mayur | Controlled persistent discretionary additions; exact cap to be specified. | superseded | [READ_CODE] docs/design/SETUP_AND_UNIVERSE.md; design proposal only, implementation pending |
| PRECSV-D-020 |2026-11-01|[ASSUMED: user-approved] Initial25–50 systematic pool plus catalysts; scale only after measured complete-sweep p95<=60s in no-trade observation |Mayur|Evidence-based capacity| superseded |[READ_CODE] docs/design/SETUP_AND_UNIVERSE.md#hybrid-universe-and-pool|


## IPO follow-up —2026-11-01

[READ_CODE] Mayur's answers:1)tradingdayTmanualentryonT-1;2)useanotherrankingmethodforN0;3)yes,separateIPOshort-historypolicy design. D033reaffirmed,not approval ofSunday/Fridaymapping;noPhase2authorization.
| ID |Date|Decision|Who decided|Rationale|Status|Design|
|---|---|---|---|---|---|---|
| D-037 |2026-11-01|[READ_CODE: user answer] Useanother rankingmethod forzero-completed-sessionIPO,ratherthan makeundefineddailyliquidity thefinalselectionmethod|Mayur|Explicit answer2|approved|docs/design/IPO_SHORT_HISTORY_POLICY.md|
| D-038 |2026-11-01|[READ_CODE: user answer] DesignaseparateIPOshort-historysetup/datapolicy|Mayur|Explicit answer3;exactindicatorparametersnotapproved|approved|docs/design/IPO_SHORT_HISTORY_POLICY.md|
| P-021 |2026-11-01|[ASSUMED] N0CSVmanual_prioritylane,proposed5initialIPOslotswithinmanual25withunusedcapacityflexibility;prioritythenSID|Codex proposal|No fabricatedliquidity/comparable-unitclaim|superseded|IPO_SHORT_HISTORY_POLICY.md section2|
| P-022 |2026-11-01|[ASSUMED] N1..19availablematching-slotRVOL;N0C0vol/previous3vol,20actual5mcloses,3completed15mstrictlyrisingcloseswhenfullHTFnotready|Codex proposal|ExplicitexperimentalIPOprofilewithoutfakehistory|superseded|IPO_SHORT_HISTORY_POLICY.md section3|
| P-023 |2026-11-01|[ASSUMED] Mixed-historysimultaneoustieholdswhen20Dmetricundefineduntilcomparabletiepolicyapproved|Codex proposal|Do notsilentlymixuserpriorityandrupeeADV|proposed|IPO_SHORT_HISTORY_POLICY.md section4|
[READ_CODE] P020's oldN0-rankpending/indicatorholdremain interim limitations,not final desiredpolicy;D037/D038authorize alternatives. ExactT-1calendar mapping remainsunresolved bythe repeatedT-1term;no same-dayadditions underanyinterpretation.


## IPO provisional policy accepted —2026-11-01

[READ_CODE] Mayur:“Yes go ahead for now.This is the currently accepted policy subjected to revision later.” Context:both preceding questions onCSVpriority/allocation andseparateshort-historyindicator model. Not a blanketPhase2/deploymentapproval. P021/P022supersededbyuserdecisionsbelow;P023mixed-historytieproposalremainspending.
|ID|Date|Decision|Who decided|Rationale|Status|Design|
|---|---|---|---|---|---|---|
| D-039 |2026-11-01|[READ_CODE: user acceptance] N0CSVprioritylane withproposed5IPOslots/flexiblemanual25allocation is acceptedfornow;historymanualnamesretainavailable-liquidityrank|Mayur|Explicitacceptanceofranking/allocationanswer|approved|docs/design/IPO_SHORT_HISTORY_POLICY.md section2|
| D-040 |2026-11-01|[READ_CODE: user acceptance] Available-sessionRVOL andfirstdayprior3volume/20actual5mEMAcloses/3completed15mrisingclose model acceptedfornow,separateexperimentalIPOcohort|Mayur|Explicitacceptanceofshort-historymodelanswer|approved|IPO_SHORT_HISTORY_POLICY.md section3|
| D-041 |2026-11-01|[READ_CODE: user condition] CurrentIPOpolicy acceptedsubjecttolaterrevision,notpermanentlylocked|Mayur|Explicitqualificationofacceptance|approved|IPO_SHORT_HISTORY_V1;futureversionhistoryrequired|
[ASSUMED] No test/empiricalproofcomesfromapproval;remainingT-1mapping/tie/source/clean-checkoutdetailsstillseparategates.

## CORRECTION — Phase 1 close-out, 2026-11-01 (append-only)
[READ_CODE] Historical rows above are preserved verbatim. This entry governs their current interpretation; no old approval is expanded.
| Historical row | Current disposition | Evidence / remaining proposal |
|---|---|---|
| [READ_CODE] P-005 | superseded as a bundled proposal | TTL15min approved D-005; trigger-time resizing superseded D-045;90s candle/5s quote remain proposed P-024 |
| [READ_CODE] P-013 | superseded as a bundled proposal | Conservative stop rule approved D-029; AON approved D-012; participation value and freshness remain proposed P-024/P-025 |
| [READ_CODE] P-020 | superseded | N0 priority/allocation and IPO indicator policy approved D-039/D-040; missing actual data still holds, not a blanket N0 prohibition |
| [READ_CODE] P-023 | superseded | Mixed-profile hold replaced by Mayur's D-044 ranking |
[READ_CODE] D-016/D-031 band-only wording is narrowed by D-043; D-003 gains D-044 mixed-profile precedence; D-022 retains L-Q risk but D-045 replaces all trigger-time sizing. D-033 is made precise by D-042. Earlier claims in AUDITOR_BRIEFING.md remain dated snapshots.
| ID | Date | Decision | Who decided | Rationale | Status | Implementing design |
|---|---|---|---|---|---|---|
| D-042 |2026-11-01|[READ_CODE] Upload window opens at previous trading-session close and ends23:59 on the calendar day before target trading day; no same-day additions.|Mayur|Explicit Phase1 close-out decision|approved|docs/design/SPEC_CURRENT.md#universe-and-pool-d-008-d-030d-043|
| D-043 |2026-11-01|[READ_CODE] Manual minimal gate: regular rolling-settlement series allowing intraday square-off; no trade-for-trade/equivalent, not suspended, verified exclusion of2%/5% bands. Liquidity/history gates waived; unknown required status held.|Mayur|Explicit Phase1 close-out decision|approved|docs/design/PARAMETER_REGISTER.md#tradability-sources-d-043|
| D-044 |2026-11-01|[READ_CODE] Simultaneous standard/IPO tie lacking comparable ADV20: standard-profile wins; IPO candidates then ascending CSV priority.|Mayur|Explicit Phase1 close-out decision|approved|docs/design/SPEC_CURRENT.md#selection-sizing-and-atomicity-d-001d-003-d-017-d-022-d-028-d-044d-046|
| D-045 |2026-11-01|[READ_CODE] Size full quantity and fees at ARM/confirmation using frozen T,S,L,Q in paper and future live. Remove trigger-time sizing.|Mayur|Explicit Phase1 close-out decision|approved|docs/design/TIME_AND_EXECUTION.md#sizing-on-stop-limit-overrides-and-precedence|
| D-046 |2026-11-01|[READ_CODE] Defer live multi-arm: pre-live resolve cash/margin blocking and simultaneous fills before cancellation; consider one broker-resident order with others internal, or explicit double-fill rule. Paper multi-arm unchanged.|Mayur|Explicit Phase1 close-out decision|approved|docs/design/PHASE2_PLAN.md#deferred-live-checklist-d-023-d-046|
| D-047 |2026-11-01|[READ_CODE] Consolidated unchanged constraints: PREVIEW_ONLY; no broker code/secrets/deploy/Render/cron changes; long-only;9800 planned risk including costs;980000capital;no leverage;one filled entry/day;five arms;09:15–14:35 scan;entry14:30;close15:00;Phase2 requires explicit instruction.|Mayur|Restates existing hard constraints, not a new implementation approval|approved|docs/design/SPEC_CURRENT.md|
| P-024 |2026-11-01|[ASSUMED] Fresh quote<=5s and last validation candle<=90s; last eligible receipt reconciliation<=90s.|Codex proposal|Unbundles P005/P013 remaining freshness choices|proposed|docs/design/PARAMETER_REGISTER.md|
| P-025 |2026-11-01|[ASSUMED] Full-fill participation/liquidity policy with numeric percentage UNSET; no guessed default.|Codex proposal|Unbundles P013 capacity choice|proposed|docs/design/PARAMETER_REGISTER.md|
| P-026 |2026-11-01|[ASSUMED] Arm-time cash reservations across paper arms sum to available cash; freeze per-arm quantity; release on cancellation/fill conversion. No full-candle evidence from confirmation candle; equal/missing IPO priorities need deterministic policy.|Codex proposal|Explicit engineering details, not implicit approval of all implications of D045|proposed|docs/design/SPEC_CURRENT.md;docs/design/PHASE2_PLAN.md|
