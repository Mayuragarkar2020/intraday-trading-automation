"""Fetch official detailed Dhan instrument master to a local research file."""
import argparse
import json
from src.source_verification import fetch_dhan_master

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/raw/dhan-detailed.csv")
    args = p.parse_args()
    print(json.dumps(fetch_dhan_master(args.output), indent=2))

if __name__ == "__main__":
    main()
