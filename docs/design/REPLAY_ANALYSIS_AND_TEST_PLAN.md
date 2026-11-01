# Replay analysis and Phase2 test targets — round 2

[ASSUMED] Analysis/test DESIGN ONLY. No real historical dataset was downloaded/analyzed this round; no new application test or Phase2 code was written. Parameter values remain placeholders, not empirical recommendations.

## Buffer and selection evidence protocol

[ASSUMED: proposal] Use authentic historical NSE5m OHLCV from our source with verified identity/tick histories, calendar, raw timestamp labels, receipts where available, restrictions/universe eligibility, split/corporate-action adjustment policy and20 preceding matching sessions. Preserve raw hashes and effective dates. Historical candles alone do NOT reveal real historical user selection times, tick path, spread/depth or fill queue.
[ASSUMED: proposal] Freeze C0_V2 signal/filter version, stop-limit policy, sizing, fees and eligibility; compare entry-buffer fractions0.10%,0.15%,0.25%,0.40% with the3-tick floor in EVERY percentage arm, plus FLOOR_ONLY=max(0,3ticks). L=ceil_tick(T+max(p*T,3tau)). Also retain3ticks as a separately reported dominance condition, not an extra hidden percent buffer.
[ASSUMED: proposal] Measure per qualified setup: next eligible candle open gap (O-T)/T in %, ticks, signed and positive-only; open>L rate by buffer; trigger touch, modeled full fill, GAPPED_THROUGH, partial-capacity anomaly and no-data counts; fill rate denominator includes all eligible qualified/armed attempts and separately triggered attempts. Distribution: median/p75/p90/p95/p99/max; sample size and confidence intervals, not only averages.
[ASSUMED: proposal] Keep identical setup IDs/data folds across buffer variants; no choosing different stock pools to improve one buffer's result. Stratify by opening/original/midday/late bucket, liquidity tier, systematic/manual, overridden/default, symbol/day and timestamp quality. Bootstrap by day to respect correlated setups. Separate development/holdout periods; do not tune on holdout, and do not silently treat surviving liquid stocks as the historical universe.
[ASSUMED: proposal] Analyze returns/netR/drawdown/fees/stop-failure tails alongside fill rate; largest fill rate alone is not a selection rule. Record missing/censored/halted/degraded paths and capped15:00 horizon. Report results across filters/distance1%,1.5%,2%,2.5%,3% before proposing final config. No numerical performance result is claimed here.
[ASSUMED: proposal] “Already broken at selection” rate = confirmed/rejected selection attempts whose observed price>=accepted T divided by all selection attempts with a fresh quote, with unobservable attempts counted separately. Setup age=selection_at-C0.close; report its distribution and rejection/expiry rate by age. Requires actual confirmation/quote journals; OHLC alone cannot measure this as an observed user rate.
[ASSUMED: proposal] Until such journals exist, simulate selection delays5/15/30/60/120/300/600/900s after C0 knowledge and label them ASSUMED_SELECTION_DELAY. For mid-bar selection, evaluate partial-bar path uncertainty and no-before-confirmation guards; don't impute exact live prices from a full-bar high. Report lower/upper bounds for already-broken rate where OHLC cannot decide.

## Protective-stop sensitivity

[ASSUMED: proposal] Compare STOP_CONSERVATIVE_V2 (low<Q or gap<Q gives STOP_NOT_FILLED) to CONTINUOUS_TOUCH (S/open-slippage within Q despite subsequent low<Q), full-liquidity stress and explicit no-fill fallback. Stop limit fractions0.5%,1.0%,1.5%,2.0% as sensitivity ONLY; keep the1.0% placeholder until reviewed.
[ASSUMED: proposal] Measure worst-case planned risk L-Q vs trigger risk L-S, quantity reduction, stop-fill rate, no-fill incident rate, fallback delay/price, probability/amount loss>9800, excess-loss tail p95/p99/max, halted/zero-volume events and15:00 breaches. Same-bar entry+stop uses both feasible paths; compare conservative primary vs alternatives without hiding losses.
[ASSUMED: proposal] Flag ambiguity: O>S,low<Q can permit an earlier S fill or a jump/no-liquidity failure. Real5m data cannot settle this; publish sensitivity interval rather than a single “verified” stop execution claim. Finer independent trade/quote evidence would be needed to validate paths later.
[ASSUMED: proposal] Retain delayed-close/degraded-feed cohorts separately from resting stops. Parameter selection must address tail loss, not falsely certify the planned-risk cap as max realized loss. Freeze chosen formula/version only after review; no production activation implied.

## Phase2 tests-first protocol and mutation protection

[ASSUMED] Proposed names below are future acceptance targets, NOT existing/RAN_TEST evidence. First slice stays a pure no-I/O lifecycle driven by replay; PostgreSQL race is a separate integration gate after that slice, not proof from pure code.
| Future named test | Required assertion / mutation killed |
|---|---|
| [ASSUMED] test_cost_inclusive_limit_to_stop_limit_cap_9800 | literal9800; exact-boundary accepted, one unit/fee increment beyond rejected; L-S shortcut mutant fails |
| [ASSUMED] test_capital_980000_no_leverage | entry notional+fees<=available cash<=980000; larger capital/budget mutant fails |
| [ASSUMED] test_only_long_positive_buy_entry | SELL entry/short/zero-negative q or S>=T rejected; long-only guard removal fails |
| [ASSUMED] test_one_filled_entry_per_ist_day | second fill blocked even after exit/restart; count-on-exit/reset-date mutants fail |
| [ASSUMED] test_five_armed_hard_cap | exactly5 distinct arms accepted,6th rejected; max_armed6 mutation fails, no cap reset via account ID |
| [ASSUMED] test_entry_buffer_formula_v2_fraction_floor_rounding | independent literal expected limits for percent-dominated/floor-dominated/rounding cases; percent/floor/ceil mutants fail |
| [ASSUMED] test_c0_close_strictly_above_prior_three_highs | equality false; one valid tick above true; using C0 high/current last3/include-C0 mutants fail |
| [ASSUMED] test_signal_requires_four_contiguous_current_session_candles | three bars or cross-session prior3 blocked; no unfinished C0 |
| [ASSUMED] test_tick_trigger_and_four_candle_stop | C0 high+tau, min of ALL4 lows-tau; fixed0.05/excludingC0/wrongtick mutants fail |
| [ASSUMED] test_filter_scope_c0_and_prior3_width | proposed filters evaluate C0, width excludes C0; old all-three trend check fails |
| [ASSUMED] test_resting_entry_fills_trigger_candle | arm before open,O<T,H>=T => modeled fill in THAT candle, not next close; open within T..L uses open |
| [ASSUMED] test_gap_through_never_fills_or_rearms | O>L even if later low returns: GAPPED_THROUGH,zero fill,no reprice or auto-rearm |
| [ASSUMED] test_reject_confirmation_at_or_above_t | equality/above rejected; selection timing journaled |
| [ASSUMED] test_cutoff_exchange_open_not_receipt |14:25-opening candle eligible,14:30-opening candle ineligible; timely14:30+receipt can reconcile prior-window fill |
| [ASSUMED] test_no_preconfirmation_or_expired_fill | no use of pre-arm high; C0.close+15min boundary; stale90s/unknown labels held |
| [ASSUMED] test_same_bar_adv_then_security_id_single_fill | reverse arrival same candle -> one deterministic fill/highestADV then ascendingSID; pure interleavings plus retry/restart |
| [ASSUMED] test_protective_gap_inside_vs_below_stop_limit | Q<=open<=S valid bounded open fill; open<Q => STOP_NOT_FILLED |
| [ASSUMED] test_low_below_stop_limit_open_above_conservative | low<Q => no filled stop under conservative model; alternate continuous model separately identified |
| [ASSUMED] test_all_or_nothing_anomaly | suggested partial means zero fill+anomaly; no partial position |
| [ASSUMED] test_entry_stop_same_candle_worst_feasible_path | no optimistic suppression of feasible entry-then-loss; open<=S pre-entry invalidates |
| [ASSUMED] test_stop_cancel_confirm_exit_race_no_short | stop fills during cancel -> no extra sell; unknown cancel -> critical reconciliation,never duplicate |
| [ASSUMED] test_bracket_activated_with_fill | no committed paper entry lacking stop/manager; bracket failure rolls back |
| [ASSUMED] test_ema_stop_be_flatten_precedence | protective stop first;5m EMA before1.5R; BE next-bar;15:00 breach cannot erase |
| [ASSUMED] test_overrides_bounded_and_separate_cohort | preserve original, reject beyond limits/invalid tick/incorrect side/stale; OVERRIDDEN tag |
| [ASSUMED] test_restart_event_authority_and_outage_exit | projection rebuild from events; corrupt chain freezes; no fabricated flat; recovery at valid later price |

[ASSUMED: proposal] Independent expected-value fixtures (not derived by calling implementation helper): T1000,tau0.05 -> L1001.50; T100,tau0.10 -> L100.30 (floor dominates); T333.35,tau0.05 -> L333.90 (ceil). For S990,Q980.10,fees2/share,L1001.50, q418 has limit-risk9781.20; q419 risk9804.60 rejects; q418 trigger-risk5643.00, stop-limit premium4138.20. Mutation protection applies to the pinned placeholder version; an approved future calibration changes config ID AND independent fixtures deliberately, not silent auto-updates.
[ASSUMED: proposal] PostgreSQL target test_pg_unique_fill_atomic_cancels_and_five_slots: independent connections/barrier; one deterministic ENTRY_FILLED; single cash debit/bracket and outbox; other arms cancelled atomically; direct duplicate SQL/sixth slot rejected; injected failure rolls back. Never call pure interleaving a PostgreSQL concurrency test.
[ASSUMED: proposal] Segmented reproducible commands/dependencies/timeboxes remain in BASELINE_AND_REFERENCES.md. No test run attempted on mixed directory. Clean checkout supplied by Mayur must be verified before Phase2 starts.

## Broker-neutral pre-live documentation checklist (no capability asserted)

[ASSUMED] Before ANY live phase, inspect then-current official Dhan documentation and record document URL/date, supported fields/product constraints and sandbox evidence. No current order capability has been verified this round.
1. [ASSUMED] Whether stop-limit ENTRY is supported within Super Orders, or needs standard orders; do not infer capability from product name.
2. [ASSUMED] Whether protective stop leg accepts separate trigger and limit, how modifications/cancel acknowledgments/versioning work and how “stop not filled” is observable.
3. [ASSUMED] Static-IP whitelisting/authentication requirements and whether hosting supplies an approved stable egress IP; no IP/secret values belong in repo.
4. [ASSUMED] Permitted product types/long intraday mode, exchange-specific tick/band validation, order validity, account limits and order-status/fill updates.
5. [ASSUMED] Broker/exchange cutoff/auto-square-off timing versus our14:30/15:00 policy, special sessions/halts/circuit rules and marketable-exit support.
6. [ASSUMED] Failed protective placement AFTER entry fill: independent fill detection, critical unprotected state, freeze entries, confirm actual position, cancel/reconcile conflicting orders and marketable close at valid price. No API success assumed protection.
7. [ASSUMED] Trigger-time sizing for an already resting order: what can be specified before broker acceptance, whether broker-held contingent sizing exists, and whether client emulation would violate the intended resting semantics.
8. [ASSUMED] Multiple live resting stock entries can fill before client cancellation; a paper DB unique index cannot prevent external fills. Require proven broker/exchange mutual exclusion or revised separately approved live architecture before claiming one-entry safety.
[ASSUMED] This is a future verification checklist only: no broker order structure, API endpoint, credential, client library, configuration or order call is added.


## Approved75-slot/manual-CSV amendment:future tests only

[READ_CODE] Automatic gates now expressly agreed by Mayur;manual membership bypasses those gates except verified2%/5%band exclusion. Add route-specific fixtures,not shared “must pass20sessions/price/liquidity” validation.
[ASSUMED] Planned test_manual_band_only_admission:manualIPO price250/history7/lowturnover/band10admits membership while same rowfailsautomatic;band2/5rejected,unknownbandpending. Separate test ensuresno fabricated setup/primary fill on unavailable indicators.
[ASSUMED] Planned test_manual_tminus1_only_and_user_identifier_lineage:server commit boundary,no same-day add/reactivation,CSVidempotency/duplicates,rowerrors,persistent membership/identifier inpool/setup/arm/alert/journal;calendar-vs-trading-day fixture pending Mayur interpretation.
[ASSUMED] Planned test_pool_50auto_25manual_100upload:100manualmembers top25basedavailable daily mean;N7vsN20actual lookback labels;zero-historyunrankable;underfilled pool usesactualcount,no invalid padding. Overlap50+25-5=70unique;50+12=62;no unused manual slots silently reassigned.
[ASSUMED] Planned test_pool_keeps_ipo_membership_while_setup_data_held:ranked IPO withN<20not silently replaced due RVOLwarmup;scan available5mprices with visible holds,not fabricated indicators. Trade tie policy for a future approved short-historysetup requires explicit handling because old20Dtrade-ranking may be undefined.
[ASSUMED] No testcode/replayanalysis executed. Buffer/risk/cutoff/lifecycle tests elsewhere remain applicable. Add IPO/available-history cohorts toreal-data studies;do not blendthemwith20-session systemic evidence.


## IPO alternative design —not executed

[READ_CODE] SeparateIPOpolicy design authorized;see IPO_SHORT_HISTORY_POLICY.md. Futuretests targetCSVpriority/missingpriority,lanequotaarithmetic,N0vsmissingolddata,availableNmatching-slotRVOL,firstday3priorvolumebaseline,20actual5mcloses and3completedHTFrisingcloses,source-timecontracts,cohortlineage andexplicitmixed-historytiehold. No script/testcodeor empirical result added.
[ASSUMED] ExactIPOparameters remain proposed andmustnotbe used toretroactivelydeclare oldSTANDARD20resultsvalid.
