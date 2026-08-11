from __future__ import annotations

import json
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from faker import Faker

SPECIALTIES = [
    "Behavioral Therapist",
    "Occupational Therapist",
    "Speech-Language Pathologist",
    "Psychologist",
    "Pediatrician",
]

SESSION_TYPES = [
    "behavioral_therapy",
    "occupational_therapy",
    "speech_therapy",
    "psychology_followup",
    "pediatric_followup",
]

LANGUAGES = ["English", "Spanish", "Mandarin", "Arabic", "Vietnamese"]
CHANNELS = ["provider_referral", "web", "school_partner", "community_partner", "payer_directory"]
STATES = ["CA", "TX", "NC", "AZ", "CO", "WA"]


def _dt_str(value: datetime | None) -> str | None:
    return value.replace(microsecond=0).isoformat() if value else None


def _date_str(value: date | None) -> str | None:
    return value.isoformat() if value else None


def _write_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def _weighted_choice(rng: random.Random, pairs: list[tuple[Any, float]]) -> Any:
    values, weights = zip(*pairs)
    return rng.choices(values, weights=weights, k=1)[0]


def _profile_at(history: list[dict[str, Any]], patient_id: str, encounter_day: date) -> dict[str, Any]:
    candidates = [
        row for row in history
        if row["patient_id"] == patient_id
        and date.fromisoformat(row["effective_from"]) <= encounter_day
        and (row["effective_to"] is None or encounter_day < date.fromisoformat(row["effective_to"]))
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"Expected one SCD2 row for {patient_id} on {encounter_day}, found {len(candidates)}")
    return candidates[0]


def generate_fixture_bundle(
    output_dir: str | Path = "fixtures",
    patient_count: int = 1200,
    encounter_count: int = 6000,
    seed: int = 42,
    as_of_date: date = date(2026, 8, 10),
) -> dict[str, int]:
    """Generate deterministic synthetic clinic-operations source fixtures.

    All records are synthetic. IDs, locations, payers, dates, and measures are invented.
    """
    output_dir = Path(output_dir)
    rng = random.Random(seed)
    fake = Faker()
    Faker.seed(seed)

    # Finance dimension source first so patient profile history can reference payer IDs.
    payer_names = [
        ("PAY-001", "Evergreen Health Plan", "commercial"),
        ("PAY-002", "Horizon Family Health", "commercial"),
        ("PAY-003", "StateCare Managed Plan", "medicaid_managed"),
        ("PAY-004", "Community Choice Health", "commercial"),
        ("PAY-005", "Direct Self Pay", "self_pay"),
    ]
    payers = [
        {"payer_id": pid, "payer_name": name, "payer_type": ptype}
        for pid, name, ptype in payer_names
    ]

    clinics = []
    for i, state_code in enumerate(STATES, start=1):
        clinics.append({
            "clinic_id": f"CLN-{i:03d}",
            "clinic_name": f"Synthetic Care Center {i}",
            "city": fake.city(),
            "state": state_code,
            "timezone": {
                "CA": "America/Los_Angeles",
                "TX": "America/Chicago",
                "NC": "America/New_York",
                "AZ": "America/Phoenix",
                "CO": "America/Denver",
                "WA": "America/Los_Angeles",
            }[state_code],
        })

    providers = []
    provider_count = max(30, math.ceil(patient_count / 18))
    for i in range(1, provider_count + 1):
        clinic = rng.choice(clinics)
        providers.append({
            "provider_id": f"PRV-{i:04d}",
            "clinic_id": clinic["clinic_id"],
            "specialty": rng.choice(SPECIALTIES),
            "employment_type": _weighted_choice(rng, [("full_time", 0.8), ("part_time", 0.2)]),
            "weekly_capacity_hours": rng.choice([24, 28, 32, 36, 40]),
            "active_flag": True,
        })

    patients = []
    profile_history = []
    base_effective = date(2020, 1, 1)
    for i in range(1, patient_count + 1):
        patient_id = f"PAT-{i:06d}"
        birth_year = rng.randint(2004, 2024)
        birth_day = date(birth_year, rng.randint(1, 12), rng.randint(1, 28))
        patients.append({
            "patient_id": patient_id,
            "birth_date": _date_str(birth_day),
            "sex": rng.choice(["F", "M", "X"]),
            "created_at": _dt_str(datetime.combine(base_effective, datetime.min.time()) + timedelta(days=rng.randint(0, 1800))),
        })

        initial_clinic = rng.choice(clinics)
        initial_payer = rng.choice(payers)["payer_id"]
        changed = rng.random() < 0.22
        if changed:
            change_day = as_of_date - timedelta(days=rng.randint(45, 280))
            profile_history.append({
                "patient_id": patient_id,
                "city": initial_clinic["city"],
                "state": initial_clinic["state"],
                "preferred_language": rng.choice(LANGUAGES),
                "payer_id": initial_payer,
                "effective_from": _date_str(base_effective),
                "effective_to": _date_str(change_day),
                "is_current": False,
            })
            new_clinic = rng.choice(clinics)
            new_payer = rng.choice(payers)["payer_id"] if rng.random() < 0.7 else initial_payer
            profile_history.append({
                "patient_id": patient_id,
                "city": new_clinic["city"],
                "state": new_clinic["state"],
                "preferred_language": rng.choice(LANGUAGES),
                "payer_id": new_payer,
                "effective_from": _date_str(change_day),
                "effective_to": None,
                "is_current": True,
            })
        else:
            profile_history.append({
                "patient_id": patient_id,
                "city": initial_clinic["city"],
                "state": initial_clinic["state"],
                "preferred_language": rng.choice(LANGUAGES),
                "payer_id": initial_payer,
                "effective_from": _date_str(base_effective),
                "effective_to": None,
                "is_current": True,
            })

    patient_ids = [p["patient_id"] for p in patients]
    provider_by_id = {p["provider_id"]: p for p in providers}

    encounters = []
    for i in range(1, encounter_count + 1):
        patient_id = rng.choice(patient_ids)
        encounter_day = as_of_date - timedelta(days=rng.randint(0, 364))
        provider = rng.choice(providers)
        start_hour = rng.randint(8, 16)
        start_minute = rng.choice([0, 15, 30, 45])
        start_dt = datetime.combine(encounter_day, datetime.min.time()).replace(hour=start_hour, minute=start_minute)
        scheduled_minutes = rng.choice([30, 45, 60, 90])
        status = _weighted_choice(
            rng,
            [("completed", 0.82), ("no_show", 0.08), ("cancelled", 0.07), ("rescheduled", 0.03)],
        )
        if status == "completed":
            actual_minutes = max(15, int(rng.gauss(scheduled_minutes, 8)))
            stop_dt = start_dt + timedelta(minutes=actual_minutes)
        else:
            actual_minutes = 0
            stop_dt = start_dt + timedelta(minutes=scheduled_minutes)

        session_type = rng.choice(SESSION_TYPES)
        base_cost = {
            "behavioral_therapy": 185,
            "occupational_therapy": 210,
            "speech_therapy": 205,
            "psychology_followup": 240,
            "pediatric_followup": 175,
        }[session_type]
        profile = _profile_at(profile_history, patient_id, encounter_day)
        encounters.append({
            "encounter_id": f"ENC-{i:08d}",
            "patient_id": patient_id,
            "provider_id": provider["provider_id"],
            "clinic_id": provider_by_id[provider["provider_id"]]["clinic_id"],
            "payer_id": profile["payer_id"],
            "start_ts": _dt_str(start_dt),
            "end_ts": _dt_str(stop_dt),
            "scheduled_duration_minutes": scheduled_minutes,
            "session_type": session_type,
            "status": status,
            "base_encounter_cost": round(base_cost * rng.uniform(0.90, 1.15), 2),
        })

    referrals = []
    referred_patients = rng.sample(patient_ids, min(patient_count, max(300, int(patient_count * 0.72))))
    for i, patient_id in enumerate(referred_patients, start=1):
        referral_day = as_of_date - timedelta(days=rng.randint(0, 364))
        clinic = rng.choice(clinics)
        funnel = _weighted_choice(
            rng,
            [("converted", 0.54), ("intake_scheduled", 0.16), ("contacted", 0.12), ("new", 0.10), ("closed_lost", 0.08)],
        )
        intake_dt = None
        converted_dt = None
        if funnel in {"intake_scheduled", "converted"}:
            intake_dt = datetime.combine(referral_day, datetime.min.time()) + timedelta(days=rng.randint(2, 18), hours=10)
        if funnel == "converted":
            converted_dt = intake_dt + timedelta(days=rng.randint(1, 14)) if intake_dt else None

        referrals.append({
            "referral_id": f"REF-{i:07d}",
            "patient_id": patient_id,
            "clinic_id": clinic["clinic_id"],
            "referral_date": _date_str(referral_day),
            "source_channel": rng.choice(CHANNELS),
            "referral_status": funnel,
            "intake_scheduled_at": _dt_str(intake_dt),
            "converted_at": _dt_str(converted_dt),
        })

    claims = []
    claim_counter = 0
    for encounter in encounters:
        if encounter["status"] != "completed":
            continue

        submitted = datetime.fromisoformat(encounter["end_ts"]) + timedelta(days=rng.randint(0, 4))
        if submitted.date() > as_of_date:
            # Encounter exists, but no claim has been submitted as of the snapshot date.
            continue

        billed = float(encounter["base_encounter_cost"])
        payer_id = encounter["payer_id"]
        payer_type = next(p["payer_type"] for p in payers if p["payer_id"] == payer_id)
        if payer_type == "self_pay":
            allowed = billed
            status = _weighted_choice(rng, [("paid", 0.75), ("pending", 0.20), ("partial", 0.05)])
        else:
            allowed = billed * rng.uniform(0.62, 0.94)
            status = _weighted_choice(rng, [("paid", 0.78), ("pending", 0.10), ("denied", 0.07), ("partial", 0.05)])

        if status == "paid":
            reimbursement = allowed
        elif status == "partial":
            reimbursement = allowed * rng.uniform(0.30, 0.75)
        else:
            reimbursement = 0.0

        paid_at = submitted + timedelta(days=rng.randint(5, 45)) if reimbursement > 0 else None
        if paid_at is not None and paid_at.date() > as_of_date:
            status = "pending"
            reimbursement = 0.0
            paid_at = None

        claim_counter += 1
        claims.append({
            "claim_id": f"CLM-{claim_counter:08d}",
            "encounter_id": encounter["encounter_id"],
            "patient_id": encounter["patient_id"],
            "payer_id": payer_id,
            "submitted_at": _dt_str(submitted),
            "paid_at": _dt_str(paid_at),
            "billed_amount": round(billed, 2),
            "allowed_amount": round(allowed, 2),
            "reimbursement_amount": round(reimbursement, 2),
            "claim_status": status,
        })

    bundle = {
        "clinical/patients.json": patients,
        "clinical/providers.json": providers,
        "clinical/clinics.json": clinics,
        "clinical/encounters.json": encounters,
        "crm/patient_profile_history.json": profile_history,
        "crm/referrals.json": referrals,
        "finance/payers.json": payers,
        "finance/claims.json": claims,
    }
    for relative_path, records in bundle.items():
        _write_records(output_dir / relative_path, records)

    metadata = {
        "synthetic_only": True,
        "seed": seed,
        "as_of_date": as_of_date.isoformat(),
        "patient_count": len(patients),
        "provider_count": len(providers),
        "clinic_count": len(clinics),
        "encounter_count": len(encounters),
        "referral_count": len(referrals),
        "claim_count": len(claims),
        "patient_profile_version_count": len(profile_history),
    }
    _write_records(output_dir / "_metadata.json", [metadata])
    return metadata
