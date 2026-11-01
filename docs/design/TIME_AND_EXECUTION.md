# Time and execution — current resting bracket detail

[READ_CODE; D-042–D-047] Close-out2026-11-01: SPEC_CURRENT.md is canonical;this file supplies execution detail. Mayur requires ARM-time frozen quantity and fees;all previous trigger-time sizing proposals are superseded.

[READ_CODE] Approval update2026-11-01: Mayur answered “all yes” to the five round2 questions. Approved scope: C0 filter scope/prior3 width denominator; max(T-S)/T2.5%; one-tick default T/S buffers; stop-limit rather than plain-limit; proposed override bounds and conservative low<Q stop-no-fill rule with sensitivity. This is design approval of those choices, not implementation/test proof, buffer calibration or Phase2 authorization. Other proposals remain proposed.

[ASSUMED] Design only / no application implementation. Mayur's amended D-005 and new D-018..020 govern; engineering defaults explicitly marked proposed await Mayur. The former next-candle-close/receipt-cutoff primary model is SUPERSEDED, not retained as normal execution.

## Signal, tick prices and lifetime

[ASSUMED: Mayur-approved strategy] C0 is the completed5m signal candle; close(C0)>max(high(-1C),high(-2C),high(-3C)), STRICTLY. Qualification exists only after C0 closes and is received/verified. C0 is not part of the three-bar comparison range.
[ASSUMED: review defaults; approved scope stated above] With effective instrument tick tau, T0=high(C0)+tau; S0=min(low(C0),low(-1C),low(-2C),low(-3C))-tau. Require source prices/tick compatible, positive S<T; do not retain fixed0.05 or silently round invalid input. Default one-tick buffers confirmed by Mayur2026-11-01.
[ASSUMED: Mayur-approved strategy] Expiry=C0.close+15minutes. No confirmation or fill after expiry. Any observed pre-entry low<=accepted S invalidates. Confirmation requires current valid quote price<T; equality rejects ALREADY_BROKEN_AT_SELECTION. No profit target.
[ASSUMED: proposal] Bar-only primary replay requires confirmation/order acceptance BEFORE the eligible candle opens; a mid-candle confirmation cannot borrow the full candle's earlier high. Use verified finer-grained observations after acceptance if available; otherwise mark CONFIRMATION_BAR_PATH_UNKNOWN and exclude that partial candle from fill evidence. If it already crossed T with unknown sequence, cancel/hold explicitly, never backdate a fill. This limitation is an analysis cohort, not a new default later-candle fill rule.

## Cutoff by exchange candle window

[ASSUMED: Mayur-approved amendment] Entry eligibility is based on normalized exchange candle timestamps: fill candle.open<14:30 IST, within regular session, and within setup lifetime. Receipt timestamp is ONLY a staleness/knowledge guard, not the14:30 eligibility boundary. Scanner09:15–14:35; setups known at/after14:30 stay hidden/shadow-only; no new confirmation then.
[ASSUMED: proposal] Normalize OPEN/CLOSE raw labels to [open,close) with independently verified instrument/session contracts. Receipt-close age<=90s remains a proposed stale guard. A resting arm existed beforehand; its qualifying historical interval may be committed on a timely later receipt without pretending the execution was newly decided before confirmation. Store event-window bounds and received/recorded_at separately; do not fabricate an exact intrabar fill timestamp.
| OPEN label | Close | Primary eligibility for pre-existing arm | Outcome |
|---|---|---|---|
| [ASSUMED]14:20|14:25|Yes|Resting entry may fill within that candle |
| [ASSUMED]14:25|14:30|YES: last eligible five-minute fill candle|Timely14:30+receipt can reconcile a fill from [14:25,14:30); no receipt-cutoff rejection |
| [ASSUMED]14:30|14:35|NO|No primary entry, hidden setup/shadow evidence only |
[ASSUMED: proposal] A C0 closing14:25 can be confirmed before14:30, but bar-only evidence cannot fill a candle that began before confirmation. It needs post-confirmation sub-bar evidence or a later full candle, which is already outside cutoff; do not assume it can fill from the whole14:25 bar. C0/arm timing and fill-candle eligibility are different guards.
[ASSUMED: proposal] At14:30 untriggered arms cancel CUTOFF_REACHED and alert. There may be an unresolved last eligible candle. Persist CUTOFF_PENDING_RECONCILIATION and a pending cancellation keyed effective_at14:30; reconcile only a timely prior eligible interval for arms demonstrably resting beforehand. If filled before cutoff, sequence fill then cancel-other-arms; otherwise finalize cutoff cancellation. Never fill the14:30-opening candle. After90s without that receipt, finalize NO_ELIGIBLE_TIMELY_EVIDENCE/no fill; later data shadow-only. No new arming during reconciliation.
[ASSUMED: proposal] Close-by15:00 remains absolute target: flatten intents from14:50, retry at valid tradable prices, flag outstanding/late/unknown closure. Entry buckets use exchange fill-window open and retain setup/selection/receipt buckets; OPENING09:15–09:45, ORIGINAL09:45–11:30, MIDDAY11:30–13:30, LATE13:30–14:30, POST_CUTOFF_SHADOW14:30–14:35. Afternoon performance unvalidated.
[ASSUMED: proposal] Late entries keep5m EMA10-close exit before/after1.5R, cost-breakeven modification and15:00 flatten, without minimum hold/target. Record minutes-to-flatten/late-entry tags; no extension to recover losses.

## Resting stop-limit entry and all-or-nothing

[ASSUMED: Mayur strategy / placeholder] Entry stop-limit trigger T; L=ceil_tick(T+max(0.0015*T,3*tau)).0.15% and3ticks are PLACEHOLDERS pending historical analysis; formula/config version ENTRY_BUFFER_REVIEW_V2 and effective tick/source pinned at arm. No market entry/chase/repricing.
[READ_CODE; D-045] At confirmation compute and freeze T,S,L,Q,full q and estimated entry/exit fees with their versions. The resting intent has that quantity from ARM onward in paper and future live. Trigger detection resolves fill eligibility only,never sizes/resizes. Persist quote/cash snapshot and immutable arm-time cost calculations;no contingent sizing policy. Any changed prices/override requires a new explicit validated confirmation,not automatic repricing.
[ASSUMED: proposal] Candle O,H,Lo,C for a fully eligible rested arm: O>L => CANCELLED/GAPPED_THROUGH with zero fill EVEN IF Lo later returns; never chase. If T<=O<=L, base entry=O. If O<T and H>=T, base entry=T. If H<T, remain ARMED until expiry/cutoff/other invalidation. Adverse buy slippage ceil_tick(base*(1+slip)) must remain<=L and within observed tradable OHLC; otherwise zero fill GAPPED_THROUGH/NO_VALID_LIMIT_PRICE. No close>=T condition or TRIGGER_RETRACE_UNMODELED restriction remains in the primary model.
[ASSUMED: proposal] Require full q<=floor(volume*participation_pct/100) plus valid tradability evidence; insufficient full capacity gives zero fill and PARTIAL_MODEL_ANOMALY (if positive partial implied), never shrink q to available volume. Same applies to exits: all-or-nothing, pending exposure if full exit unproven.
[ASSUMED: proposal] Initial bar O<=S invalidates before entry. If O<T and both H>=T and Lo<=S, OHLC cannot order entry vs invalidation: retain LOW_FIRST=no-entry and HIGH_FIRST=entry-then-stop paths, primary result selects worse net outcome where both paths are feasible, tag ENTRY_STOP_PATH_AMBIGUOUS. If O>=T within L, entry at open precedes later stop movement. No profitable omission of same-bar stop risk.

## Protective stop-limit and STOP_NOT_FILLED

[ASSUMED: Mayur strategy / placeholder] Logical bracket: entry plus protective SELL stop-limit, no profit target. Protective trigger S; Q=floor_tick(S*(1-0.01)), positive.1% is a placeholder STOP_BUFFER_REVIEW_V2. Stop becomes active atomically with paper entry. A plain limit sell resting below market would behave differently; do not implement it while terminology awaits Mayur.
[ASSUMED: Mayur-approved resting-stop model, bounded by stop-limit] Stop fill is at S when touched from above, or opening price if gap opens below S, with adverse sell slippage. This applies ONLY if resulting price>=Q and valid/tradable. If open<Q, stop is NOT filled. This reconciles the approved resting-stop shortcut with the explicit stop-limit failure case; no unbounded gap fill at open.
[ASSUMED: review defaults; approved scope stated above] Primary OHLC stop rule:
1. [ASSUMED] Tradability/halt/zero/insufficient-full-capacity => no fill; retain exposure.
2. [ASSUMED] O<Q => STOP_NOT_FILLED, regardless of later rebound.
3. [ASSUMED] Q<=O<=S => candidate=floor_tick(O*(1-slip)); fill full only if candidate>=Q and observed tradable.
4. [ASSUMED] O>S and Lo>S => untouched; HOLD.
5. [ASSUMED] O>S and Q<=Lo<=S => candidate=floor_tick(S*(1-slip)); fill full only if candidate>=Q and inside observed range.
6. [ASSUMED] O>S but Lo<Q => STOP_NOT_FILLED under the conservative rule, even though a continuous descent could have filled near S first. This explicitly avoids optimistic path/liquidity certainty.
7. [ASSUMED] A candidate below Q or partial-capacity suggestion => STOP_NOT_FILLED/anomaly, not a fill at an unlawful sell price.
[ASSUMED: Mayur strategy] STOP_NOT_FILLED is a CRITICAL state/event; notify immediately on detection, freeze new entries, retain full outstanding quantity, cancel/confirm old stop then issue a broker-neutral marketable EXIT intent at next valid tradable price. Never pretend the INR9,800 planned-loss cap bounds this loss.
[ASSUMED: proposal] With only completed5m data, failure detection and fallback may be delayed. Do not use a next-bar open that predates failure receipt/cancel confirmation. Use first verified tradable quote AFTER exit intent acceptance, or later valid close as DEGRADED_FEED_FALLBACK. Record fallback detection lag and not-fill incident loss separately. A delayed-close protective model remains only a named degraded-feed fallback, never silently pooled with resting-stop primary results.
[ASSUMED: proposal] Sensitivity: compare conservative rule6 with CONTINUOUS_TOUCH (S-slippage if above Q despite later low<Q), gap/liquidity-stress variants, and no-fill+next-valid-exit. Report stop-fill rate, STOP_NOT_FILLED count, next-price latency, excess-loss quantiles and max drawdown by model; no assertion any variant matches real queue behavior.

## Sizing on stop LIMIT, overrides and precedence

[ASSUMED: Mayur-approved sizing] Worst-case modeled per-share price risk=L-Q, plus estimated fees. Also report trigger-based L-S+fees. “Worst-case” is bounded modeled stop-limit risk, NOT a guaranteed max loss if the stop fails.
[ASSUMED; D-022,D-045] At ARM/confirmation q is largest positive integer with q*(L-Q)+fees_entry(q,L)+fees_exit(q,Q)<=9800 AND q*L+fees_entry(q,L)<=min(cash,980000). Decimal/nonlinear fee model; pin approved fees or hold. Slippage must fit L/Q; do not double-count it by adding allowances already represented by these bounds. Store both risk calculations and stop-limit buffer premium q*(S-Q). q=0/unknown fee/tick/cash => REJECTED_BY_RISK at confirmation, no arm. Fees fixed from frozen limit prices/version at arm; actual modeled execution costs are journaled separately,never used to increase frozen quantity at trigger.
[ASSUMED: review defaults; approved scope stated above] Max trigger distance (T-S)/T<=2.5%: limits broad invalidation distance without confusing prior-range width; report rejection/sample bias and replay1%/1.5%/2%/2.5%/3% sensitivity before approval. Not an optimization result.
[ASSUMED: review defaults; approved scope stated above] Overrides relative to rule T0/S0: abs(T-T0)<=max(0.10%*T0,2*tau), abs(S-S0)<=max(0.10%*T0,2*tau). Require T>=high(C0)+tau; S<=min(low4)-tau; risk/distance/tick/freshness/live_price<T all pass. This permits only modest later entry/wider stop, avoiding overrides that erase the actual breakout/invalidation levels. Log bound model and OVERRIDDEN cohort; bounds approved by Mayur2026-11-01; not implemented/tested.
[ASSUMED: proposal] Exit precedence: halt/nontradable holds exposure; existing protective fill beats any replacement; STOP_NOT_FILLED recovery critical; active-stop touch beats EMA or1.5R within an ambiguous bar; EMA10 close<EMA10 requests cancel-confirm-marketable exit; else1.5R high requests stop modification effective NEXT bar; flatten from14:50 uses same cancel-confirm-exit sequence and15:00 deadline. No fixed target.
[ASSUMED: proposal] Cost-breakeven is based on entry fill and all fee/slippage assumptions. To remain cost-breakeven under the protective stop-limit model, raise the stop trigger enough that its derived Q covers the net break-even exit price; do not equate new S=entry+fees with a guarantee when Q is1% lower. Pin modified S/Q, never loosen, and report unrealized feasibility. The1.5R condition remains based on actual entry minus ORIGINAL S.
[ASSUMED: proposal] For EMA/flatten/recovery, STOP_CANCEL_REQUESTED -> STOP_CANCEL_CONFIRMED -> EXIT_REQUESTED -> EXITED. Before exit re-read fills/open quantity under same fenced lock. If stop filled during cancellation, close/journal it and submit no extra sell. Unknown cancel result means STOP_CANCEL_UNCONFIRMED, critical hold/reconcile; never sell full size while a potentially active stop could create a short position.

## Replay correction

[READ_CODE] Existing code lacks the C0 breakout signal, four-candle tick stop and resting stop-limit bracket. Previous design's following-close primary model is also superseded.
[ASSUMED: proposal] New immutable engine/rule/config IDs; preserve all stored runs. ALL old-rule runs are non-evidence for the new strategy (not necessarily erroneous for their recorded rule). Flag optimistic gap-chase/partial fills/stop fills below Q; rerun only from authentic timestamp-normalized data. No production run IDs/counts verified here.
[ASSUMED: proposal] Detailed real-data buffer/selection/stop sensitivity protocol is in REPLAY_ANALYSIS_AND_TEST_PLAN.md. No analysis or new application tests run this round.

## Confirmation delay and last eligible C0 close
[READ_CODE; D-018,D-045] Candle labels are exchange OPEN times;C0 close is signal-known time,not its label. Human confirmation delay reduces remaining execution opportunity.
[ASSUMED; D-018,P-026] For conservative bar-only replay,confirmation INSIDE the next candle excludes that partial candle entirely;order must precede the next full eligible candle open. Faster observed post-confirmation quotes/sub-bars form a separately evidenced cohort,not whole-candle hindsight.
| C0 OPEN label | C0 closes | Confirmation inside next candle | First full rested fill candle | Primary result |
|---|---|---|---|---|
| [ASSUMED; D-018]14:10 |14:15 |[14:15,14:20) |[14:20,14:25) |Eligible |
| [ASSUMED; D-018]14:15 |14:20 |[14:20,14:25) |[14:25,14:30) |LAST C0 CLOSE14:20 for full-bar model under this delay assumption |
| [ASSUMED; D-018]14:20 |14:25 |[14:25,14:30) |[14:30,14:35) |Ineligible;only verified post-confirmation sub-bar evidence before14:30 could permit entry |
| [READ_CODE; D-004,D-018]14:25 |14:30 |>=14:30 |None |Hidden/shadow-only,no confirmation |
[ASSUMED; D-018] Confirmation exactly on a boundary must have verified acceptance ordering before execution evidence;equal timestamps without ordering proof cannot borrow that candle. Receipt latency still only guards stale evidence;never backdate human action.
[ASSUMED; D-015,D-045] Journal setup_age_at_selection_seconds=confirmed_at-C0.close,setup_age_at_arm_seconds,confirmation_quote_age,arm_to_fill_window_delay and order acceptance time;record rejected attempts including already-broken and expired. Existing “selection age” metric is retained with an explicit unit/formula.
[READ_CODE; D-046] Future live multi-arm deferred;paper5-arm batch resolution unchanged. Pre-live must resolve cash/margin blocking and simultaneous external fills;see PHASE2_PLAN.
