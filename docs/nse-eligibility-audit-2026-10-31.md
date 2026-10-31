# Official NSE eligibility audit — 31 October 2026

## Result

The earlier 106-name reference pool is reduced to **103 research candidates**. This is not a tradable universe; approved trading count remains zero.

| Security | Finding | Outcome |
|---|---|---|
| WELCORP | NSE long-term ASM Stage I, source dated 30 October; Dhan had shown clear | EXCLUDED_NSE_ASM |
| TECHM | Candidate/master ISIN INE669C01036; corporate-action feed uses INE669C01028 | HOLD_NSE_IDENTITY_CONFLICT |
| SHRIRAMFIN | Candidate/master ISIN INE721A01047; corporate-action feed uses INE721A01013 | HOLD_NSE_IDENTITY_CONFLICT |
| ESDS | NSE long-term ASM Stage I; already excluded from the previous 106 pool for a 5% band | Remains excluded |

Do not map the conflicting corporate-action records by symbol alone or assume adjustment factors. Reinstatement requires reconciling identities and event history with official evidence.

## Evidence

The official website JavaScript for the NSE ASM and GSM report pages identifies the public reportASM and reportGSM endpoints. Both endpoints were fetched successfully with HTTP 200 on 31 October 2026 at approximately 12:05 IST. Every surveillance row supplies an as-on date of 30 October 2026.

- Long-term ASM: 144 source rows. One duplicated AAATECH restriction has the same symbol, ISIN, stage and date but different company-name capitalization. The parser records that duplicate and retains one restriction.
- Short-term ASM: 47 rows.
- GSM: 77 rows.
- No GSM or short-term ASM match was found among the earlier 106 candidates. The only long-term ASM match in that pool is WELCORP.
- ESDS also matches long-term ASM, but was already outside that pool.
- [Saved parsed responses](../research/2026-10-30/nse-eligibility-evidence.json) preserve endpoint URLs, retrieval timestamps, original-response SHA-256 and canonical-payload SHA-256. The latter verifies the saved parsed payload during replay. Original raw response bytes are not embedded.
- [Updated candidate CSV](../research/2026-10-30/candidates.csv) includes surveillance evidence, corporate-action records and review statuses.
- [Updated snapshot](../research/2026-10-30/universe.json) retains all 109 liquidity candidates, including exclusions and holds.

These are snapshots of the exchange lists as observed, not verification of their continued applicability on 2 November or any later date. Source dates are checked individually. Missing endpoints, malformed payloads, inconsistent hashes, future dates, undated empty lists and conflicting duplicate restrictions fail processing. Stale or mixed source dates cannot establish an absent-match result for the snapshot date.

## Corporate actions

The NSE corporate-action endpoint was queried from 1 October through 2 November 2026. It returned 78 records. Six records match candidate symbols:

| Symbol | Ex-date | Subject | Identity review |
|---|---|---|---|
| HCLTECH | 16 October | Interim dividend INR 12/share | ISIN matches |
| ICICIAMC | 21 October | Interim dividend INR 30/share | ISIN matches |
| TECHM | 23 October | Interim dividend INR 15/share | ISIN conflict — hold |
| LTM | 23 October | Interim dividend INR 25/share | ISIN matches |
| SHRIRAMFIN | 29 October | Interim dividend INR 6.50/share | ISIN conflict — hold |
| COLPAL | 2 November | Interim dividend INR 24/share | ISIN matches; event on intended session |

No structural action was returned for these candidate identities in that requested interval. This is an observed response, not proof of completeness. Announcement broadcast times are null in these records, so point-in-time backtest eligibility is not established. No adjusted price, volume or indicator values are manufactured. Event-bearing histories remain flagged for indicator review; dividend records are not automatically treated as violations of the original liquidity rules.

## Reproduce or refresh

Use the existing dated snapshot as input in a disposable cloud/CI workspace:

```sh
python -m scripts.audit_universe_eligibility --snapshot research/2026-10-30/universe.json --evidence research/2026-10-30/nse-eligibility-evidence.json --output output/replayed_universe.json
python -m scripts.audit_universe_eligibility --snapshot research/2026-10-30/universe.json --evidence output/new_nse_evidence.json --output output/refreshed_universe.json --fetch
```

The fetch path contacts only the three public NSE endpoints. Existing evidence cannot be overwritten using --fetch. Report output is replaced atomically after successful validation. This command does not schedule itself or update the deployed cockpit.

Replaying identical evidence is idempotent. Original reference statuses are retained separately so repeat audits do not lose the evidence of broker/NSE disagreement or compound exclusions.

## Remaining release boundary

The branch is ready for a research-only cockpit release after final CI passes. Deploying it requires Mayur's approval. It adds no Render service and performs no database mutation. The scheduled Dhan research service remains RELIANCE-only. Target-date eligibility, full calendar completeness, ISIN conflicts, corporate-action adjustments and Dhan chart reconciliation remain separate gates before trading clearance.
