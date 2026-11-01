# IPO ranking and short-history setup policy — proposed review defaults

[READ_CODE] Mayur reaffirmedT-1manual entry,requested another ranking method forzero-historyIPO,and authorized DESIGN of a separate short-history policy. This does NOT approve the exact lane allocation or indicator substitutes below. Phase2 not started.
[ASSUMED] No empirical ranking/strategy result,data validation or current-capacity claim. Universe admission stays manual band-only;setup/risk/order guards remain independent.

## 1. T-1 and CSV

[READ_CODE] User entry remainsT-1for trading dayT;no new manual additions onT. Existing accepted memberships may revalidate onTwithout being a new upload.
[ASSUMED] The answer repeatsT-1but does not explicitly resolve precedingcalendar-day vs precedingtrading-session calendar mapping. Keep that exact mapping pending before implementation;do not silently claim Sunday/Friday approved. No same-day entry under either interpretation.
[ASSUMED: proposal] Add manual_priority (positive integer,1highest) toT-1CSV forzero-historyIPO;retain user_identifier,reason_type=IPO,note,verified listing date/identity/band. Ranking priority and membership edits freeze underT-1gate;no same-day backdoor through metadata.
[ASSUMED] Distinguish real newly listed N0 from an older stock whose price files are missing. Missing old data does not qualify as IPO history. Listing identity/date must be verifiable to use this special model.

## 2. Zero-history ranking — no invented liquidity

[READ_CODE] ForN>=1completed sessions,manual ranking remains average available completed-day traded value,with explicit lookback. ForN0,there is no historical daily average.
[ASSUMED: proposed alternative] Use a discretionary PRIORITY_IPO lane forband-valid,verified first-listing-day stocks:ascending CSVmanual_priority,then numericsecurityID. This is user-declared priority,NOT a liquidity estimate and not comparable to ADV in currency.
[ASSUMED: proposal] Keep totalmanual scanning quota25. Let I=number ofrankable priorityIPOs and H=number ofavailable-history manual names. Proposed IPOallocation k=min(I,max(5,25-min(H,25)),25);historyallocation=min(H,25-k). This reserves up to5manual slots forpriorityIPOs whenhistorycohort isfull;lets IPOs use more slots ifhistorynames arefewer;unusedIPOslots return tohistorycohort.
[ASSUMED] Allocation examples:100history+8IPOs =>20history+5IPOs;100history+2IPOs =>23history+2IPOs;10history+30IPOs =>10history+15IPOs;0history+30IPOs =>25IPOs. Always<=25manual,plus<=50automatic,beforecross-cohortdedup. Five IPOslots is a PROPOSED allocation,unrelated to the separate maximum5armed trades.
[ASSUMED: proposal] Missing CSVpriority=>PRIORITY_REQUIRED,not an invented liquidity score. Default priority must be explicitly supplied beforeT. Rank/exclusion/lane/priority/allocation version visible in cockpit. Othermanualnames remain liquidity-ranked within theirlane.
[ASSUMED] This changes only zero-history selection,not automatic50ranking. A fixed lane allocation avoids mixing incompatible priority/rupee scores and prevents silent intraday reranking from first-day turnover spikes. Final allocation requires Mayur approval.
[ASSUMED] No same-day newstock entry;feed observations revalidate an existingT-1record. Missing band/identity alwayspending;rankingpriority cannot overrideband,setuporriskguard. No real subscription/poolchange now.

## 3. Setup profiles by available verified history

| Profile | Relative-volume baseline |5mEMA |15mconfirmation |
|---|---|---|---|
| [ASSUMED: unchanged] STANDARD20 |20prior matchingtime slots |ExistingEMA10/20warm-up |Existing21+completed15mbars,risingEMA10/20 |
| [ASSUMED: proposed] IPO_AVAILABLE_DAYS (N1..19) |Mean matching slot over ALL Nverified completed prior sessions;zero-volume observations retained;mean<=0/missingrequiredslot HOLD |Use verified available prior+current closes;need>=20closes |Use standard21+HTF rule ifready;otherwise proposed IPO3close alternative |
| [ASSUMED: proposed] IPO_LISTING_DAY (N0) |C0volume/mean volume of the3preceding completedcurrent-session5mbars |Need>=20completedcurrent-sessioncloses;SMAseed thenEMA recurrence,no IPOissue-price syntheticseed |Require>=3completed15mbars;last3closes strictly rising |

[ASSUMED: proposal] Same RVOLthreshold>=1.2but different denominators are NOT equivalent signals;label the profile/baseline/count and analyze cohorts separately. Never claim these substitutes are the approved standard20-day strategy.
[ASSUMED: proposal] FirstdayHTF substitute:latest completed15mclose>previous>previous-previous,latestnotfuture/stale beyond15min. No EMA20/slope claim when21HTFbars absent. At>=21completedHTFbars switch only through explicit version/profile event,not retroactive recomputation of old setups.
[ASSUMED] All other rules retained:C0strictclose>prior3highs;prior3width<=2.5%;C0close above5mEMA10/EMA20/sessionVWAP;EMA10>EMA20;ticktrigger/4candleSL;15minlife;maxdistance2.5%;validatedoverride;restingentry/protection,AON,plannedL-Qrisk<=9800/capital980000/onefilledentry/day/fivearms/cutoffs.
[ASSUMED: proposal] VWAPstarts at the instrument's VERIFIEDcontinuous-sessionstart on listing day. Do not assume everyIPOhas anordinary09:15opening or manufacture missingbars. FirstdayEMA20requires20actualcompleted5mbars(100tradingminutes);a valid4-candlepricepatternalone is notqualified. Example only:ifverifiedstart09:15,twentiethclose10:55;if10:00,twentiethclose11:40. Actual listing-sessioncontract not verified here.
[ASSUMED] Source/history validators must be profile-aware,never set existingfalseverificationflags true just to passIPOdata. Gap/unknownsession/tick/quote or inadequatewarm-up=>SETUP_DATA_HOLD,whilepoolmembershipandprice monitoringremainvisible. Stale signals cannotarmretroactively afterwarm-up.

## 4. Selection,risk,trade ties and lineage

[ASSUMED: proposal] Carry IPOprofile/listingdate,N,RVOLdenominator/count,EMA/HTFwarm-up,rankinglane/priority,source andmanualuseridentifier into everysetup/selection/arm/fill/shadow/journal. Cockpit prominentlylabels IPO_EXPERIMENTAL_PROFILE,withdatastatus;no blending with STANDARD20performance.
[ASSUMED: proposal] Armedsame-candleties need comparablemetric whenanycandidateN0. Do NOTmixCSVpriority and20Dtradedvalue inone orderedfield. Defaultuntilanexplicitpolicyapproved:hold primarysimultaneousmixed-historytie as TIE_METRIC_UNAVAILABLE,shadowrecordall;single eligiblecandidatewithvalidIPOprofile canproceed onlyafterprofileapproval/implementation.
[ASSUMED] Alternative futuretiebreak coulduse measuredcurrent-sessionliquidity forALLarmedcandidates withinthatIPOprofile session;that wouldchange approvedD003and needs specificreview. No automaticpriorityoverride ofalreadyapprovedstockselectionoronefillrule.
[ASSUMED] No guaranteeoflowgaploss orprofitfromnewIPOprofiles. Stop-limitfailure/marketablefallback/circuitsholdand15:00breachsemanticsremainidentical.

## 5. Validation and open choices

[ASSUMED] Futuretests:priorityrankpermutations/missingpriority,N0versusmissingolddata,laneallocationunder/overfill/dedup,historyN1..19matchingbaseline,firstdayprior3volumeexcludingC0,zero/missingslots,20actualcloses/3completeHTFbars,verifiedsessionstart,profiletaglineage,mixed-tiehold,no risk/cutoffwaiver.
[ASSUMED] Replay/observation compare STANDARD20 vs IPO_AVAILABLE_DAYS vs IPO_LISTING_DAY;report qualification/fill/already-broken/stopfailure/excessloss by age/priority/history/timebucket. Current-session3barvolume and3closeHTFare unvalidated research hypotheses,not calibrated replacements.
[ASSUMED] Reviewchoices:approveCSVprioritywithproposed5-slotIPOreservation/flexiblemanualquota? approveavailable-sessionRVOLandfirstdayprior3RVOL/20closes/3HTFcloses? selectamixed-historytrade-tiepolicy? settlecalendarT-1mappingbeforeimplementation. Allare exactproposals;userapproveddesigninganalternative,nottheseparameters.
