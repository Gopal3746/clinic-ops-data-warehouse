from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from clinic_ops.config import Settings
from clinic_ops.contracts import SOURCE_ENTITIES
from clinic_ops.lake import LakeStorage, get_lake


def fetch_paginated(base_url: str, source: str, entity: str, page_size: int = 500) -> list[dict]:
    records: list[dict] = []
    offset = 0
    while True:
        query = urlencode({"limit": page_size, "offset": offset})
        url = f"{base_url.rstrip('/')}/v1/{source}/{entity}?{query}"
        with urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        records.extend(payload["records"])
        if payload["next_offset"] is None:
            break
        offset = int(payload["next_offset"])
    return records


def _jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in records)


def ingest_snapshot(
    ingest_date: str,
    settings: Settings | None = None,
    lake: LakeStorage | None = None,
) -> list[dict]:
    settings = settings or Settings()
    lake = lake or get_lake(settings)
    manifest_rows: list[dict] = []

    for source, entities in SOURCE_ENTITIES.items():
        for entity in entities:
            records = fetch_paginated(settings.api_base_url, source, entity)
            body = _jsonl(records)
            key = f"raw/{source}/{entity}/ingest_date={ingest_date}/part-00000.jsonl"
            lake.write_text(key, body)
            manifest_rows.append({
                "source": source,
                "entity": entity,
                "ingest_date": ingest_date,
                "object_key": key,
                "row_count": len(records),
                "byte_count": len(body.encode("utf-8")),
                "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "ingested_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                "synthetic_only": True,
            })

    manifest_body = _jsonl(manifest_rows)
    manifest_key = f"_manifests/ingest_date={ingest_date}/manifest.jsonl"
    lake.write_text(manifest_key, manifest_body)
    return manifest_rows
