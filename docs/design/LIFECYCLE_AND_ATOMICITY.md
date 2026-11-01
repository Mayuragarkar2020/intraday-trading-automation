# Current-detail precedence
[READ_CODE; D-042–D-047] SPEC_CURRENT.md is canonical. ARM time freezes full quantity and fees;manual tradability/upload and mixed-profile tie amendments there override older wording below. Detail proposals remain proposals.

# Lifecycle and atomicity — round 2 resting paper bracket

[READ_CODE] Approval update2026-11-01: Mayur answered “all yes” to the five round2 questions. Approved scope: C0 filter scope/prior3 width denominator; max(T-S)/T2.5%; one-tick default T/S buffers; stop-limit rather than plain-limit; proposed override bounds and conservative low<Q stop-no-fill rule with sensitivity. This is design approval of those choices, not implementation/test proof, buffer calibration or Phase2 authorization. Other proposals remain proposed.

[ASSUMED] DESIGN ONLY. The logical paper intents below are broker-neutral records, not broker orders, endpoints, credentials or library integrations. No Phase2/migration executed.
[ASSUMED: Mayur amendment] Confirming persists SELECTED+ARMED. Entry is a resting stop-limit from acceptance, not a new instruction after a trigger candle closes. ARMED->TRIGGERED->ENTERED may occur in the SAME eligible candle; paper evidence commits on its receipt. Required ordering: accepted arm before execution evidence; no retrospective pre-confirmation high.

## Event envelope and transitions

[ASSUMED: proposal] Every event E: account/session/ledger kind, setup/confirmation/intent/bracket IDs, instrument identity, expected event sequence/fencing epoch, before/after state, reason, raw label/open/close/execution-window bounds, known/received/recorded timestamps, rule/config/source/universe hashes and idempotency key. Changed payload under same key conflicts. Intrabar OHLC has a window, not invented exact execution time.
| Transition | Trigger / guard | Additional persisted fields | Idempotency key | Restart behavior |
|---|---|---|---|---|
| [ASSUMED] none->DETECTED | C0 completed, strict close>prior3high; fresh eligible inputs; provisional filter defaults pass | C0/prior3 IDs, indicators, width, generated T0/S0 | instrument+session+C0+rule hash | Reconstruct; no duplicate signal |
| [ASSUMED] DETECTED->SURFACED | known before14:30 and valid/within15min | visibility and outbox/deep links | setup+SURFACE | Retry outbox only |
| [ASSUMED] DETECTED->SHADOW_RECORDED | hidden after cutoff / unselected research | cohort, no-primary-entry code | setup+shadow model | No setup push/main-cockpit appearance |
| [ASSUMED] SURFACED->SELECTED->ARMED | live price<T, valid bounded override/tick/risk/freshness, before expiry/cutoff, free slot<=5, no daily fill | T0/S0 and accepted T/S/L/Q, note, quote, accepted_at, quantity policy, arm slot, bracket version | account+client_request_id | Both events atomic; validate arm still eligible before prospective use |
| [ASSUMED] ARMED->TRIGGERED->ENTERED | Same-candle high>=T or allowed opening gap; eligible exchange window; full AON capacity; cost-inclusive L-Q sizing; deterministic batch winner | frozen arm-time quantity consumed (no resizing), entry fill/window, full risk comparison, bracket stop activated | account+session+eligible interval+resolution; unique ENTRY_FILLED | Return committed result, never refill |
| [ASSUMED] ENTERED->MANAGED | Atomic protective-intent activation/manager assignment | active stop S/Q/version, owner lease, open q | entry+BRACKET_ATTACHED | No paper state exposing committed entry without bracket |
| [ASSUMED] MANAGED->STOP_NOT_FILLED | gap below Q / conservative cross-through / full fill unproven | failure reason, gap/path/capacity evidence, open q, critical incident | bracket+stop version+receipt+failure | Retain position; do not replay imaginary stop fill |
| [ASSUMED] MANAGED/STOP_NOT_FILLED->STOP_CANCEL_REQUESTED | EMA/flatten/recovery or replacement intent | cancel intent targeting exact active stop version | bracket+exit decision+cancel | Retry same cancel/reconcile |
| [ASSUMED] STOP_CANCEL_REQUESTED->STOP_CANCEL_CONFIRMED | confirmed no remaining active stop; check concurrent stop fills | confirmed stop q/status, reconciled open q | cancel intent+confirmation | Already-filled stop wins; zero position means no second exit |
| [ASSUMED] STOP_CANCEL_CONFIRMED->EXIT_REQUESTED | remaining q>0, fresh tradable evidence, no competing sell | marketable paper intent, reason, exit evidence lower bound | bracket+exit decision+EXIT | Execute only later/valid evidence, no backdated quote |
| [ASSUMED] STOP_CANCEL_REQUESTED->STOP_CANCEL_UNCONFIRMED | failed/unknown cancel outcome | critical reason, pending protection/exposure | cancel+unknown outcome | Freeze new entries; reconcile before any duplicate full sell |
| [ASSUMED] MANAGED->STOP_MODIFIED | old stop cancel-confirm/reconcile then atomically install raised protective version;1.5R | old/new S/Q, BE cost calculation, effective next bar | bracket+new stop version | Resume only known active version; uncertainty critical |
| [ASSUMED] MANAGED/EXIT_REQUESTED->EXITED->JOURNALED | full valid protective/fallback/discretionary exit, q reconciles | costs, P&L, MFE/MAE, stop-failure/excess-loss/deadline flags | entry+EXIT_FILLED; entry+JOURNAL schema | Regenerate derived journal; no extra fill |
| [ASSUMED] DETECTED/SURFACED/ARMED->EXPIRED | C0.close+15min/session expiry | expiry/effective time | attempt+EXPIRY | Terminal; no automatic re-arm |
| [ASSUMED] unfilled->INVALIDATED | pre-entry low<=S; identity/band/restriction/source failure | invalidating evidence/code | setup+receipt+INVALIDATION | Never erase history; no entry from invalid setup |
| [ASSUMED] confirmation->REJECTED_BY_RISK | invalid override/tick/distance/fees/cash or q=0/cap breach | original/override, L-Q and L-S risk computations | request+validation version+receipt | Same request same rejection |
| [ASSUMED] ARMED/TRIGGERED->CANCELLED | gap O>L, cutoff/expiry/user/removal/other fill/no AON | GAPPED_THROUGH/SUPERSEDED_BY_FILL/USER_CANCELLED/CUTOFF_REACHED etc | attempt+cause event | Release slot exactly once; manual new confirmation only |
[ASSUMED: proposal] Same-bar entry-vs-stop ambiguity uses TIME_AND_EXECUTION's pessimistic path model, not low-before-entry guessed ordering. A filled position cannot be “cancelled”; it must follow exit management. Partial-fill suggestions are anomalies and zero fills; no partial position model.

## Route-aware membership and selection guard

[READ_CODE] New manual route bypasses automatic universe price/history/liquidity/restriction thresholds at admission;requiresT-1 CSV and verified non2%/5%band. Source provenance/user identifier and ranking history length must accompany setup and choice. Global300–5000automatic guards must not silently blockmanual admission/confirmation solely on that price criterion.
[ASSUMED] Setup/risk/quote/tick/stop-distance/override/cutoff guards still apply to both routes. Short-history indicator holds remain explicit pending a separately approved IPO setup-data policy. CSV same-day addition cannot create or swap an arm. Lifecycle events record immutable membership/upload/user label;accepted prior-day membership revalidation is not a new user entry.

## Selection contract and override bounds

[ASSUMED: review defaults; approved scope stated above] Generated T0/S0 one tick beyond C0/prior4 extrema, accepted overrides within max(0.10%*T0,2ticks), still above highC0/below all4 lows, positive exact ticks, (T-S)/T<=2.5%, fresh quote<T, full15min lifetime and available cost-inclusive risk/cash. Store selection reason, original/overridden values and OVERRIDDEN cohort. Full formula in TIME_AND_EXECUTION.
[ASSUMED: proposal] Setup age is C0.close to selection; validation quote max age5s/latest candle90s are proposals. Readiness hold or unknown tick/source rejects, never silently rounds/repairs. Stale selection/expired attempt cannot place/rest an intent.
[ASSUMED: proposal] Same account+request ID returns original result; changed override conflicts. Active arm is one symbol/setup/attempt; hard total5. After daily entry fill no new arming. Manual re-selection after gap requires still-valid signal, fresh quote<T and before14:30; a terminal attempt never revives itself.
[ASSUMED: proposal] Alert noise: one setup per C0 fingerprint, per-symbol15min setup-message rate and total5/min digest;30min snooze suppresses setup messages only. Risk/stop-failure/exit/cutoff alerts unsnoozable. Signal refresh never silently moves an existing user's T/S.

## Database guarantees and same-candle ties

[ASSUMED: proposal] Authoritative append-only paper_events with UNIQUE partial index(account_id,session_date) WHERE event_type='ENTRY_FILLED' AND ledger_kind='PRIMARY'. Paper account fixed/server-pinned; positive BUY q; fee/risk/capital checks inside writer transaction. JSON account and relational guard tables are projections of committed events.
[ASSUMED: proposal] paper_arm_slots CHECK(slot BETWEEN1 AND5), primary key(account,session,slot), unique confirmation and unique active symbol. DB session gate rejects arming after fill. One primary resolution candidate per session. Session lock+fencing+expected sequence protect effects; direct duplicate SQL fill fails unique index.
[ASSUMED: Mayur-approved ranking / versioned tie] Eligible armed candidates in the SAME five-minute candle use highest frozen20D mean traded value, then ascending security ID, policy ARMED_BAR_ADV20_SID_V1. Freeze the complete armed set/input hashes. This is a candle-model tie, not proof of which stock crossed first at tick resolution. Incomplete candidate coverage holds interval; late backfill is shadow-only.
[ASSUMED: proposal] Transaction: lock session -> replay/reconcile if needed -> evaluate full batch and choose winner -> validate frozen arm quantity/fees and reserved cash,never resize -> insert unique primary fill+bracket activation/manager events -> cancel all other arms SUPERSEDED_BY_FILL -> clear slots/candidate -> project cash/risk -> persist entered/cancelled/critical outbox -> commit. Protective STOP_NOT_FILLED on entry candle is appended in same event bundle when evidence requires it; never omit the loss.
[ASSUMED: proposal] Any cancellation/bracket/projection/outbox SQL failure rolls back the whole paper entry. Unknown commit result queries idempotency key under lock before retry. Telegram failure does not roll back committed trade or resurrect other arms. No same-bar runner-up chase after GAPPED_THROUGH; other valid arms may await later eligible evidence, without re-arming the cancelled setup.
[ASSUMED: proposal] Restart with multiple arms: event replay, projection comparison/repair, cutoff/expiry and source checks, pending last eligible interval reconciliation, then prospective evidence. Daily fill exists => all remaining arms terminal before resume. No retrospective price before accepted intent. Damaged event chain => EXPOSURE_UNKNOWN/new entries frozen.

## Stop-versus-exit race and neutral intents

[ASSUMED: proposal] Intent types: ENTRY_STOP_LIMIT, PROTECTIVE_STOP_LIMIT, MODIFY_STOP, CANCEL_INTENT, MARKETABLE_EXIT. Common fields: intent/version/bracket IDs, BUY/SELL, full frozen q, trigger/limit/expiry, cause event and status. No broker-specific payload/API call or client library.
[ASSUMED: proposal] Rule: CANCEL -> CONFIRM -> RECONCILE -> EXIT/REPLACE. Stop fill during cancel wins. Re-read remaining exposure under lock; if q=0, journal only. Unknown cancel => no blind duplicate sell, critical incident. Exit fill q can never exceed current q and never create short exposure.
[ASSUMED: proposal] Paper bracket activation/replacement can be atomic in events; a future broker might not support that atomicity. Failed stop placement after a live fill, multiple resting entries all filling before client cancels, and uncertain cancel ACKs are live-phase blockers, not solved by a paper DB index. See future preflight checklist; no live capability is assumed.

## Authoritative Phase2 base and test design

[ASSUMED: Codex proposal] Single implementation base: origin/main 79a2d3086c8aea660dc31068e2758db1f7332808, i.e. PR14's HumanChoicePaperLedger foundation. New pure lifecycle/replay slice branches there after clean-checkout verification/design approval. Reuse tested accounting/choice guard concepts; replace incompatible single-choice/old-window interfaces via reviewed implementation, not a hidden PR15 dependency.
[READ_CODE] Current main paper_choice.py contains HumanChoicePaperLedger validating the exact saved human choice under the ledger writer path. It does NOT already implement this revised multi-arm/bracket model.
[ASSUMED: proposal] PR13 and PR15 stay open, unmerged reference-only proposals; no wholesale merge/cherry-pick. Document any future selective reuse with tests/review and provenance. PR14 remains the merged foundation; docs PR16–round2 are continuity only. Close no PR.
[ASSUMED: proposal] Migration later: audit old event/cash/open exposure, create new event/index/slot guards, preserve legacy runs read-only; never reset daily history or migrate an unknown open position blindly. No migration executed.
[ASSUMED: proposal] Planned PG concurrency test uses two independent connections+barrier, reversed arrival and tied/different ADV/SID; exactly one ENTRY_FILLED with correct winner, one cash debit/bracket, all others cancelled. Direct duplicate fill and sixth arm must fail SQL constraints. Inject failures in fill/bracket/cancel/outbox to prove full rollback. Pure interleaving test is separate and cannot claim PG race proof.

## Close-out arm snapshot and ranking corrections
[READ_CODE; D-045] SURFACED->SELECTED+ARMED atomic event persists generated/accepted T,S,L,Q,full q,arm-time fee components/version,riskL-Q/riskL-S,quote/cash snapshot and selection reason. Rejected risk creates no resting intent. Restart restores exact q/fees;trigger never recomputes them.
[ASSUMED; P-026] Reservation events reserve entry notional+entry fee for each paper arm;sum<=cash. Fill converts winner reservation,atomically releases cancelled arms;race/failure rollback preserves cash. This is an unapproved detail,not automatic shrinking of q.
[READ_CODE; D-044] When standard/IPO candidates lack comparableADV20,standard-profile candidates win;standard subset usesADV20/SID,IPO candidates useCSVpriority. Earlier mixed-history TIE_METRIC_UNAVAILABLE hold is superseded for this case.
[ASSUMED; D-044,P-026] Equal IPO priorities useSID and missingpriority holds are proposals pending review;do not claim an approved numeric bridge betweenpriority andADV.
[READ_CODE; D-046] Database paper one-fill guarantee is unchanged;no claim it prevents multiple external broker fills. Live multi-arm remains deferred.
