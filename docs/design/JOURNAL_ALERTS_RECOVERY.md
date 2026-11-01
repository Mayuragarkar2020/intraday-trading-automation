# Journal, alerts and recovery — round 2 resting bracket

## Manual CSV/source amendment

[READ_CODE] Mayur now requires manual stocks admitted byT-1 CSV,only2%/5%band exclusion as admission filter,and a visible user identifier across universe/scanning/setup/selection/trade/journal. This supersedes any same-filter/manual20cap or same-day addition assumption.50automatic/25manual cohort slots,not75manual memberships.
[ASSUMED] Add upload_id,row_hash,uploaded_at,target_session,user_identifier,reason_type,note,universe_route,manual_rank_lookback_sessions,band_admission_status,pool_selected/status and source-provenance snapshots. Notifications,shadow exports and closed outcomes retain identifier. Editable later labels do not rewrite the uploaded label attached to past trades.
[ASSUMED] Band-only admission does not create20 matching RVOL slots;indicator/data holds remain separately visible. A zero-history IPO's liquidity rank is unresolved,not fabricated. Manual price/history/liquidity exemptions must carry into route-aware UI/validation so old automatic price filters cannot silently reject membership.

[ASSUMED: proposal] Design only; no service, token, Telegram chat, process supervisor or production migration is configured here.

## Round 2 additions: bracket risk, path uncertainty and stop failure

[ASSUMED] Primary engine is C0_V2/resting stop-limit bracket, with exchange fill-candle-open cutoff; former following-close primary semantics are superseded. Delayed-close execution remains DEGRADED_FEED_FALLBACK only. Same-candle ranking version ARMED_BAR_ADV20_SID_V1.
[ASSUMED: proposal] Extend trade/setup records with C0/prior3 IDs, generated T0/S0 vs overrides, accepted T/S, entry L, stop Q, stop-buffer version, per-share/total L-Q risk INCLUDING fees, comparison L-S risk, selection age/live quote, filter/distance/buffer policy and OVERRIDDEN cohort.
[ASSUMED: proposal] Bracket/intent events include active stop version, trigger/touch window, bounded fill price, STOP_NOT_FILLED reason/model, cancellation request/confirmation/unknown status, stop-versus-exit race outcome, full remaining quantity, fallback accepted_at and first valid post-intent evidence. No broker-specific fields/call.
[ASSUMED: proposal] Separate STOP_FAILURE_EXCESS_LOSS cohort with realized loss, loss-minus9800 (positive excess only), stop gap/cross-through, failure-to-alert and failure-to-exit latency, unrealized/open status and deadline breach. “Planned<=9800” must never display as guaranteed max realized loss.
[ASSUMED: proposal] Exchange execution window and received/recorded_at are separate. For resting intrabar fills/exits, exact MFE/MAE and selection-order chronology may be unknown. Use fully held bars plus execution prices for observed bounds; record entry/exit-bar PATH_AMBIGUOUS and lower/upper excursion bounds or finer verified data. Do not include pre-entry extrema or post-exit low as exact MAE. Preserve model-specific path assumptions in primary/shadow comparison.
[ASSUMED: proposal] Stop failure alerts are CRITICAL immediately on detection, unsnoozable; dashboard shows STOP_NOT_FILLED/STOP_CANCEL_UNCONFIRMED until reconciled/fully exited. A failed cancel does not authorize a duplicate full sell. See TIME_AND_EXECUTION stop rules and LIFECYCLE stop-versus-exit race.

## Authoritative event and journal schemas

[ASSUMED: approved user intent] D-015: database event journal is authoritative; JSON projection is derived/rebuildable.
[ASSUMED: proposal] paper_events stores append-only sequence/hash-chain events with explicit columns for account/session/ledger_kind/type, IDs, state transition and timestamp provenance. Unique idempotency key and monotonic per-account sequence; validated payload/config/source hashes. Role denies event UPDATE/DELETE. Account, arm-slot, order-attempt and UI models are projections; every write uses expected sequence and writer fencing.
[ASSUMED: proposal] setup_observations: setup_id, instrument identity, range and qualification reasons, qualified_at/known_at, universe_source and membership IDs/note, original proposal, rule/config hashes, receipts, source freshness, setup_bucket, hidden/shadow flags. Include all qualified setups even unselected, denied, expired or cancelled; no trading state inferred from catalogue presence.
[ASSUMED: proposal] confirmations: original T/S, requested override, accepted T/S, user reason, validation quote/candle/tick/cost evidence, request and actor IDs, confirmed_at, arm slot, rejection codes; later attempts link supersedes_confirmation_id without rewriting history.
[ASSUMED: proposal] trade_outcomes: setup/confirmation/order/entry/exit event IDs; trigger and modeled-vs-received fill times; entry trigger, frozen limit, actual modeled fill, quantity, original SL, stop changes, participation/slippage assumptions; estimated/actual modeled fee breakdown; gross/net P&L; planned risk; net R; actual-loss-risk/deadline breaches; setup and entry buckets; source provenance; selected reason; exit reason; MFE/MAE; incomplete-data flags; schema/engine/config/rule versions.
[ASSUMED: proposal] Excursions start at entry price: MFE/share=max(0,max(valid post-fill highs)-entry), MAE/share=max(0,entry-min(valid post-fill lows)); money=q*per-share; price R uses entry-originalS; net-R uses cost-inclusive planned L-Q risk. Only fully held bars have exact OHLC inclusion; entry/exit-bar unknown path yields bounds per round2 additions. Missing intervals => EXCURSION_DATA_INCOMPLETE.
[READ_CODE] trade_manager.py::excursion already computes high/low since fill and price-R excursions; paper_engine.py's inspected final journal does not include those fields. Reuse requires proper receipt/fill boundaries and schema/version work.
[ASSUMED: proposal] Journal write occurs atomically with closed-outcome projection after verified EXIT_FILLED; if rendering fails, authoritative EXITED event supports idempotent regeneration. Failed exit remains open journal with outstanding exposure, not a completed trade. Cash identity: opening cash+realized net P&L=closing cash when flat; any mismatch freezes new entries.
[ASSUMED: proposal] User post-trade tags/reason corrections are separate append-only annotations (actor/time/revision), not event/fill edits. Cockpit filter columns include source, selected/unselected, time bucket, cancellation reason, engine/rule/config hash and shadow cohort. No manual trade retyping required.

## Shadow tracking without selection bias claims

[ASSUMED: proposal] shadow_runs and shadow_events use the SAME rule/fee/tick/stop-limit/AON/exit engine version and timestamp contract, separate hypothetical account IDs. Each alternative gets its own one-trade counter/cash; it never consumes primary risk or broker requests. Reuse already captured eligible prices; if unavailable, NO_DATA, not guessed fill.
[ASSUMED: proposal] Cohorts: UNSELECTED_QUALIFIED, CANCELLED_GAP, CANCELLED_SUPERSEDED, USER_CANCELLED, EXPIRED and POST_CUTOFF_HIDDEN. Retain actual terminal outcome (e.g. gap gives no fill) plus a separately identified counterfactual that begins at the next permissible decision time, never falsely “fills” the cancelled attempt.
[ASSUMED: proposal] For comparison, use a fixed hypothetical confirmation time after setup knowledge (e.g. next complete bar boundary plus configured processing delay); version it. Hidden post-cutoff setups must retain primary NO_ENTRY_CUTOFF result. An optional RESEARCH_EXTENDED_ENTRY cohort can simulate after14:30 until the15:00 exit deadline ONLY with explicit shadow-only cutoff override, prominently marked counterfactual/not rule-compliant primary. Otherwise post-cutoff shadow is qualification/path tracking with zero primary-like trades.
[ASSUMED: proposal] This distinction avoids violating D-004 while claiming to measure hypothetical late-entry outcomes. Store missing horizon, unfillable gaps and censoring. Compare Mayur against unselected alternatives within matched day/time/source/model cohorts; no proven skill/causality claim from descriptive differences.
[ASSUMED: proposal] Hidden means no main cockpit candidate and no setup push, not inaccessible forever. Authenticated Analysis/Shadow view and read-only export/query support session/source/selected/state/bucket/version filters. A query joins setup_observations to shadow_runs/trade_outcomes on setup_id/model version; exclude PRIMARY when requesting hypothetical results. No public raw DB endpoint; notes remain access-controlled.
[ASSUMED: proposal] Keep minimal immutable events/closed outcomes; retain raw market receipts per reviewed storage policy with hashes/provenance. Proposed90-day online receipt retention then archive, never delete required audit/event lineage silently. Capacity/retention approval remains separate from deployment.

## TradingView links and test cases

[ASSUMED: proposal] Link-only URL: https://www.tradingview.com/chart/?symbol= + percent_encode("NSE:"+symbol, safe="") + "&interval=5". Use the exchange symbol from verified mapping, not free-form pasted query strings. No embedding/scraping, chart-derived signal, token or account state in the URL. Cockpit detail links use setup ID plus session, not bearer credentials.
[ASSUMED: proposal] Browser tab uses noopener/noreferrer. Chart availability/symbol mapping is informative and unverified until browser test; our independently validated Dhan/NSE feed is decision authority. This session's example web retrieval was inaccessible; no functioning chart claim.
| Input | Expected symbol query value | Future assertion |
|---|---|---|
| [ASSUMED] RELIANCE | NSE%3ARELIANCE | interval=5 and exact symbol |
| [ASSUMED] M&M | NSE%3AM%26M | ampersand stays inside symbol, not a second query parameter |
| [ASSUMED] BAJAJ-AUTO | NSE%3ABAJAJ-AUTO | hyphen preserved |
| [ASSUMED] invalid identity / whitespace / injected query | reject or use verified canonical mapping | no arbitrary URL/query injection |
[ASSUMED: proposal] Future tests parse generated URL back into one symbol and interval key, round-trip M&M and verify external anchor protections. Test cases are design only; no application tests added/run.

## Telegram alert contract

[ASSUMED: approved user intent] Telegram is the phone alert channel; a daily alive message is required. Telegram API acceptance is not proof of handset delivery or user attention.
[ASSUMED: proposal] Outbox atomically commits with domain events; idempotency=(account,event_id,channel,alert_type). Delivery attempts/ACK/status separate from trade state. Store chat/token securely outside repo; redact request URLs and provider response bodies. Retries may duplicate a delivery if send succeeded but ACK persistence failed: include stable alert/event ID and record UNKNOWN_DELIVERY rather than promise exactly-once Telegram delivery.
| Alert | Payload | Proposed service target |
|---|---|---|
| [ASSUMED] Qualified | symbol, T/S, age, setup bucket, chart link, authenticated cockpit deep link | <=60s from verified candle close and <=5s after setup commit |
| [ASSUMED] Armed | symbol, frozen T/S and limit preview, slot count, holds | <=5s after confirmation commit |
| [ASSUMED] Other arms cancelled | winning stock and list/reason SUPERSEDED_BY_FILL | <=5s after atomic fill commit |
| [ASSUMED] Gap cancellation | symbol, O/L, GAPPED_THROUGH; manual reselection only | <=5s after decision |
| [ASSUMED] Cutoff cancellation | summary of remaining arms, CUTOFF_REACHED | <=10s after14:30 |
| [ASSUMED] Triggered / entered | distinct statuses; trigger receipt then full fill q/P/risk, no promise from trigger alone | <=5s after each commit |
| [ASSUMED] Exited | reason, full fill, net P&L, deadline/data flags, journal link | <=5s after exit commit |
| [ASSUMED] STOP_NOT_FILLED | trigger/limit, gap/path model, outstanding q, critical recovery status; no max-loss guarantee | immediate on detection; target<=5s after event commit |
| [ASSUMED] System fault / missed heartbeat | exposure status, last data/manager heartbeat, recovery phase | warning by90s stale; critical open-position outage at600s |
| [ASSUMED] Daily alerting alive | dated session, runtime/source readiness, no-execution reminder | 08:55 target; absence by09:05 is conspicuous failure |
[ASSUMED: proposal] Targets are not measured SLAs. Retry critical messages with bounded backoff (1,5,15,60s then periodic incident update); prevent flood by incident ID. Setup messages expire at TTL/cutoff and are not sent late. Alert rate limit: per-symbol setup once per new C0 fingerprint and at most once/15min; total setup5/min with overflow digest. Symbol snooze30min suppresses new setup pushes only, never risk/exit/cutoff/fault messages or database capture.
[ASSUMED: proposal] Quiet market still publishes scan heartbeat with scheduled interval, completed/expected pool counts, source age, holds and zero-qualified count. Cockpit shows last successful scan, next due, worker/manager and Telegram ACK ages separately; last DB write alone is not proof of scan health.
[ASSUMED: proposal] Telegram unreachable: red ALERT_CHANNEL_DOWN banner, pending/failed outbox counts, no new confirmations/entries once channel health stale, primary manager/clock continues. Independent watchdog records incident and retries Telegram; if Telegram itself is down, it cannot deliver a phone alert through Telegram. User sees absence of daily alive and cockpit red status; no alternate channel is assumed configured. This remains an operational limitation before activation.

## Independent supervision, replay and reconciliation

[ASSUMED: proposal] Future worker writes liveness every30s with owner/fencing epoch, position/exposure status, latest committed event sequence, last processed market close and next manager due. Feed/DB/alert health are separate fields. Monitor runs on a different host/process boundary, with its own last-known heartbeat; a dead worker cannot be its own outage detector.
[ASSUMED: proposal] Host/container supervisor restarts a crashed process with bounded backoff, single-writer lease/fencing and restart count. Independent monitor polls<=30s, warns if heartbeat>90s, and flags critical D-014 if open or UNKNOWN exposure and downtime>=600s (two candles). Render supervision behavior is currently UNVERIFIED; no new monitor or restart policy is configured by this design.
[ASSUMED: proposal] If DB is unreachable, monitor falls back to last known open/unknown exposure and process heartbeat, never “flat”. DB and worker sharing a failure domain must not silence monitor. No indefinite retry loop consumes all worker attention; clock/network operations have individual deadlines.
[ASSUMED: proposal] Restart sequence: acquire fenced writer -> load last trusted event checkpoint -> verify contiguous sequence/hash/config/source lineage and one daily-fill constraint -> replay canonical events -> compare JSON/relational projections, cash/exposure/arms -> record RECONCILIATION_OK or repair projections atomically from events. Do not adjust events to match projection.
[ASSUMED: proposal] If projection alone differs and event chain is valid, record PROJECTION_REBUILT with before/after hashes; resume only after invariant checks. If events conflict/missing/corrupt, freeze new trades, display EXPOSURE_UNKNOWN, retain last known position, critical alert and require reviewed recovery; do not zero cash/position.
[ASSUMED: proposal] After open-position downtime>=600s, set recovery_exit_required; cancel unfilled entries/arms, request full exit at FIRST valid tradable post-recovery price after accepted recovery intent/cancel confirmation; use a labelled delayed-close fallback only if finer evidence unavailable, and journal outage duration/gap/MAE-MFE incompleteness. No fill during downtime; “flat” occurs only after that committed exit. If next valid receipt is after15:00, retain closure breach forever. At halt/circuit hold until actually tradable, not an auction/zero-volume assumed print.
[ASSUMED: proposal] Recovery after missed current candles cannot replay them as retrospectively executed stops/entries; use for research/excursion bounds only and flag uncertainty. Conservative recovery exit takes precedence over resuming ordinary strategy. No new entry while unresolved exposure or reconciliation hold exists.

## Failure matrix

| Fault | No position | Open position | Alert/evidence |
|---|---|---|---|
| [ASSUMED] Worker crash | Persisted arms held; no new trigger/fill; supervisor restart | Ownership incident; restart/reconcile; >=600s recovery exit | Independent heartbeat warning/critical; no fake fill |
| [ASSUMED] Missed5m candle | Cancel affected attempt FEED_GAP_NO_NEW_ENTRY; no backfill entry | Clock continues; pending protective/recovery exit at next valid price | Missing close and pool coverage visible |
| [ASSUMED] Feed disconnect/gap | Block selection/entry; reconnect with verified continuity | Keep exposure; source-aware clock; next tradable exit if recovery needed | SOURCE_STALE incident plus age |
| [ASSUMED] DB outage | No new arm/entry/write success | Exposure UNKNOWN; no unjournaled simulated fill; external watchdog | Last-known exposure critical; reconcile first |
| [ASSUMED] Duplicate trigger | Same event/result returned | Same event cannot mutate twice | Idempotency conflict if payload differs |
| [ASSUMED] Cancellation SQL fails | Retry under session lock | Entire entry fill transaction rolls back if fill/cancel bundle fails | No partial primary bundle; incident/outbox after durable recovery |
| [ASSUMED] Cancellation alert fails | State still terminal | Entry/manager stay committed | ALERT_UNDELIVERED; outbox retry, no re-arm |
| [ASSUMED] Telegram down | Block new handoffs/entries; show red banner | Manager and clock remain priority; no automatic abandonment | Delayed incident, daily-alive absence; no phone-delivery guarantee |
| [ASSUMED] Stop crossed without valid fill | No new entry after incident | STOP_NOT_FILLED, full exposure, cancel-confirm then marketable recovery; no invented Q fill | CRITICAL, excess-loss cohort |
| [ASSUMED] Halt/circuit | Suspend/cancel entry, no fill | Hold, immediate alert request, first full valid tradable exit | HALTED exposure; late closure breach if applicable |
