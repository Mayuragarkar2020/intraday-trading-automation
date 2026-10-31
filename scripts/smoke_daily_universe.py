"""Read public sources and round-trip a research universe in a temporary test store."""
import argparse
import json
from pathlib import Path
import tempfile
from src.daily_universe_refresh import build_daily_universe
from src.universe_store import UniverseStore

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-date",required=True)
    args=parser.parse_args()
    report,evidence=build_daily_universe(args.target_date)
    with tempfile.TemporaryDirectory(prefix="universe_smoke_") as directory:
        store=UniverseStore("sqlite:///"+str(Path(directory)/"test.db"))
        store.initialize()
        published=store.publish(report,evidence)
        loaded=store.latest(args.target_date)
        if loaded["snapshot"]!=report or loaded["revision"]!=published["revision"]:
            raise ValueError("Research snapshot round-trip mismatch")
    print("LIVE_RESEARCH_SMOKE "+json.dumps({
        "target_date":report["target_date"],"asof_date":report["asof_date"],
        "sources_downloaded":len(evidence["public_sources"]),
        "summary":report["summary"],"config_sha256":report["config_sha256"],
        "execution_enabled":False,"tradable_count":0,"round_trip":"MATCH"}))

if __name__=="__main__":
    main()
