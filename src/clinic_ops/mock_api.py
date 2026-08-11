from __future__ import annotations

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Synthetic Clinic Ops Source APIs",
    description="Synthetic-only mock third-party APIs for portfolio ingestion practice.",
    version="1.0.0",
)

FIXTURE_ROOT = Path(os.getenv("CLINIC_OPS_FIXTURE_ROOT", "fixtures"))

ROUTES = {
    ("clinical", "patients"),
    ("clinical", "providers"),
    ("clinical", "clinics"),
    ("clinical", "encounters"),
    ("crm", "patient_profile_history"),
    ("crm", "referrals"),
    ("finance", "payers"),
    ("finance", "claims"),
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_classification": "synthetic_only"}


@app.get("/v1/{source}/{entity}")
def get_records(
    source: str,
    entity: str,
    limit: int = Query(default=500, ge=1, le=2000),
    offset: int = Query(default=0, ge=0),
) -> dict:
    if (source, entity) not in ROUTES:
        raise HTTPException(status_code=404, detail="Unknown source/entity")

    path = FIXTURE_ROOT / source / f"{entity}.json"
    if not path.exists():
        raise HTTPException(
            status_code=503,
            detail=f"Fixture not generated: {path}. Run scripts/generate_synthetic_sources.py first.",
        )

    records = json.loads(path.read_text(encoding="utf-8"))
    page = records[offset: offset + limit]
    next_offset = offset + limit if offset + limit < len(records) else None
    return {
        "source": source,
        "entity": entity,
        "records": page,
        "offset": offset,
        "limit": limit,
        "total": len(records),
        "next_offset": next_offset,
        "synthetic_only": True,
    }
