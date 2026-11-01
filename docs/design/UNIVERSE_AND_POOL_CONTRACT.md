# Universe and scanning pool — precise contract for review

[ASSUMED] Phase1 docs-only proposal; exact selection/freeze/readiness rules below await Mayur. Existing approved universe safety filters,hybrid timing,initial25–50 range,<=5 arms and measured scale gate are preserved. No Phase2 or runtime change.

## 1. Five different sets

| Set | Exact meaning | Membership authority |
|---|---|---|
| [ASSUMED] Raw stock scope R | NSE ordinary cash-equity candidates with verified security classification and instrument mapping | Source/security masters;no setup condition |
| [ASSUMED] Eligible universe U | EVERY candidate passing current-session eligibility and historical liquidity gates | System evaluates objective rules;no target count |
| [ASSUMED] Scanning pool P | Capacity-limited eligible names whose source/reference history is ready and which will actually be scanned | Deterministic automatic ranking plus explicit eligible manual membership |
| [ASSUMED] Qualified setups Q | Pool observations whose completed C0 meets the approved signal/filters and is actionable before cutoff | Scanner;Q is a set of setup records,not just stock names |
| [ASSUMED] Armed attempts A | Qualified setups explicitly confirmed by Mayur and accepted by validation | Mayur;maximum5;no confirmation means no primary trade |

[ASSUMED] Open primary positions<=1 by single daily filled-entry rule. U is not the same as P or Q; a lack of setup does not remove a stock from U. A stock can produce multiple historical setup records but at most one active arm per symbol.
[ASSUMED] Universe eligibility is a necessary condition,not an execution guarantee: fresh quote,spread/impact/full fill feasibility,tick/risk/stop checks still apply at confirmation/trigger. Daily turnover does not certify intraday spreads or queue liquidity.

## 2. Universe eligibility — no arbitrary universe size

[READ_CODE] Current baseline config/universe.yaml and screening.py define these historical gates. They are existing defaults,not replay-calibrated profitability claims:
| Gate | Precise check |
|---|---|
| [READ_CODE] Series | NSE EQ in current config |
| [READ_CODE] Reference price | Last completed session close300<=price<=5000 INR |
| [READ_CODE] History | Exactly20 distinct completed exchange sessions through T-1,in order,same ISIN |
| [READ_CODE] Mean traded value |20-session mean turnover>=100Cr |
| [READ_CODE] Median traded value |20-session median turnover>=50Cr |
| [READ_CODE] Latest traded value |T-1 turnover>=75Cr |
| [READ_CODE] Activity ratio |T-1 turnover/20-session mean>=0.75 |
| [READ_CODE] Last-five floor |Each of latest5 sessions turnover>=30Cr |
| [READ_CODE] Volume |All20 sessions volume>0 |
| [READ_CODE] Restrictions defaults |Exclude2%/5% bands and ASM/GSM;unknown restriction/mapping holds |

[ASSUMED: proposed scope clarification] R means ordinary equity shares,not an accidental inclusion of ETF/fund/debt/preference/warrant instruments merely because a source reports EQ. Verify instrument type/series/segment and supported order-lot identity; unsupported/unknown class holds out. No SME or other segment is silently included by a name match. This is a proposed classification safeguard,not a claim of existing implementation.
[ASSUMED] Admission to FINAL U additionally requires dated/effective current-session band/restriction/trading status,single unambiguous NSE identity/ISIN-to-Dhan security ID,valid tick/lot and supported cash-equity tradability. Allowed band class must be explicitly verified (10%,20%,or genuinely verified no-fixed-band policy); never infer safety from an F&O/name heuristic.2%/5% always out;unknown data HOLD.
[ASSUMED] Persist each gate input/date/source/hash/result and reason. Liquidity pass with eligibility HOLD is a research candidate,NOT a final U member. One stock has one canonical identity;symbol changes do not create duplicate membership.
[ASSUMED] U is as large or small as the gates produce. Do not lower thresholds to fill25/50 slots. Initial price gate uses T-1 reference close; intended entry price/runtime risk validation remains separate. No EMA,C0,RVOL,news or current breakout is required merely to belong to U.

## 3. Hybrid daily publication and fail-safe

[READ_CODE] Approved D-008 requires evening provisional list,pre09:15 revalidation,and scanning from final validated list.
[ASSUMED] Provisional T list uses only20 completed sessions available through T-1;missing official files =>PROVISIONAL_INCOMPLETE. Revalidate source effective dates/identity/bands/restrictions/ticks before09:15. Publish immutable universe_revision and pool_revision with source/config hashes.
[ASSUMED] A stale/provisional list is never substituted for final U. Required-source failure or late whole final publication =>no new scan/arming/entry that session under the current conservative design;visible UNIVERSE_FINAL_NOT_READY. Known per-stock failures are individually excluded/held,not fabricated as healthy.
[ASSUMED] Preserve old revisions and explicit exclusion/HOLD rows. Intraday status deterioration suspends new activity for that symbol;it does not disable the protective feed/manager for an already-open position. Position management has priority over universe/pool maintenance.

## 4. Who chooses the pool and how

[ASSUMED: proposal P-014] The SYSTEM chooses systematic membership;Mayur chooses trades later. Proposed initial N=25,within approved25–50 range. Raising N—including25to50—requires measured complete-sweep p95<=60s in no-trade observation;no automatic scale-up without that gate.
[ASSUMED: proposal P-015] Sort eligible U by frozen20-day mean traded value DESC,then numeric security ID ASC. This is a capacity/liquidity policy,NOT a strategy-quality ranking and not evidence of better profits. Warm reference candles/EMA/20 matching RVOL slots/HTF for candidates before pool finalization. Among eligible data-ready names take first min(N,count ready);record any higher-ranked skipped name with DATA_NOT_READY.
[ASSUMED] Daily ranking uses T-1 completed evidence only. Do not rank by future performance,current C0 or retrospective winner. Configuration records N,rank version,gate thresholds,data readiness and session revision.
[ASSUMED] If only12 names qualify and are ready,scan12;do not add13 failing names. If100 qualify but N25,75 are ELIGIBLE_NOT_SCANNED_CAPACITY,not excluded/unqualified. Show both universe rank and actual pool rank;no undisclosed sampling.
[ASSUMED] Capacity omission means missed possible setups elsewhere in U. Long-term goal can be broader U coverage once measured capacity supports it;25/50 is an initial operational limit,NOT a permanent strategy restriction.

## 5. Manual catalysts and total pool count

[ASSUMED: proposal P-016] Let S=topN eligible,data-ready systematic stocks;M=active eligible,data-ready manual catalyst names. Actual scanned pool P=S UNION M,by canonical identity. Manual membership can ensure coverage of an otherwise unscanned eligible stock;it never grants an eligibility exception.
[READ_CODE] Existing D-016 design keeps manual entries until removal,with daily revalidation,visible suspension,30-day review reminder and about20 entries. Hard cap20 including suspended entries remains a previously proposed precise implementation choice.
[ASSUMED] Systematic count and catalyst count are separate:with N25 and20 nonoverlapping catalysts,total45;N50 and20,total70. Duplicates fetch/scan once. Benchmark ACTUAL deduplicated total P with management priority—not N alone. Do not secretly cut catalysts or lower systematic count to conceal overload;hold admissions/entries visibly and resolve capacity before use.
[ASSUMED] Preserve source_provenance flags for both memberships. Confirmed manual-catalyst setup uses universe_source=manual_catalyst and systematic_member flag where applicable;single event/outcome,not double journal counting.
[ASSUMED] Adding a manual name intraday requires the same dated eligibility/liquidity checks,current-session data continuity and all warm-up before it can scan;otherwise PENDING_VALIDATION/SUSPENDED. Publish audited overlay revision,not a bypass of failed initial final-U publication or retroactive signal evidence.
[ASSUMED] Removing manual membership removes that reason;the stock can remain scanned if it is already a systematic member. Explain this in UI. Cancel affected unfilled manual arms with reason;already-open position remains managed until exit. No automatic replacement trade.

## 6. Freeze, failures and visibility

[ASSUMED: proposal P-017] Freeze systematic pool before09:15 for that session;no automatic intraday rotation into next-ranked stocks. Record suspension/data failures without silently shrinking expected coverage. Fully validated user catalyst additions/removals are explicit versioned exceptions,not hidden churn.
[ASSUMED] A pool member with a missing/stale candle has SCAN_HELD/DATA_GAP,not “no setup”. Quote/tick/source hold prevents new arm/entry. Whole-source failure =>global new-trade hold;incomplete armed interval prevents winner resolution. Unfilled attempts/positions follow separate lifecycle recovery rules.
[ASSUMED] Cockpit sections/counts:Raw scope;Eligible universe;Held/excluded with reasons;Scanning pool;Eligible not scanned;Qualified setups;Armed;Open position. Publish last successful interval,expected vs scanned/held count and source age,so quiet market differs from broken scanner.
[ASSUMED] Every U candidate stores session,canonical identity,pass/HOLD/exclusion reasons,20day metrics/source dates,band/restriction/tick status,universe revision. Pool membership adds rank/N/version,systematic/manual provenance,warm-up status,selected_at,suspension and NOT_SELECTED_CAPACITY reason.
[ASSUMED] Hypothetical example ONLY:U100,S25,M8 with3overlap =>P30;U70 not scanned. Qualified4 andarmed2 are independent later counts,not current observed project data.
[ASSUMED] Active arms are normally members of P;retain feeds for any existing position even if suspended/removed. Subscription/request budget counts unique(P UNION arms UNION open-position instruments),not P+5 automatically.
[ASSUMED] Future acceptance tests:exact gate boundaries/no unknown admission;deterministic ranking/input permutations;N25 plus catalyst dedup;no-padding small U;ranked-name readiness holds;no intraday silent rotation;revalidation fail-safe;manual suspension/removal;visible unscanned universe;coverage denominator and scale gate. No test implemented/run here.

## 7. Approval checkpoint

[ASSUMED] New exact rules P-014..017 remain PROPOSED. Review proposal:initial25 automatic ADV-ranked systematic names plus all eligible catalyst members,explicit readiness/visibility and frozen session membership;expand only after measured gate. Existing liquidity thresholds shown above are implementation defaults;their strategy suitability has not been empirically established.
[ASSUMED] No Phase2,application/config/deployment/cron/Render/broker change or measured capacity claim. Local baseline UNKNOWN;actual Render state unverifiable by Codex.
