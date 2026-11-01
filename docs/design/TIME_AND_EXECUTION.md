# Time, stop-limit execution, risk and replay

[ASSUMED: proposal] Design only. Implements the intended meaning of D-004..007/D-011..014 subject to review; exact conventions below are not asserted approved.

## Time authority and cutoff

[READ_CODE] PR7 documentary evidence establishes one historical opening-labelled example, not a universal contract. Current adapters assume OPEN timestamps; candle_session uses close times. Timestamp/session clearance is still incomplete.
[ASSUMED: proposal] Persist exchange_session, raw_timestamp, raw_label_convention, open_at, close_at, first_received_at, decision_at, recorded_at, source_hash and clock_skew. Normalize only with independently verified instrument/session contract. Every guard uses Asia/Kolkata instants, never display-label string comparison.
[ASSUMED: proposal] Latest accepted primary entry means receipt/decision timestamp **<=14:30:00.000 IST**, not a candle labelled 14:30. Order request must exist before its simulated fill; a late receipt cannot be backdated. Scanner processes closes through 14:35; it begins at 09:15 but cannot qualify a three-bar session range immediately.
[ASSUMED: proposal] Setup visibility uses known_at: known_at>=14:30 is hidden/no setup alert (strictly before cutoff is actionable; equality treated conservatively as hidden). Already-open position/fault/exit alerts remain visible all afternoon. Detection/receipt latency is separately journaled.
[ASSUMED: proposal] The breakout candle's high reaching trigger is evaluated only at its close, after confirmation. Pin all armed candidates before that candle opens; no setup can claim a pre-confirmation high. No extra close>trigger condition is added to the current high-cross rule.
[ASSUMED: proposal] Simulate at the **following candle close** (economic price at that close, accepted/recorded only on timely receipt). This is paper bar simulation, not proof that a live stop-limit would have filled at that price. Never use following open that predates the decision's actual receipt.
[ASSUMED: proposal] Fill acceptance requires next_close<=cutoff AND received_at<=cutoff AND trigger_known_at<next_close. At 14:30 process any exact-on-boundary eligible fill before cutoff expiry within the session lock; later arrivals are NO_FILL_LATE_RECEIPT. The live clock never waits beyond cutoff to accept a new entry.

| Raw OPEN label | Close | Role | Proposed result |
|---|---|---|---|
| [ASSUMED] 14:15 | 14:20 | Breakout detection | Following 14:20–14:25 close receipt can fill before cutoff |
| [ASSUMED] 14:20 | 14:25 | Breakout detection | Following close 14:30 is eligible only if received exactly by 14:30; normal delayed receipt is too late |
| [ASSUMED] 14:25 | 14:30 | Breakout detection | Following close 14:35 exceeds cutoff: CANCELLED/FILL_WINDOW_EXCEEDS_CUTOFF |
| [ASSUMED] 14:30 | 14:35 | Research setup | Hidden, shadow only; no primary order |

[ASSUMED: proposal] At 14:30 all untriggered arms cancel CUTOFF_REACHED with outbox alert; pending entry candidates that cannot fill by cutoff also cancel CUTOFF_REACHED, including remaining retry attempts. Existing position management continues. No automatic re-arm; manual reselection before cutoff gets a new confirmation ID, linked to the old attempt, only if still valid.
[ASSUMED: proposal] Entry buckets: OPENING [09:15,09:45), ORIGINAL [09:45,11:30), MIDDAY [11:30,13:30), LATE [13:30,14:30], POST_CUTOFF_SHADOW (14:30,14:35]. Store both setup-known and fill buckets. Opening/midday/late strategy performance is UNVALIDATED.
[ASSUMED: proposal] Late fills have identical initial SL, five-minute EMA10 close exit and 1.5R cost-breakeven rules; no relaxed stop or artificial target. No minimum holding time overrides the 15:00 deadline. Flag SHORT_TIME_TO_FLATTEN, minutes_to_1500 and entry_bucket for analysis.

## Stop-limit price, sizing and conservative all-or-nothing fill

[ASSUMED: proposal] Let T be tick-valid confirmed entry trigger, S confirmed initial stop, tau instrument-effective tick. Limit L = ceil_to_tick(T + max(0.0015*T,3*tau)). Formula version STOP_LIMIT_BUFFER_V1; parameters and instrument tick source/date hashed into config. Do not assume every stock uses 0.05. No repricing after trigger. Entry still occurs only after trigger-close evidence; no broker stop-limit is submitted.
[ASSUMED: proposal] At trigger time compute q as largest positive integer satisfying BOTH q*(L-S)+estimated_entry_fee(q,L)+estimated_exit_fee(q,S_adverse)+q*(S-S_adverse)<=9800 AND q*L+estimated_entry_fee(q,L)<=min(available_cash,980000). S_adverse is tick-rounded down stop minus approved slippage allowance. Use Decimal; nonlinear fee schedules require integer search or verified bounded sizing, not an unproved per-share division.
[ASSUMED: proposal] Reject REJECTED_BY_RISK if q=0, fee/tick data unknown or any final guard exceeds the cap; never infer actual gap losses are capped at INR9,800. Recheck original confirmation envelope, free cash, session lock and daily-fill slot before fill; no enlargement after trigger.
[ASSUMED: proposal] For following candle O,H,Lo,C, first check timeliness, tradability, same-session/source integrity, and that decision_at precedes its close. If O>L, immediately cancel GAPPED_THROUGH even if Lo later comes back inside L. This is intentionally pessimistic under unknown intrabar sequence; do not infer a beneficial pullback.
[ASSUMED: proposal] Other no-fill guards: Lo<=S => INVALIDATED/AMBIGUOUS_ENTRY_STOP; O<T => CANCELLED/TRIGGER_RETRACE_UNMODELED; C<T => CANCELLED/TRIGGER_NOT_HELD; ceil_to_tick(C*(1+slippage))>L => GAPPED_THROUGH; volume/quoted liquidity cannot support full q => CANCELLED/INSUFFICIENT_FULL_FILL_CAPACITY. These are conservative simulation proposals, not asserted exchange mechanics.
[ASSUMED: proposal] Eligible model price P=ceil_to_tick(C*(1+slippage_bps/10000)); require T<=P<=L, Lo<=P<=H and q<=floor(volume*participation_pct/100). Full q fills or zero fills. If capacity is positive but <q, append PARTIAL_MODEL_ANOMALY with proposed quantity then zero fill/cancel; never silently reduce quantity to available liquidity.
[ASSUMED: proposal] For an exit, full position quantity must be executable at the chosen later valid candle price; otherwise zero exit with EXIT_PENDING, anomaly and critical visibility. D-012 applies to all paper fills. No synthetic fraction or partial accounting. No adverse price outside observed tradable high/low. Missing quote depth cannot be represented as known queue priority.
[ASSUMED: proposal] Gap cancellation consumes no daily filled-entry token; other valid arms remain available for later intervals, with no same-interval runner-up fallback. This prevents a late re-ranking/chase. User may manually reselect the cancelled setup before cutoff with fresh confirmation. This allocation policy remains a proposal.
[ASSUMED: proposal] To avoid optimistic competition, resolve all valid armed signals in the complete interval before winner reservation. Incomplete armed coverage holds that interval; no backfilled price can later create its missed primary entry.

## Exit precedence

[ASSUMED: proposal] All rules use completed five-minute OHLC/EMA10; EMA on a chart is informational only. Keep original entry/SL/R immutable.
1. [ASSUMED] Halt/circuit/not-tradable: retain position, alert; no fill. Exit first later valid full tradable price; mark deadline breach if late.
2. [ASSUMED] Existing pending recovery/flatten/protective exit has priority over new stop changes; request flatten at 14:50 and retry on later valid closes. 15:00 is deadline, never assumed fill.
3. [ASSUMED] If active protective SL touched, request STOP; no 1.5R move can retroactively rescue same-candle stop.
4. [ASSUMED] Otherwise close<EMA10 requests EMA10 exit, including before 1.5R; close==EMA10 holds.
5. [ASSUMED] Otherwise high>=entry+1.5*(entry-originalSL) requests cost-breakeven; effective next bar, never on the bar generating it. Stop never moves down.
[ASSUMED: proposal] Breakeven floor is the smallest tick-valid stop whose adverse full-exit proceeds cover entry debit plus all expected exit fees under the pinned fee/slippage model. It is a request, not a guarantee against future gap losses. EMA10 exit and time flatten remain active after breakeven; no fixed target.
[ASSUMED: proposal] Initial-fill bar's pre-fill extremes do not produce trailing/EMA decisions. Protective monitoring starts after modeled fill; ambiguous same-bar entry/stop is rejected rather than guessed. Exit signals at close execute at a later valid close; this may add delay/loss and must be versioned.

## Replay correction and invalidated evidence

[READ_CODE] src/paper_engine.py currently sizes/fills using slipped max(bar.open,trigger), supports partial capacity fills, and sorts same-time plans by their identifiers. These do not implement the intended stop-limit/multi-arm model.
[ASSUMED: proposal] Introduce a new immutable engine/model version; do not overwrite old stored replay runs. Existing results are NOT evidence for STOP_LIMIT_BUFFER_V1. Mark all old runs LEGACY_ENTRY_MODEL; runs whose buy price>new L or opening gaps above L are optimistic under the new contract. Old same-candle/partial-fill plans, input-order winners, old-window runs presented as all-day evidence and unknown source labels require re-evaluation. Not every old run is mathematically wrong; its scope is different.
[ASSUMED: proposal] Query old runs by engine_version and ENTRY_FILL price vs recomputed limit; without stored config/tick/source inputs, mark COMPARISON_UNRESOLVABLE rather than inventing a list/count. No production DB queried; affected run IDs/counts currently UNKNOWN.
[ASSUMED: proposal] Required future pure tests: exact cutoff boundaries and delayed receipt; next-bar only; gap opens>L then trades back remains cancelled; no reprice/re-arm; full/zero capacity; same-bar stop/BE/EMA priority; halted exit and late recovery; no use of pre-decision extremes; fee/risk cap mutation tests. Phase 2 first slice writes tests before code, without deployment/order paths.
