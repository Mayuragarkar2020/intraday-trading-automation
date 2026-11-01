# Universe and scanning pool — two admission routes and fixed75-slot design

[READ_CODE] Mayur's latest instruction supersedes earlier same-filter manual admission,20-member manual cap,25-systematic pilot and same-day catalyst additions. This is Phase1 documentation only;no implementation/Phase2/activation.
[ASSUMED] Universe membership,scanning membership,indicator readiness,qualified setup and armed trade remain different states. Manual admission exemptions do NOT waive approved setup,risk,position or fill rules.

## 1. Universe admission routes

| Route | Membership conditions | Provenance |
|---|---|---|
| [READ_CODE: Mayur-approved] Automatic | ALL automatic gates below,from Dhan/NSE source inputs | universe_source=systematic |
| [READ_CODE: Mayur-approved] Manual discretionary CSV | No2%/5% band;automatic price/20-session/turnover/volume/restriction screening thresholds are NOT admission conditions for this route | universe_source=manual_catalyst;user identifier preserved |

[ASSUMED: operational clarification] Both routes need a resolvable NSE stock identity and verified band to apply the requested rule. Unknown identity/band remains PENDING_VALIDATION,not an asserted pass;this is identification/proof of the band condition,not an additional liquidity filter. No invented band for a newly listed IPO.
[READ_CODE: Mayur-approved] Manual IPO/news/earnings candidates may be outside300–5000,have<20sessions or fail automatic liquidity gates and still belong to manual U if the band condition is satisfied.
[ASSUMED] Trade/data readiness is separate from membership:halted/not-tradable/missing data cannot produce a fabricated fill;all manual trades still need a valid setup,quote/tick/SL/override checks,<=9800 planned risk,<=980000cash,long only,one daily fill,<=5arms and cutoffs. Do not quietly reapply the automatic300–5000 guard to manual confirmation/entry.
[ASSUMED] Restriction/surveillance flags may be displayed on a manual stock;under this amendment they are not an automatic-route exclusion reused as a manual admission rule. Actual execution feasibility/prohibitions remain a separate explicit hold,not hidden deletion.

## 2. Automatic gates — all approved by Mayur

| Condition | Requirement |
|---|---|
| [READ_CODE] NSE series | EQ |
| [READ_CODE] Reference closing price |300–5000 INR inclusive |
| [READ_CODE] History |20completed trading sessions through T-1 |
| [READ_CODE]20D average daily traded value |>=100Cr |
| [READ_CODE]20D median daily traded value |>=50Cr |
| [READ_CODE] Latest completed-session traded value |>=75Cr |
| [READ_CODE] Latest/20D average |>=0.75 |
| [READ_CODE] Lowest daily traded value,last5 sessions |>=30Cr |
| [READ_CODE] Volume |Positive in all20sessions |
| [READ_CODE] Bands/status |Exclude2%/5% and restricted stocks;unknown status/identity HOLD |

[READ_CODE] Sources are Dhan Data API plus NSE inputs;no performance calibration or current source certification is implied. The universe is uncapped:all passing automatic names plus band-valid manual memberships,by canonical identity.
[ASSUMED] Keep dated source originals/hashes,canonical ISIN/security ID,symbol and rule/config revision. A research HOLD row is not a final validated automatic member. No filtering by C0/EMA/news merely for automatic universe inclusion.
[READ_CODE] Hybrid evening provisional/pre09:15 revalidation remains the approved timing. Automated revalidation is allowed on trading day;user same-day additions are not.
[ASSUMED: route-isolation proposal] Publish route-specific validity:auto daily-history failure holds automatic admission,not a hidden20-day gate on otherwise band-valid manual names. Manual route needs its own validated final revision;shared identity/band/feed failures hold affected names. Never reclassify an automatic failure as manual without a valid prior-day user upload;show missing automatic coverage explicitly.

## 3. Manual CSV contract and T-1 gate

[READ_CODE: Mayur-approved] Add manual stocks by CSV one day before the intended trading day;NO same-day manual entry. Persist user-provided identity/identifier throughout universe,pool,setup,selection,arm,intents,alerts,trade and journal.
[ASSUMED: proposed schema] CSV columns:target_session_date,symbol,user_identifier,reason_type,note;optional ISIN/security_id/listing_date. Server resolves canonical identity;CSV cannot set eligibility flags,rank,price history,risk or source attestations. reason_type supports IPO/NEWS/EARNINGS/OTHER;user_identifier required,nonempty,display-safe text;note retained with audit trail. No credentials/URLs containing secrets.
[ASSUMED: proposed example] Header:target_session_date,symbol,user_identifier,reason_type,note. Placeholder row example:2026-11-02,EXAMPLE,IPO-watch,IPO,Discretionary candidate. This is format-only,not a real security or upload.
[ASSUMED: proposed timing interpretation] “One day prior” defaults to previous CALENDAR day in Asia/Kolkata,including Sunday for Monday,from00:00 up to target-day00:00 exclusive. Calendar target must be an exchange session. Whether Mayur instead means the previous TRADING session remains an explicit question;no same-day addition under either interpretation.
[ASSUMED] Validate admission at server commit time as well as upload-start;an upload begun23:59 but committed after00:00 target day is rejected SAME_DAY_MANUAL_ENTRY_NOT_ALLOWED. No client-clock/date workaround. Additions,reactivation and identifier-changing uploads cannot alter current-day membership;return row-level errors and no silent rollover.
[ASSUMED: proposal] Accepted rows receive immutable membership_id/upload_id/row hash,target session,uploaded_at,actor,user_identifier,note,band-evidence state. Proposed idempotency=(account,target_session,upload hash);canonical duplicate stock rows cannot create duplicate memberships;conflicting identifiers require explicit pre-session correction. Preserve original and revised versions,never silently overwrite history.
[READ_CODE] Existing persistence intent remains:membership stays until user removal;daily band revalidation;failure visibly suspended;30day review reminder. No20- or25-stock upload/membership cap:25 is a SCANNING quota,not a maximum upload count. A100-stock CSV is a supported design case.
[ASSUMED] No same-day additions;removal/cancel for risk control remains allowed and journaled. Removing a manual reason does not stop protection for an open position;systematic membership may independently retain scanning. Same-day uploads cannot “reactivate” or replace held stocks;next target's T-1 gate applies.

## 4. Pool quotas and cohort ranking

[READ_CODE: Mayur-approved] Initial pool CAPACITY75 = up to50automatic + up to25manual. Rank within cohorts independently;use fewer if fewer available. No automatic/manual eligibility rule conflation.
[ASSUMED: proposed precise metric] Automatic score=mean daily traded value over latest20completed sessions. Manual score=mean daily traded value over latest min(20,N) verified COMPLETED listed trading sessions available through T-1,where N>=1. Metric in INR/Cr;include verified zero-turnover sessions;do not cherry-pick active days.20+history =>same20D metric;short history =>explicit available-history mean.
[READ_CODE] Manual use of average available daily liquidity when20sessions unavailable is approved;no automatic100/50/75Cr thresholds imposed on manual candidates.
[ASSUMED: operational proposal] Rank descending average daily traded VALUE,then numeric security ID ascending as stable tie-break. Persist score,lookback session count,source dates,latest date,history completeness and ranking version. Missing expected source files are DATA_MISSING,not zero;unrankable rows remain visible in U,not assigned invented score.
[ASSUMED] Select first min(50,automatic ranked count) and first min(25,manual ranked count). Pool=P_auto UNION P_manual by canonical identity. Do not displace top-ranked selected manual IPO merely because its setup warm-up is incomplete;keep pool membership with SETUP_DATA_HOLD and process its available5m behavior. Missing data stays a visible hold,not silent replacement by the next name.
[ASSUMED] Cross-cohort overlap fetches/scans once,with source_provenance containing both flags and manual identifier still prominent. No duplicate arm/fill/journal. Example:50automatic+25manual-5overlap =>70unique instruments. Quotas are maxima,no hidden backfill/lending to force75unique.
[ASSUMED] If12manual rows available,manual pool12,not25;with50automatic/no overlap total62. If100manual rows rankable,top25scan and75remain MANUAL_ELIGIBLE_NOT_SCANNED_CAPACITY with rank/reason. A stock outsideP has not failed the setup;it was not monitored by setup scanner.
[ASSUMED] Systematic/manual rank revisions freeze before09:15;no same-day CSV-induced rotation. Status/feed failures are suspended/held visibly and do not hide missing coverage. Existing arms/positions retain required management feeds even if pool membership changes.
[READ_CODE] Scan every5m interval09:15–14:35;post14:30 newly surfaced setups remain hidden/shadow per existing cutoff rule. Up to75capacity is an approved target,not measured throughput. Prior measured complete-sweep p95<=60s no-trade gate remains for verification/any further expansion;if75cannotmeet safety/freshness,hold new trading and report rather than silently reduce quotas.

## 5. IPO edge cases — membership is not qualification

[ASSUMED] N=0 completed sessions =>average daily liquidity undefined. Keep a band-valid IPO in manual U as RANK_PENDING_ZERO_HISTORY;do not invent yesterday's turnover or treat offer size/IPO demand as daily traded value. Default:no rankable pool place until a ranking policy for zero-history names is approved. This technical edge case awaits Mayur;it is not a new universe admission threshold.
[ASSUMED] Short-history N1..19 ranks on available completed-day mean,but current approved RVOL construction expects20 matching prior5m slots and EMA/15m warm-up. Such a name remains in the selected manual pool with explicit SETUP_DATA_HOLD if required indicators cannot be computed. It is monitored separately;no fabricated qualified setup.
[ASSUMED] First-listing-day IPO may have no prior slots/EMA/HTF at all;4current candles alone cannot satisfy every existing indicator rule. Changing RVOL to available-session baseline or other IPO-specific warm-up is a separate strategy proposal requiring Mayur. Do not silently waive setup conditions because manual universe entry bypasses automatic liquidity thresholds.
[ASSUMED] Pre-listing unknown mapping/band can be stored as CSV pending intent onT-1;final universe admission waits for verified identity/band. No same-day new upload is needed to revalidate an existing pending membership. Distinguish NEW_ENTRY from automated validation.

## 6. Cockpit,provenance and data schema

[READ_CODE: Mayur-approved] Separate Automatic Universe and Manual Discretionary Universe views,with a prominent user identifier for every manual candidate throughout its journey. Show counts for memberships vs unique instruments,manual ranking/selected/not-scanned/suspended/indicator-held states.
[ASSUMED: proposal] Manual record fields:membership/upload/row IDs,target session,canonical identity,symbol,universe_source,user_identifier,reason_type,note,uploaded_at/actor,band evidence/status,active/suspended/removed timestamps,rank score/lookback/selected/reason,pool revision. Carry immutable membership/user label snapshot into each setup/confirmation/trade;later edits cannot rewrite past attribution.
[ASSUMED] Setup/trade journal includes strategy_source/systematic_member/manual_member,user_identifier/upload lineage,liquidity_lookback_sessions,ranking version,available-history/IPO flags,SETUP_DATA_HOLD reasons and time buckets. No statistical blending of manual/IPO/overridden cohorts with systematic20-day samples.
[ASSUMED] Row readiness/coverage is distinct from0signals. Expose expected unique pool count vs attempted/held/scanned counts,last candle and data ages;manager/clock priority stays separate. Daily membership revalidation cannot disable protective exits.
[ASSUMED] Future acceptance tests:automatic thresholds all;manual250INR/N7 fails auto but band10admits manual;unknown/2%/5%band blocks verified admission;T-1 server-boundary upload/retry/persistence;identifier throughout;100manualtop25;N7vsN20 score/lookback;N0unrankable;50+25overlap arithmetic;underfilled quota;no warm-up fabrication/no same-day additions. Tests are targets only.

## 7. Approval/open implementation details

[READ_CODE] Mayur approves automatic gates,manual band-only route/exemptions,CSV/pre-day-only addition,persistent displayed identifier,and75capacity split50/25 with liquidity ranking/available-history fallback. Earlier same-filter/manual20cap/intraday-add and25-auto proposals are superseded.
[ASSUMED] Exact CSV columns/idempotency,calendar-day vs previous-session interpretation,ranking tie/overlap treatment and zero-history/short-indicator-history behavior remain proposed. No Phase2,app/test/config/broker/deploy/cron/Render change;local baseline UNKNOWN,actual Render state unverifiable by Codex.
