# Audit packet —2026-11-01 / IPO follow-up design
## a. Session summary
[ASSUMED] BAD NEWS:IPOpriorityallocation/indicator/tieparametersunapproved,localbaselineUNKNOWN,noempiricalIPOanalysis.
[READ_CODE] Mayur reaffirmedT-1,requestedalternativeN0ranking,authorizedshort-historyIPOdesign.
[READ_CODE] D037/D038approveddirection;P021..023exactdefaultsproposed.
[READ_CODE] Parenta0ea658c1eff12fbb33df184879e6c6a8733685b;branch codex/phase1-review-round2;11Markdownfiles.
[READ_CODE] Phase2NOTSTARTED;noapp/test/broker/deploy/cron/Renderaction.

## b. Safety invariants
[READ_CODE] PASS diff-only:PREVIEW_ONLY/app pathsuntouched;no brokerordercode/endpoint/client/credential.
[RAN_TEST] PASS limitedcredential/private-URLscan:11proposedMarkdownfiles,0matches.
[ASSUMED] UNVERIFIED:repo-widesecretabsence,actualruntime/Renderstate.
[ASSUMED] UNVERIFIEDcurrenttests:9800risk,980000cash,long-only,dailyfill,fivearms,limitformula.
[READ_CODE] PASSscope:legacyfiles/config/workflow/deploy/cronuntouched.
[ASSUMED] IPOuniverseexceptiondoesnotwaivetraderisk/cutoff/stop-failurelosssemantics.

## c. Traceability delta
[READ_CODE] D037/D038andP021..023DESIGNED;no TESTED/DEPLOYEDpromotion.
[READ_CODE] D033T-1reaffirmed;calendar-mappingnotexplicitlyapproved.
[READ_CODE] NewIPOprofile/rankingproposalslinkedfromcanonicalcontract/overview/testplan.

## d. Deviations,risks,assumptions
[ASSUMED] CSVpriorityisdiscretion,notliquidity;5IPOslotallocationwithmanual25isproposed,notuser-approved.
[ASSUMED] Available-sessionRVOLandcurrent3barvolumearestatisticallydifferentfromSTANDARD20.
[ASSUMED] ReducedHTF3risingcloseconfirmationisaproposedstrategyvariant,notexistingEMA20proof.
[ASSUMED] Firstdayneeds20actual5mclosesandverifiedinstrument-sessionstart;no syntheticIPOprice/historyseed.
[ASSUMED] Mixedhistorytiecanlack20DADV;defaultproposalholds,tiealternativeneedsreview.
[READ_CODE] No currentnew-test,replay,source-capability,capacityorprofitabilityclaim.
[READ_CODE] Priorprogressprefixretained;useranswersnotstretchedintoexactparameter/Phase2approval.

## e. Unverified claims
[ASSUMED] No realIPOdataset/firstdayranking/profileoutcome/Telegram/supervisiontest.
[ASSUMED] ActualRenderstateunverifiablebyCodex;localbaselineUNKNOWN.
[ASSUMED] T-1calendarvstrading-sessionmappingstillneedsresolutionbeforeimplementation.
[ASSUMED] CurrentDhan/marketIPOstart/tick/bandcapabilitynotverifiedhere.

## f. Test results
[ASSUMED] ApplicationtestsNOTRUN;commandnone;pass/fail/skips/durationN/A.
[RAN_TEST] functions.exec docvalidator:11Markdownpaths,append-onlylog,38currentDIDs,packet<=120lines,31coveragerows.
[RAN_TEST] Hypotheticallaneallocations<=25manual/75totalchecked;notruntime/invarianttests.
[RAN_TEST] Credential/private-URLscan0matches;noapplicationtestcodeadded.

## g. Numbered open choices
[ASSUMED] 1. AcceptCSVpriorityandproposed5IPOslotreservation/flexiblemanualquota?
[ASSUMED] 2. Acceptavailable-sessionRVOLandfirstdayprior3volume/20closes/3HTFrisingcloseprofile?
[ASSUMED] 3. Choosecomparablemixed-historytiebreakbeforeallowingcompetingIPOprimaryentries;currentproposalholds.
[ASSUMED] ExactT-1calendar mappingstillpending;no same-day additionsunderanyinterpretation.

## h. Suggested next step / auditor first paths
[ASSUMED] ReviewIPOdefaults;cleancheckout/baselineandexplicitPhase2approvalremainseparate.
[READ_CODE] First5:IPO_SHORT_HISTORY_POLICY.md;UNIVERSE_AND_POOL_CONTRACT.md;REPLAY_ANALYSIS_AND_TEST_PLAN.md;../audit/DECISIONS.md;../audit/PROGRESS_LOG.md(design-relative).

## Coverage map — paths relative to docs/design/; coverage means designed, NOT tested
| Phase1 item | Document and section |
|---|---|
| [READ_CODE] a Lifecycle | LIFECYCLE_AND_ATOMICITY.md — Event envelope and transitions |
| [READ_CODE] b Time windows | TIME_AND_EXECUTION.md — Cutoff by exchange candle window |
| [READ_CODE] c Shelf life/noise | LIFECYCLE_AND_ATOMICITY.md — Selection contract; JOURNAL_ALERTS_RECOVERY.md — Telegram |
| [READ_CODE] d Selection | LIFECYCLE_AND_ATOMICITY.md — Selection contract and override bounds |
| [READ_CODE] e Multi-arm/SQL | LIFECYCLE_AND_ATOMICITY.md — Database guarantees and same-candle ties |
| [READ_CODE] f Limit/AON/sizing | TIME_AND_EXECUTION.md — Resting entry; Protective stop; Sizing |
| [READ_CODE] g Replay correction | TIME_AND_EXECUTION.md — Replay correction; REPLAY_ANALYSIS_AND_TEST_PLAN.md |
| [READ_CODE] h Precedence/halt | TIME_AND_EXECUTION.md — Sizing/precedence; JOURNAL_ALERTS_RECOVERY.md — Failure matrix |
| [READ_CODE] i Exact setup | SETUP_AND_UNIVERSE.md — Side-by-side change map; Exact preserved calculations |
| [READ_CODE] j Shadow | JOURNAL_ALERTS_RECOVERY.md — Shadow tracking without selection bias claims |
| [READ_CODE] k Catalysts | SETUP_AND_UNIVERSE.md — Persistent manual catalysts |
| [READ_CODE] l TradingView | JOURNAL_ALERTS_RECOVERY.md — TradingView links and test cases |
| [READ_CODE] m Journal | JOURNAL_ALERTS_RECOVERY.md — Round2 additions; Authoritative schemas |
| [READ_CODE] n Scaling | SETUP_AND_UNIVERSE.md — Scaling; Hybrid universe/p95 gate |
| [READ_CODE] o Supervision/failures | JOURNAL_ALERTS_RECOVERY.md — Independent supervision; Failure matrix |
| [READ_CODE] p Telegram | JOURNAL_ALERTS_RECOVERY.md — Telegram alert contract; stop-failure critical row |
| [READ_CODE] q Flow | README.md — Updated flow |
| [READ_CODE] r PR drift/Render | ../NEXT_WORK_PLAN.md; ../PROJECT_HANDOFF.md — latest checkpoint |
| [READ_CODE] R2-1 Strategy comparison | SETUP_AND_UNIVERSE.md — Side-by-side change map |
| [READ_CODE] R2-2 Fill/cutoff/risk | TIME_AND_EXECUTION.md — all execution sections |
| [READ_CODE] R2-3 Same-candle atomicity | LIFECYCLE_AND_ATOMICITY.md — transitions; Database guarantees |
| [READ_CODE] R2-4 Replay measurement | REPLAY_ANALYSIS_AND_TEST_PLAN.md — Buffer and selection evidence; Stop sensitivity |
| [READ_CODE] R2-5 Overrides | TIME_AND_EXECUTION.md — Sizing on stop limit overrides and precedence |
| [READ_CODE] R2-6 Acceptance restored | ../NEXT_WORK_PLAN.md — Restored acceptance checks |
| [READ_CODE] R2-7 Sole base | LIFECYCLE_AND_ATOMICITY.md — Authoritative Phase2 base |
| [READ_CODE] R2-8 Clone/setup | BASELINE_AND_REFERENCES.md — Clone failure explanation and clean checkout handoff |
| [READ_CODE] R2-9 Mutation/new tests | REPLAY_ANALYSIS_AND_TEST_PLAN.md — Phase2 tests-first protocol |
| [READ_CODE] R2-10 Audit coverage | ../audit/AUDIT_PACKET.md — this coverage map |

| [READ_CODE] Universe/pool definition refinement | UNIVERSE_AND_POOL_CONTRACT.md — sections1–7 |

| [READ_CODE] ManualT-1CSV and75-slot amendment | UNIVERSE_AND_POOL_CONTRACT.md sections1–7;REPLAY_ANALYSIS_AND_TEST_PLAN.md amendment tests |

| [READ_CODE] IPO ranking/short-historyfollow-up | IPO_SHORT_HISTORY_POLICY.md sections1–5 |

