from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize selected official Synthea CSV exports into the project's clinical fixture contract."
    )
    parser.add_argument("--synthea-dir", required=True)
    parser.add_argument("--output-dir", default="fixtures")
    args = parser.parse_args()

    src = Path(args.synthea_dir)
    out = Path(args.output_dir)

    patients = pd.read_csv(src / "patients.csv")
    encounters = pd.read_csv(src / "encounters.csv")
    providers = pd.read_csv(src / "providers.csv")
    organizations = pd.read_csv(src / "organizations.csv")

    normalized_patients = [
        {
            "patient_id": f"PAT-SYN-{row.Id}",
            "birth_date": str(row.BIRTHDATE),
            "sex": str(row.GENDER),
            "created_at": f"{row.BIRTHDATE}T00:00:00",
        }
        for row in patients.itertuples(index=False)
    ]

    normalized_clinics = [
        {
            "clinic_id": f"CLN-SYN-{row.Id}",
            "clinic_name": str(row.NAME),
            "city": str(row.CITY),
            "state": str(row.STATE),
            "timezone": "America/New_York",
        }
        for row in organizations.itertuples(index=False)
    ]

    provider_cols = {c.upper(): c for c in providers.columns}
    normalized_providers = []
    for row in providers.to_dict(orient="records"):
        pid = row[provider_cols["ID"]]
        org = row.get(provider_cols.get("ORGANIZATION", ""), "")
        normalized_providers.append({
            "provider_id": f"PRV-SYN-{pid}",
            "clinic_id": f"CLN-SYN-{org}",
            "specialty": str(row.get(provider_cols.get("SPECIALITY", ""), "GENERAL PRACTICE")),
            "employment_type": "synthea_source",
            "weekly_capacity_hours": 32,
            "active_flag": True,
        })

    normalized_encounters = []
    for row in encounters.to_dict(orient="records"):
        normalized_encounters.append({
            "encounter_id": f"ENC-SYN-{row['Id']}",
            "patient_id": f"PAT-SYN-{row['PATIENT']}",
            "provider_id": f"PRV-SYN-{row['PROVIDER']}",
            "clinic_id": f"CLN-SYN-{row['ORGANIZATION']}",
            "payer_id": f"PAY-SYN-{row.get('PAYER', 'UNKNOWN')}",
            "start_ts": str(row["START"]).replace("Z", "+00:00"),
            "end_ts": str(row["STOP"]).replace("Z", "+00:00"),
            "scheduled_duration_minutes": 60,
            "session_type": str(row.get("ENCOUNTERCLASS", "encounter")),
            "status": "completed",
            "base_encounter_cost": float(row.get("BASE_ENCOUNTER_COST", 0) or 0),
        })

    _write(out / "clinical/patients.json", normalized_patients)
    _write(out / "clinical/providers.json", normalized_providers)
    _write(out / "clinical/clinics.json", normalized_clinics)
    _write(out / "clinical/encounters.json", normalized_encounters)

    print("Normalized official Synthea clinical CSVs into fixture contract.")
    print("Note: CRM profile history and finance payer/claim fixtures still need to be generated or supplied.")


if __name__ == "__main__":
    main()
