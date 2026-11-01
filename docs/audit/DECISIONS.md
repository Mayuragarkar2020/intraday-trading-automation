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
| D-003 | 2026-11-01 | [ASSUMED: user requirement] Same-candle ties use highest 20-day average traded value. | Mayur | Approved deterministic liquidity ranking. | approved | [READ_CODE] docs/design/LIFECYCLE_AND_ATOMICITY.md; design proposal only, implementation pending |
| D-004 | 2026-11-01 | [ASSUMED: user requirement] Latest entry 14:30; scanner ends 14:35; later setups hidden from cockpit/alerts but shadow-recorded. | Mayur | Separate research from trading eligibility. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| D-005 | 2026-11-01 | [ASSUMED: user requirement] Detect breakout on five-minute close; model fill in following candle; define cutoff against open labels/close times. | Mayur | Prevent look-ahead and pre-decision fills. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
| D-006 | 2026-11-01 | [ASSUMED: user requirement] Entries are stop-limit, with buffered limit about 0.1–0.2% or a few ticks; exact versioned formula is a Codex proposal; unfillable gap cancels as GAPPED_THROUGH; no market chase/repricing. | Mayur | Bound fill price; exact formula not yet approved. | approved | [READ_CODE] docs/design/TIME_AND_EXECUTION.md; design proposal only, implementation pending |
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
| P-003 | 2026-11-01 | [ASSUMED] Stop-limit buffer=max(0.15% of trigger,3 effective ticks), rounded up; next-candle-close/AON model and conservative ambiguity guards | Codex proposal | Bound modeled price without optimistic gap chasing | proposed | docs/design/TIME_AND_EXECUTION.md |
| P-004 | 2026-11-01 | [ASSUMED] Entry receipt timestamp<=14:30; strict primary visibility before cutoff; late receipt never backdated | Codex proposal | Precise cutoff under source-label/latency ambiguity | proposed | docs/design/TIME_AND_EXECUTION.md |
| P-005 | 2026-11-01 | [ASSUMED] TTL15min; latest validation candle90s and quote5s; preview quantity re-sized at trigger | Codex proposal | Avoid stale handoffs | proposed | docs/design/LIFECYCLE_AND_ATOMICITY.md |
| P-006 | 2026-11-01 | [ASSUMED] Systematic top100 plus up to20 filtered persistent catalysts; membership cap includes suspended; no late primary final universe | Codex proposal | Bounded auditable coverage; fail closed | proposed | docs/design/SETUP_AND_UNIVERSE.md |
| P-007 | 2026-11-01 | [ASSUMED] Authoritative event unique daily-fill index, five numbered arm slots, session lock/fencing and atomic fill/cancel/outbox | Codex proposal | Database-backed guarantees, restart recovery | proposed | docs/design/LIFECYCLE_AND_ATOMICITY.md |
| P-008 | 2026-11-01 | [ASSUMED] Independent watchdog30s; warning90s; critical600s; Telegram alive08:55, absence09:05 visible; new-entry hold when alert channel unhealthy | Codex proposal | Explicit supervision and outage observability | proposed | docs/design/JOURNAL_ALERTS_RECOVERY.md |
| P-009 | 2026-11-01 | [ASSUMED] Protected shadow cohorts and optional explicitly extended-hours research model; never counted as primary trades | Codex proposal | Honest selection comparisons without hidden cutoff violation | proposed | docs/design/JOURNAL_ALERTS_RECOVERY.md |
