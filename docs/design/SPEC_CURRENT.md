# Current canonical specification [READ_CODE; D-047]
[READ_CODE; D-047] Future sessions read SPEC_CURRENT.md plus the task only, unless the task requires a detail file. Other design documents are detail/history; this specification and latest append-only decisions take precedence.
[READ_CODE; D-041,D-047] Phase1 design only; not implemented/validated by these documents. No Phase2, broker code, deployment, cron or Render change.
[READ_CODE; D-047] PREVIEW_ONLY; long-only; capital INR980000; planned risk including costs<=INR9800; no leverage; one filled entry/IST day; at most five armed stocks.
[READ_CODE; D-021,D-047] Planned risk is not maximum realized loss: stop failure/halts can exceed9800 or15:00; retain visible exposure/breach rather than fabricate flat.
## Universe and pool [READ_CODE; D-008,D-030–D-043]
[READ_CODE; D-008,D-030] Build provisional automatic universe after previous session, revalidate before09:15; unknown identity/status/source freshness holds; no fallback to unvalidated list.
[READ_CODE; D-030] Automatic gates ALL apply: NSE EQ; reference close300–5000 inclusive;20completed sessions; positive volume each session.
[READ_CODE; D-030] Daily traded value gates:20Dmean>=100Cr,median>=50Cr,latest>=75Cr,latest/mean>=0.75,min(last5)>=30Cr; exclude2%/5% bands/restricted/unknown.
[READ_CODE; D-016,D-031,D-043] Manual IPO/news/earnings stocks persist until removal; liquidity/history/automatic-price gates waived; regular rolling-settlement intraday-square-off series only,not suspended,no2%/5% band; unknown required evidence holds.
[READ_CODE; D-042] For trading day T, upload opens at PREVIOUS TRADING SESSION CLOSE and ends23:59 on calendar T-1; no same-day additions. Use exchange calendar/Asia-Kolkata.
[ASSUMED; D-042] Proposed exact interval is [previous_session_close,T00:00),including whole23:59 minute; server commit time controls admission; weekends/holidays included,not a one-calendar-day-only window.
[READ_CODE; D-016,D-032,D-036,D-043] CSV user identifier/note/source follow every stage; separate cockpit universe view; daily minimal-gate revalidation; visible suspension/reason;30day reminder;25is not upload cap.
[READ_CODE; D-043] NSE series/security files,TFT/surveillance/suspension notices and band reports are documented-only source candidates; PARAMETER_REGISTER defines validation needed. Admission is not permission to fill nontradable data.
[READ_CODE; D-020,D-034,D-035] Pool capacity75=50automatic+25manual; descending liquidity within cohorts; manual uses available completed-day mean when<20sessions; underfill allowed.
[ASSUMED; D-034,D-035,P-019] Precise rank uses mean last min(20,N) sessions,then numericSID; dedup overlapping routes,retain both provenance,no quota lending. Missing source is HOLD,not zero turnover.
[READ_CODE; D-039] N0 IPO lane: ascending supplied CSV priority then SID; manual allocation k=min(I,max(5,25-min(H,25)),25),history=min(H,25-k); total<=25.
[READ_CODE; D-020,D-034]75is target capacity,not measured throughput; complete-sweep p95<=60s in no-trade observation needed before activation/further scaling; hold if unmet.
## Signal and cohorts [READ_CODE; D-005,D-009,D-024–D-026,D-040]
[READ_CODE; D-005] C0 completed5m close STRICTLY>highest high of -1C,-2C,-3C; established only after verified close.
[READ_CODE; D-026] T0=high(C0)+instrument tick; S0=minLow(C0..-3C)-tick; compatible positive ticks required; no fixed0.05 buffer.
[READ_CODE; D-024] C0:EMA10>EMA20,close above both and sessionVWAP,RVOL>=1.2; prior3width/close(-1C)<=2.5%.
[READ_CODE; D-024,D-040] STANDARD20 RVOL uses20prior matching slots; completed15m EMA10>EMA20 with both rising; need valid20-close5m/21+completed15m warm-up per detail specification.
[READ_CODE; D-040] IPO_AVAILABLE_DAYS N1..19 RVOL uses matching slots of all Nverified prior sessions; missing/zero denominator holds;20actual5m closes needed; standard HTF if ready,else3completed15m closes strictly rising.
[READ_CODE; D-040] IPO_LISTING_DAY N0 RVOL=C0volume/mean(previous3current5m volumes);20actual current5m closes,SMA-seeded EMA;3completed15m closes strictly rising; no synthetic history.
[READ_CODE; D-005,D-025] Lifetime15minutes after C0.close; no confirmation/fill after expiry; low<=accepted S before entry invalidates; (T-S)/T<=2.5%.
[READ_CODE; D-009,D-032,D-040,D-041] Keep standard/systematic,manual catalyst,IPO experimental,override,late,shadow/degraded-feed cohorts separate; afternoon/IPO effectiveness unvalidated.
## Selection, sizing and atomicity [READ_CODE; D-001–D-003,D-017,D-022,D-028,D-044–D-046]
[READ_CODE; D-001,D-017,D-028] User confirms proposed T/S or bounded override; original/override/reason logged; ticks,side,distance,staleness and live quote<T checked. Equality rejects ALREADY_BROKEN_AT_SELECTION.
[READ_CODE; D-028] Override absolute changes<=max(0.10%T0,2ticks); T>=T0,S<=S0; regenerate L/Q then validate all guards.
[READ_CODE; D-045] At confirmation freeze T,S,L,Q,full q,fee breakdown/version,capital snapshot and arm event atomically. Quantity and fees computed NOW,never resized at trigger.
[ASSUMED; D-022,D-045] q=max positive integer satisfying q(L-Q)+entryFees(q,L)+exitFees(q,Q)<=9800 and qL+entryFees<=available cash<=980000; unknown inputs/q0 reject. Also report q(L-S)+same fees and q(S-Q).
[ASSUMED; D-045,P-026] Proposed paper reservations sum across arms<=cash; released atomically,fill converts winner reservation. Never shrink frozen q at trigger; insufficient cash/full capacity =>zero fill,explicit rejection/cancellation.
[READ_CODE; D-002,D-012] Confirm arms up to5; double-tap returns same result; first eligible candle winner gets only daily fill,all other arms atomically CANCELLED/SUPERSEDED_BY_FILL+alert; no arming after fill.
[READ_CODE; D-003,D-044] Comparable STANDARD20 candidates rank frozenADV20 descending thenSID; if standard/IPO tie lacks comparableADV20,STANDARD20 wins; IPO candidates rank CSV priority.
[ASSUMED; D-044,P-026] Missing IPO priority in an IPO trade tie holds unresolved cohort; equal priorities proposed SID ascending; pin tie version MIXED_PROFILE_V2 before implementation.
[ASSUMED; D-002,D-015,P-007] Database unique daily ENTRY_FILLED event;five numbered unique slots;session lock/fencing;fill/bracket/cancel/outbox transaction; failure rolls back all. PostgreSQL barrier test required,not yet run.
[READ_CODE; D-046] Paper multi-arm remains; future live multi-arm DEFERRED pending cash/margin blocking and pre-cancellation simultaneous-fill decision.
## Entry and protection [READ_CODE; D-006,D-012,D-019,D-021,D-027,D-029]
[READ_CODE; D-006] Resting BUY stop-limit: L=ceil_tick(T+max(0.0015T,3ticks));0.15%/3tick formula is pinned placeholder,not final calibration.
[READ_CODE; D-006,D-007] Eligible rested arm: open>L =>GAPPED_THROUGH zero fill even if returns; no chase/reprice/automatic rearm; manual reselection only valid/before cutoff.
[ASSUMED; D-006,D-012] T<=open<=L base=open;open<T and high>=T base=T;adverse tick-rounded slippage<=L,within tradable observed range; otherwise zero fill; full frozen q only.
[READ_CODE; D-021,D-027] Logical bracket,no target: protective SELL stop-limit trigger S,limit Q=floor_tick(S*(1-0.01));1% placeholder; protective intent activates atomically with paper fill.
[READ_CODE; D-019,D-029] Valid stop fills at S or gap-open after sell slippage only>=Q; open<Q or open>S with low<Q =>STOP_NOT_FILLED even if a continuous descent might have filled first.
[ASSUMED; D-012,D-029] Untouched low>S holds; Q<=open<=S uses open;open>S with Q<=low<=S uses S; require full tradable capacity/observed price,else stop failure/anomaly.
[READ_CODE; D-013,D-021,D-023] STOP_NOT_FILLED:critical alert,retain quantity,freeze new trades,cancel-confirm/reconcile then next valid post-intent marketable exit; halt holds exposure,never invented price.
[ASSUMED; D-005,D-029] Same-bar entry/stop ordering unknown:retain low-first/high-first sensitivity,primary worse feasible net outcome; no hindsight omission of stop risk.
[ASSUMED; D-019,D-023] Exit precedence: existing stop fill first; stop-failure recovery; stop touch before EMA/1.5R ambiguity;5mclose<EMA10 exits;else1.5R modifies stop next bar;15:00 flatten overrides holding.
[ASSUMED; D-019,D-022] Cost-breakeven modification must lift derived Q enough to cover costs,never loosen stop;1.5R uses actual fill minus original S;not guaranteed realized breakeven.
[ASSUMED; D-023] Cancel stop,confirm/reconcile remaining quantity,then exit;stop filled during cancel=>no duplicate sell;unknown cancellation=>critical reconciliation,never risk short.
## Time and evidence [READ_CODE; D-004,D-005,D-011,D-018,D-047]
[READ_CODE; D-004,D-018] Scan09:15–14:35IST;new setups known>=14:30 hidden/no setup push,still shadow-recorded;no new confirmations>=14:30.
[READ_CODE; D-018] Fill interval OPEN<14:30;last eligible full interval14:25–14:30;receipt is freshness/knowledge guard,not entry-cutoff timestamp.
[ASSUMED; D-018,P-024,P-026] Bar-only confirmation inside next candle excludes that partial candle;C0close14:20,confirm14:20–14:25,first full eligible fill14:25–14:30;C0close14:25 needs post-confirmation finer evidence,not whole-bar hindsight.
[READ_CODE; D-011] Untriggered arms cancel at14:30/CUTOFF_REACHED+alert; timely last-interval reconciliation for pre-existing arms detailed in TIME_AND_EXECUTION,not new14:30-bar entry.
[ASSUMED; D-047] Flatten from14:50 proposed to meet15:00;stop failures/halts retain explicit unresolved/deadline-breach state. No extension to recover losses.
## Journal, alerts and recovery [READ_CODE; D-010,D-013–D-015,D-021,D-032,D-045]
[ASSUMED; D-015,D-032,D-045] Journal every setup/selection/cancellation/shadow with versions/hashes,reason,user label,original/override,T/S/L/Q,frozen arm q/fees/reservations,modeled fills/costs,MFE/MAE,source/profile/time buckets and editable post-trade tags.
[ASSUMED; D-005,D-015] Persist setup_age_at_selection_seconds=selection_at-C0.close;confirmation latency,already-broken rejection,arm/fill interval and receipt times;unknown intrabar MAE/MFE flagged.
[READ_CODE; D-010,D-021] Telegram qualified(chart+cockpit link),armed,cancelled/gap/cutoff,entered,exited,fault/heartbeat and daily alive;critical alerts unsnoozable.
[ASSUMED; D-010,P-008] Proposed alive08:55,missing09:05;event alerts<=5s after commit/qualified<=60s after close;watchdog30s,warn90s,open-position outage600s;not measured SLA.
[ASSUMED; D-010] Quiet market heartbeat shows expected/completed pool/last candle/zero setups;Telegram down shows red cockpit/outbox,retry and no new entries;no independent phone channel assumed.
[READ_CODE; D-014,D-015] Database events authoritative,JSON derived;fenced restart verifies chain,rebuilds projections,reconciles arms/daily fill;conflict=>EXPOSURE_UNKNOWN/no new trade.
[READ_CODE; D-013,D-014] Open-position downtime>about10min alerts/flags;recover at first valid post-recovery price,never fictitious flat;independent supervision/restart remains unverified.
[ASSUMED; D-015] Shadow uses same versioned rules with independent hypothetical accounts;unselected,cancelled,hidden post-cutoff remain queryable in database,not cockpit primary list.
[READ_CODE; D-023] TradingView link only:https://www.tradingview.com/chart/?symbol=NSE%3AM%26M&interval=5;own feed decides;no scrape/embed.
## Phase boundary [READ_CODE; D-047]
[READ_CODE; D-047] PHASE2_PLAN.md is a proposal only. Clean checkout+baseline,required parameter decisions and explicit Mayur “start Phase2” instruction are prerequisites.
