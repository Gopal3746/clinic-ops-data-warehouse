from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

from clinic_ops.dq import run_mart_checks, run_staging_checks, write_report
from clinic_ops.ingest import ingest_snapshot
from clinic_ops.staging import load_snapshot
from clinic_ops.synthetic import generate_fixture_bundle


def _wait_for_api(url: str, attempts: int = 40) -> None:
    for _ in range(attempts):
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError("Mock API did not become ready")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest-date", default="2026-08-10")
    parser.add_argument("--patients", type=int, default=1200)
    parser.add_argument("--encounters", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    generated = generate_fixture_bundle(
        patient_count=args.patients,
        encounter_count=args.encounters,
        seed=args.seed,
    )

    env = os.environ.copy()
    env.setdefault("CLINIC_OPS_API_BASE_URL", "http://127.0.0.1:8765")
    api = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "clinic_ops.mock_api:app",
            "--host", "127.0.0.1",
            "--port", "8765",
            "--log-level", "warning",
        ],
        env=env,
    )

    try:
        _wait_for_api("http://127.0.0.1:8765/health")
        manifest = ingest_snapshot(args.ingest_date)
        landing_counts = load_snapshot(args.ingest_date)

        staging_report = write_report(
            run_staging_checks(args.ingest_date),
            "artifacts/dq_staging.json",
        )
        if staging_report["status"] != "pass":
            raise RuntimeError("Staging DQ failed")

        subprocess.run(
            ["dbt", "build", "--profiles-dir", "."],
            cwd="transform",
            check=True,
        )

        mart_report = write_report(
            run_mart_checks(),
            "artifacts/dq_marts.json",
        )
        if mart_report["status"] != "pass":
            raise RuntimeError("Mart DQ failed")

        report = {
            "verified_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "synthetic_only": True,
            "generated": generated,
            "manifest_entities": len(manifest),
            "landing_counts": landing_counts,
            "staging_dq": staging_report["status"],
            "mart_dq": mart_report["status"],
            "dbt_build": "pass",
        }
        Path("artifacts").mkdir(exist_ok=True)
        Path("artifacts/verification_report.json").write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(report, indent=2))
    finally:
        api.terminate()
        try:
            api.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api.kill()


if __name__ == "__main__":
    main()
