from __future__ import annotations

import argparse
import sys

from clinic_ops.dq import run_mart_checks, run_staging_checks, write_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["staging", "marts"], required=True)
    parser.add_argument("--ingest-date")
    args = parser.parse_args()

    if args.phase == "staging":
        if not args.ingest_date:
            parser.error("--ingest-date is required for staging checks")
        checks = run_staging_checks(args.ingest_date)
        output = "artifacts/dq_staging.json"
    else:
        checks = run_mart_checks()
        output = "artifacts/dq_marts.json"

    report = write_report(checks, output)
    for check in checks:
        print(f"[{check.status.upper()}] {check.name}: {check.observed} ({check.expected})")
    print(f"Report: {output}")
    if report["status"] != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
