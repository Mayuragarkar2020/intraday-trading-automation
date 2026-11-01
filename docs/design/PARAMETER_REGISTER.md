# Parameter register — Phase1 close-out
[READ_CODE; D-047] No application/config changes. Every entry describes design status; “approved” requires the linked Mayur decision. UNSET inputs fail closed; synthetic test fees are not production tariffs.
[ASSUMED; D-047] Owners below are proposed workflow ownership: Mayur approves strategy/operational values; Codex prepares evidence; official-source values require effective-date verification,not discretion.
| Input | Current value | Owner | How set / evidence needed | Status / decision |
|---|---|---|---|---|
| [READ_CODE] Entry buffer | ceil_tick(T+max(0.15%T,3ticks)) | Mayur;Codex analysis | Authentic5m replay0.10/0.15/0.25/0.40% plus floor;fill/gap/tail/cohort results | PLACEHOLDER D-006 |
| [READ_CODE] Stop buffer | Q=floor_tick(S*(1-1%)) | Mayur;Codex analysis | Stop failure/tail-loss sensitivity0.5/1/1.5/2%;review | PLACEHOLDER D-021,D-027 |
| [ASSUMED] Buy/sell/exit slippage | UNSET; adverse direction,tick rounded;withinL/Q for limits | Mayur;Codex evidence | Observed quotes/trades;separate normal/stress/marketable exit;no guessed value | OPEN D-019,D-029 |
| [ASSUMED] Participation | UNSET percentage;full quantity or zero | Mayur;Codex evidence | Tradable volume/depth evidence and AON sensitivity;bar volume not queue proof | OPEN P-025,D-012 |
| [READ_CODE] Fee schedule | UNSET;no numeric tariff guessed | Official tariff/levies;Codex verifies | Component sources below,date/product/side/base/cap/rounding;independent fixtures | DOCUMENTED-ONLY D-022,D-045 |
| [ASSUMED] Quote freshness | <=5s proposed | Mayur | Feed latency/clock-skew observation and review | PROPOSED P-024 |
| [ASSUMED] Validation candle / last-interval receipt age | <=90s proposed | Mayur | Measured complete-sweep/receipt delays;no stale-entry optimism | PROPOSED P-024,D-018 |
| [READ_CODE] Setup lifetime |15min afterC0close | Mayur | Boundary tests;not performance calibration | APPROVED D-005 |
| [READ_CODE] Pool quotas |50auto+25manual,totalcapacity75 | Mayur | Measured no-trade complete-sweep p95<=60s;not yet measured | APPROVED target D-020,D-034 |
| [READ_CODE] IPO pool allocation |k=min(I,max(5,25-min(H,25)),25) | Mayur | Permutation/underfill tests;experimental cohort observation | APPROVED provisional D-039,D-041 |
| [READ_CODE] Tick/source identity | Instrument effective tick;UNVERIFIED live mapping | Official NSE/Dhan reference;Codex verifies | Date-effective symbol/ISIN/SID/series/tick mapping including IPO/special names | DOCUMENTED-ONLY D-026,D-043 |
| [READ_CODE] Tradability sources | NSE source set below;exact ingestion contract UNSET | NSE;Codex validates | Effective-date samples,schemas,completeness/status flags/reconciliation | DOCUMENTED-ONLY D-043 |
| [READ_CODE] Upload window |previous exchange-session close to23:59 calendarT-1 | Mayur | Exchange calendar/special sessions/timezone fixtures;proposed end-exclusiveT00:00 | APPROVED D-042 |
| [READ_CODE] Risk/cash/arms/dailyfill |9800includingcosts/980000/no leverage/5/1 | Mayur | Independent boundary/mutation tests;DB constraints later | APPROVED D-002,D-022,D-047 |
| [READ_CODE] Distance/overrides |(T-S)/T<=2.5%;deltas<=max(0.1%T0,2ticks),T>=T0,S<=S0 | Mayur | Independent decimal/tick boundary fixtures | APPROVED D-025,D-028 |
| [READ_CODE] Indicators |5mEMA10/20,VWAP,RVOL1.2;15mtrend;prior3width2.5% | Mayur | Source-session boundaries,seed/aggregation fixtures;actual warm-up detail | APPROVED D-024,D-040 |
| [READ_CODE] IPO substitutes |availableNmatchingRVOL orN0prior3volume;20actual5mcloses;3completed15mrisingcloses | Mayur | No fabricated history;separate replay/forward cohorts | APPROVED provisional D-040 |
| [ASSUMED] Cash reservations |sum frozen paper-arm entry budgets<=cash | Mayur | Arm-time multi-arm/cancel/fill/restart fixtures | PROPOSED P-026 |
| [READ_CODE] Mixed-profile tie |standard wins whenADV20unavailable;IPOCSVpriority | Mayur | Cross-profile permutation tests | APPROVED D-044 |
| [ASSUMED] Equal/missing IPO priority tie |equal=>SID proposed;missing=>visiblehold proposed | Mayur | Explicit approval;N1..19CSVpriority availability | PROPOSED P-026 |
| [ASSUMED] Early flatten |14:50 intent for15:00deadline | Mayur | No guaranteed closure;latency/failure observation | PROPOSED;deadline APPROVED D-047 |
| [ASSUMED] Alerting/watchdog |alive08:55/absence09:05;heartbeat30s,warn90s,critical600s;event5s,qualified60s | Mayur | Independent outage/Telegram-down drills;measured latency | PROPOSED P-008;10min intent D-014 |
| [ASSUMED] Noise/retention |setup1/symbol/15min,total5/min,snooze30min;raw receipts90days proposed | Mayur | Load/notification/storage review;criticalalerts never snoozed | PROPOSED D-010,D-015 |
| [ASSUMED] Timestamp/source contract |normalized[open,close);unknown labels hold | Codex verifies;Mayur reviews | Independent candle examples incl PR7 issue/session calendar | UNVERIFIED D-018 |
| [ASSUMED] Counterfactual shadow selection |separate accounts;explicit synthetic arm delay/cohort | Mayur;Codex analysis | Do not imply actual user timing for unselected setup | PROPOSED P-009,D-045 |
## Tradability sources [READ_CODE; D-043]
[READ_CODE: documented-only] Official NSE source catalogue read2026-11-01; individual daily files,parsers and broker intraday permissions NOT verified.
| Required fact | Official source to use | Verification still needed |
|---|---|---|
| [READ_CODE] Identity/series/active status | https://www.nseindia.com/static/market-data/securities-available-for-trading — equity list and active CM securities; https://www.nseindia.com/all-reports — CM MII Security File | Effective target date,ISIN/symbol/series joins;absence does not prove tradable |
| [READ_CODE] Rolling settlement/TFT exclusions | https://www.nseindia.com/static/regulations/movement-securities-periodic-review and dated exchange surveillance/circular notices | Current applicable BE/TFT/equivalent restrictions;series whitelist reviewed from evidence,not guessed from symbol alone |
| [READ_CODE] Suspension/limited trading | https://www.nseindia.com/regulations/listing-compliance plus dated exchange notices and security status | Noncompliance and corporate-action suspensions are not exhaustive from one list;intraday change handling |
| [READ_CODE]2%/5% bands | https://www.nseindia.com/all-reports — price-band changes and current security file;daily price-band review | Reconstruct complete target-day band,not just change rows;missing baseline/contradiction=>HOLD |
[ASSUMED; D-043] Store source URL/publication/effective session/hash/retrieved_at/parser version and allow/hold reason. Revalidate daily before09:15 and hold on known status change;never silently delete. Dhan instrument/market data cross-checks identity/prices,not sole authority for NSE restrictions.
[ASSUMED; D-043] Candidate status gates may exclude many first-listing IPOs;IPOpolicy never overrides TFT/suspension/band gates. Exact applicable IPO segment must be established from dated files.
## Fee sources — no tariff numbers pinned [READ_CODE; D-022,D-045]
[READ_CODE: documented-only] Dhan official pricing https://dhan.co/pricing/ and calculator https://dhan.co/calculators/brokerage-calculator/ identify equity-intraday charge components;pricing-page direct fetch timed out,search indexed text read. Neither is a verified executable fee fixture.
| Component | Official source to verify before pinning | Evidence/rounding required |
|---|---|---|
| [READ_CODE] Brokerage | Dhan pricing,download-centre tariff and applicable account tariff | Per-executed-order basis,cap/minimum/product,buy/sell applicability,effective date |
| [READ_CODE] NSE exchange charges/IPFT | https://nsearchives.nseindia.com/content/circulars/FA73061.pdf plus any subsequent NSE circular;cross-check Dhan current tariff | Cash segment/effective date,both-side bases,IPFT treatment;do not assume this circular remains latest |
| [READ_CODE] STT | https://www.nseindia.com/static/invest/first-time-investor-sebi-turnover-fees-stt-other-levies and effective Finance Act/tax notification linked or independently verified | Intraday non-delivery equity,sell/buy applicability,rounding and trade/day aggregation |
| [READ_CODE] GST | Same NSE official levies page,applicable CBIC notification and Dhan tariff | Taxable component base incl brokerage/exchange/SEBI/IPFT treatment;rounding |
| [READ_CODE] SEBI fees | Same NSE official levies page and current SEBI fee regulation/circular | Effective cash-equity turnover fee,both-side base/rounding |
| [READ_CODE] Stamp duty | Same NSE official levies page,Indian Stamp Act/collection notification and Dhan tariff | Buy-side non-delivery classification,rate/base/rounding |
[ASSUMED; D-022,D-045] Codex must reconcile source conflicts with effective-dated primary documents;Mayur reviews pinned schedule. Save component source/effective date/hash,rounding scope and independent hand-calculated cases;future contract-note reconciliation is separate,not current evidence. No assumed zero fees.
[ASSUMED; D-045] Slice1 may test injected synthetic fee functions distinctly labelled TEST_FIXTURE_ONLY;real arm eligibility stays blocked until fee version and other required inputs verified. No external data/order I/O inside pure module.
