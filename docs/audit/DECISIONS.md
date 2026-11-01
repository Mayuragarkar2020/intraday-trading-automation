# Decision register

[READ_CODE] Created during Phase 0 on 2026-11-01; approval attribution below refers to Mayur's current request, not inferred consent from old chats.
[ASSUMED] Rationale paraphrases the stated intent; it does not add implementation permission. All implementation links below identify existing partial/conflicting code or explicitly pending design.

| ID | Date | Decision | Who decided | Rationale | Status | Evidence / implementation |
|---|---|---|---|---|---|---|
| D-001 | 2026-11-01 | [ASSUMED: user requirement] Selection means the user confirmed a setup. | Mayur | User-defined meaning; older SELECTED_HELD conflicts. | approved | [READ_CODE] src/paper_choice.py; Phase 1 design pending |
| D-002 | 2026-11-01 | [ASSUMED: user requirement] Confirming a selection arms the stock. | Mayur | No additional manual handoff step. | approved | [READ_CODE] src/paper_choice.py (conflict); Phase 1 pending |
| D-003 | 2026-11-01 | [ASSUMED: user requirement] Hard cap: five simultaneously armed stocks. | Mayur | Bound operational load and exposure candidates. | approved | [READ_CODE] Phase 1 pending |
| D-004 | 2026-11-01 | [ASSUMED: user requirement] First armed stock to break out takes the single daily entry. | Mayur | Only user-confirmed candidates may compete. | approved | [READ_CODE] src/forward_paper_ledger.py (partial); Phase 1 pending |
| D-005 | 2026-11-01 | [ASSUMED: user requirement] On a fill, cancel all other armed stocks atomically and alert the user. | Mayur | Prevent multiple competing entries. | approved | [READ_CODE] Phase 1 pending |
| D-006 | 2026-11-01 | [ASSUMED: user requirement] No new arming after the daily fill. | Mayur | Preserve one filled entry per day. | approved | [READ_CODE] src/paper_choice.py (single-choice restriction only) |
| D-007 | 2026-11-01 | [ASSUMED: user requirement] Same-candle ties: highest 20-day average traded value. | Mayur | User-selected tie rule; no alternative proposed. | approved | [READ_CODE] src/paper_choice.py (advisory sort only); Phase 1 pending |
| D-008 | 2026-11-01 | [ASSUMED: user requirement] Latest entry is 14:30 IST; measurement convention remains a Phase 1 proposal. | Mayur | User-set cutoff; do not reinterpret candle label as fill time. | approved | [READ_CODE] src/forward_paper_ledger.py (11:30 conflict) |
| D-009 | 2026-11-01 | [ASSUMED: user requirement] Scanner stops after 14:35 IST. | Mayur | User-set scan window ends at 14:35. | approved | [READ_CODE] src/universe_scanner.py (11:30 conflict) |
| D-010 | 2026-11-01 | [ASSUMED: user requirement] Every entry is a limit order. | Mayur | Bound the accepted entry price. | approved | [READ_CODE] src/paper_engine.py (conflict); src/forward_paper_ledger.py (limit guard) |
| D-011 | 2026-11-01 | [ASSUMED: user requirement] Open beyond the allowed limit cancels that setup as GAPPED_THROUGH, with no fill. | Mayur | No gap chasing. | approved | [READ_CODE] src/paper_engine.py (conflict); Phase 1 pending |
| D-012 | 2026-11-01 | [ASSUMED: user requirement] Never chase with a market entry or reprice the entry order. | Mayur | Preserve the confirmed entry envelope. | approved | [READ_CODE] src/paper_engine.py (conflict); Phase 1 pending |
| D-013 | 2026-11-01 | [ASSUMED: user requirement] Never re-arm automatically. | Mayur | A cancelled setup needs a new explicit user decision. | approved | [READ_CODE] Phase 1 pending |
| D-014 | 2026-11-01 | [ASSUMED: user requirement] Post-14:30 setups through 14:35 are hidden from cockpit and alerts but stored for shadow analysis. | Mayur | Separate trading eligibility from research evidence. | approved | [READ_CODE] Phase 1 pending |
| D-015 | 2026-11-01 | [ASSUMED: user requirement] All positions closed by 15:00 IST; unfilled exposure must remain visible. | Mayur | User's closure requirement; no manufactured flat state. | approved | [READ_CODE] src/paper_models.py; src/paper_trade_management.py |

[ASSUMED: Codex proposal; NOT approved] P-001: archive src/run_daily.py and root render.yaml together after checking external references. Do not delete yet; neither file was changed. Evidence: [READ_CODE] run_daily exits 2 with NOT_READY; render.yaml invokes it.
[ASSUMED: Codex proposal; NOT approved] P-002: handle mid-position faults as visible unresolved exposure plus protective recovery; do not promise flat during feed/DB outages, halts or circuits. Detailed mechanics await Phase 1.
