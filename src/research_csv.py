"""Export only current research-pool rows; retain dates and verification status."""
import csv
import io
from src.universe_store import validate_report

def export_research_csv(payload):
    report=validate_report(payload["snapshot"])
    output=io.StringIO(newline="")
    writer=csv.writer(output)
    writer.writerow(["target_date","asof_date","mode","source","target_matches_today",
                     "symbol","isin","dhan_security_id","close","avg_turnover_20d_cr",
                     "median_turnover_20d_cr","last_turnover_cr","min_turnover_5d_cr",
                     "activity_ratio","reference_band","review_status","execution_enabled"])
    def safe(value):
        text=str(value)
        return "'"+text if text.startswith(("=","+","-","@")) else text
    for row in report["candidates"]:
        if row["reference_review_status"]!="HOLD_EFFECTIVE_DATE_AND_SURVEILLANCE":
            continue
        metrics=row["metrics"]
        writer.writerow([safe(value) for value in [
            report["target_date"],report["asof_date"],report["mode"],payload["source"],
            payload.get("target_matches_today",False),row["symbol"],row["isin"],
            row["dhan_security_id"],metrics["close"],metrics["avg_turnover_20d_cr"],
            metrics["median_turnover_20d_cr"],metrics["last_turnover_cr"],
            metrics["min_turnover_5d_cr"],metrics["activity_ratio"],
            row["reference_price_band"],row["reference_review_status"],False]])
    return output.getvalue()
