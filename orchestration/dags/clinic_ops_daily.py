from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from airflow.sdk import dag, get_current_context, task

PROJECT_ROOT = Path(os.getenv("CLINIC_OPS_PROJECT_ROOT", Path(__file__).resolve().parents[2]))
def _run(*parts: str) -> None:
    subprocess.run(parts, cwd=PROJECT_ROOT, check=True)


def _ingest_date() -> str:
    context = get_current_context()
    if context.get("ds"):
        return str(context["ds"])
    logical_date = context.get("logical_date")
    if logical_date is None:
        raise RuntimeError("No Airflow logical date available")
    return logical_date.date().isoformat()


@dag(
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["clinic_ops", "synthetic_healthcare", "portfolio"],
)
def clinic_ops_daily():
    @task
    def ingest() -> None:
        _run("python", "scripts/ingest.py", "--ingest-date", _ingest_date())

    @task
    def load_staging() -> None:
        _run("python", "scripts/load_staging.py", "--ingest-date", _ingest_date())

    @task
    def staging_dq() -> None:
        _run("python", "scripts/run_dq.py", "--phase", "staging", "--ingest-date", _ingest_date())

    @task
    def dbt_build() -> None:
        subprocess.run(
            ["dbt", "build", "--profiles-dir", "."],
            cwd=PROJECT_ROOT / "transform",
            check=True,
        )

    @task
    def mart_dq() -> None:
        _run("python", "scripts/run_dq.py", "--phase", "marts")

    @task
    def write_bi_refresh_flag() -> None:
        output = PROJECT_ROOT / "artifacts" / "bi_refresh_ready.txt"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f"ready_for_refresh={_ingest_date()}\n", encoding="utf-8")

    ingest() >> load_staging() >> staging_dq() >> dbt_build() >> mart_dq() >> write_bi_refresh_flag()


clinic_ops_daily()
