from __future__ import annotations

import io
import json
from pathlib import Path

import duckdb
import pandas as pd

from clinic_ops.config import Settings
from clinic_ops.contracts import LANDING_TABLES
from clinic_ops.lake import LakeStorage, get_lake


def _read_jsonl(text: str) -> pd.DataFrame:
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return pd.DataFrame(rows)


def load_snapshot(
    ingest_date: str,
    settings: Settings | None = None,
    lake: LakeStorage | None = None,
) -> dict[str, int]:
    settings = settings or Settings()
    lake = lake or get_lake(settings)
    settings.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(settings.warehouse_path))

    con.execute("create schema if not exists landing")
    con.execute("create schema if not exists ops")

    row_counts: dict[str, int] = {}
    for (source, entity), table_name in LANDING_TABLES.items():
        key = f"raw/{source}/{entity}/ingest_date={ingest_date}/part-00000.jsonl"
        frame = _read_jsonl(lake.read_text(key))
        view_name = f"tmp_{table_name}"
        con.register(view_name, frame)
        con.execute(f"create or replace table landing.{table_name} as select * from {view_name}")
        con.unregister(view_name)
        row_counts[table_name] = len(frame)

    manifest_keys = lake.list_keys("_manifests")
    manifest_rows: list[dict] = []
    for key in manifest_keys:
        if key.endswith("manifest.jsonl"):
            text = lake.read_text(key)
            manifest_rows.extend(json.loads(line) for line in text.splitlines() if line.strip())

    manifest_df = pd.DataFrame(manifest_rows)
    con.register("tmp_manifest", manifest_df)
    con.execute("create or replace table ops.ingestion_manifest as select * from tmp_manifest")
    con.unregister("tmp_manifest")
    con.close()
    return row_counts
