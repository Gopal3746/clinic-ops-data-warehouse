from __future__ import annotations

import argparse

from clinic_ops.staging import load_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest-date", required=True)
    args = parser.parse_args()
    counts = load_snapshot(args.ingest_date)
    for table, count in counts.items():
        print(f"landing.{table}: {count} rows")


if __name__ == "__main__":
    main()
