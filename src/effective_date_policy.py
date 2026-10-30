"""Conservative source-to-target effective-date manifest gate.

It does not assert NSE publication conventions. Requires human-reviewed,
source-specific evidence before an exchange restriction can be cleared.
"""
from datetime import date

REQUIRED=("bhavcopy","fo_bhavcopy","price_band_complete",
          "price_band_changes","surveillance")

def validate_manifest(manifest,asof,target):
    if not isinstance(manifest,dict):raise ValueError("Missing source evidence manifest")
    if date.fromisoformat(target)<=date.fromisoformat(asof):
        raise ValueError("Invalid target session")
    if manifest.get("asof_date")!=asof or manifest.get("target_date")!=target:
        raise ValueError("Manifest dates mismatch")
    sources=manifest.get("sources",{})
    decisions={}
    for key in REQUIRED:
        row=sources.get(key)
        if not isinstance(row,dict):
            decisions[key]="HOLD_NO_SOURCE_EVIDENCE"
            continue
        if row.get("source_session")!=asof:
            decisions[key]="HOLD_WRONG_SOURCE_SESSION"
        elif row.get("effective_for_session")!=target:
            decisions[key]="HOLD_EFFECTIVE_DATE_UNVERIFIED"
        elif row.get("evidence_reviewed") is not True:
            decisions[key]="HOLD_REVIEW_REQUIRED"
        elif not isinstance(row.get("sha256"),str) or len(row["sha256"])!=64:
            decisions[key]="HOLD_MISSING_FINGERPRINT"
        else:
            decisions[key]="EVIDENCE_REVIEWED"
    ready=all(v=="EVIDENCE_REVIEWED" for v in decisions.values())
    return {"approval_state":"RESEARCH_ONLY_NO_TRADING",
            "source_evidence_complete":ready,"decisions":decisions,
            "may_place_orders":False}
