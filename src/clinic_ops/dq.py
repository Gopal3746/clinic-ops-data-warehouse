from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import duckdb

from clinic_ops.config import Settings
from clinic_ops.contracts import LANDING_TABLES


@dataclass
class CheckResult:
    name: str
    status: str
    observed: float | int | str
    expected: str
    severity: str = "error"


def _scalar(con, sql: str):
    return con.execute(sql).fetchone()[0]


def _result(name: str, observed, expected_predicate: bool, expected: str, severity: str = "error") -> CheckResult:
    return CheckResult(
        name=name,
        status="pass" if expected_predicate else "fail",
        observed=observed,
        expected=expected,
        severity=severity,
    )


def run_staging_checks(ingest_date: str, settings: Settings | None = None) -> list[CheckResult]:
    settings = settings or Settings()
    con = duckdb.connect(str(settings.warehouse_path), read_only=True)
    checks: list[CheckResult] = []

    for (source, entity), table_name in LANDING_TABLES.items():
        current = _scalar(con, f"select count(*) from landing.{table_name}")
        manifest = _scalar(
            con,
            f"""
            select row_count
            from ops.ingestion_manifest
            where source = '{source}' and entity = '{entity}' and ingest_date = '{ingest_date}'
            order by ingested_at_utc desc
            limit 1
            """,
        )
        checks.append(_result(
            f"manifest_row_count::{source}.{entity}",
            current,
            current == manifest,
            f"equals manifest row_count ({manifest})",
        ))

        previous = con.execute(
            f"""
            select row_count
            from ops.ingestion_manifest
            where source = '{source}' and entity = '{entity}' and ingest_date < '{ingest_date}'
            order by ingest_date desc, ingested_at_utc desc
            limit 1
            """
        ).fetchone()
        if previous:
            prev_count = previous[0]
            ratio = current / prev_count if prev_count else 1.0
            checks.append(_result(
                f"row_count_delta::{source}.{entity}",
                round(ratio, 4),
                0.50 <= ratio <= 2.00,
                "current/previous between 0.50 and 2.00",
                severity="warning",
            ))

    null_key_checks = {
        "clinical_patients.patient_id": "select count(*) from landing.clinical_patients where patient_id is null",
        "clinical_providers.provider_id": "select count(*) from landing.clinical_providers where provider_id is null",
        "clinical_clinics.clinic_id": "select count(*) from landing.clinical_clinics where clinic_id is null",
        "clinical_encounters.encounter_id": "select count(*) from landing.clinical_encounters where encounter_id is null",
        "crm_referrals.referral_id": "select count(*) from landing.crm_referrals where referral_id is null",
        "finance_claims.claim_id": "select count(*) from landing.finance_claims where claim_id is null",
    }
    for name, sql in null_key_checks.items():
        observed = _scalar(con, sql)
        checks.append(_result(f"not_null::{name}", observed, observed == 0, "0 null keys"))

    duplicate_checks = {
        "clinical_patients.patient_id": "select count(*) - count(distinct patient_id) from landing.clinical_patients",
        "clinical_providers.provider_id": "select count(*) - count(distinct provider_id) from landing.clinical_providers",
        "clinical_clinics.clinic_id": "select count(*) - count(distinct clinic_id) from landing.clinical_clinics",
        "clinical_encounters.encounter_id": "select count(*) - count(distinct encounter_id) from landing.clinical_encounters",
        "crm_referrals.referral_id": "select count(*) - count(distinct referral_id) from landing.crm_referrals",
        "finance_claims.claim_id": "select count(*) - count(distinct claim_id) from landing.finance_claims",
    }
    for name, sql in duplicate_checks.items():
        observed = _scalar(con, sql)
        checks.append(_result(f"unique::{name}", observed, observed == 0, "0 duplicate keys"))

    ri_checks = {
        "encounter_patient": """
            select count(*) from landing.clinical_encounters e
            left join landing.clinical_patients p on e.patient_id = p.patient_id
            where p.patient_id is null
        """,
        "encounter_provider": """
            select count(*) from landing.clinical_encounters e
            left join landing.clinical_providers p on e.provider_id = p.provider_id
            where p.provider_id is null
        """,
        "encounter_clinic": """
            select count(*) from landing.clinical_encounters e
            left join landing.clinical_clinics c on e.clinic_id = c.clinic_id
            where c.clinic_id is null
        """,
        "claim_encounter": """
            select count(*) from landing.finance_claims c
            left join landing.clinical_encounters e on c.encounter_id = e.encounter_id
            where e.encounter_id is null
        """,
        "claim_patient": """
            select count(*) from landing.finance_claims c
            left join landing.clinical_patients p on c.patient_id = p.patient_id
            where p.patient_id is null
        """,
        "claim_payer": """
            select count(*) from landing.finance_claims c
            left join landing.finance_payers p on c.payer_id = p.payer_id
            where p.payer_id is null
        """,
        "referral_patient": """
            select count(*) from landing.crm_referrals r
            left join landing.clinical_patients p on r.patient_id = p.patient_id
            where p.patient_id is null
        """,
        "profile_patient": """
            select count(*) from landing.crm_patient_profile_history h
            left join landing.clinical_patients p on h.patient_id = p.patient_id
            where p.patient_id is null
        """,
    }
    for name, sql in ri_checks.items():
        observed = _scalar(con, sql)
        checks.append(_result(f"referential_integrity::{name}", observed, observed == 0, "0 orphan rows"))

    con.close()
    return checks


def run_mart_checks(settings: Settings | None = None) -> list[CheckResult]:
    settings = settings or Settings()
    con = duckdb.connect(str(settings.warehouse_path), read_only=True)
    checks: list[CheckResult] = []

    landed = _scalar(con, "select count(*) from landing.clinical_encounters")
    fact = _scalar(con, "select count(*) from marts.fct_encounters")
    checks.append(_result("fact_grain::encounter_row_count", fact, fact == landed, f"equals landed encounters ({landed})"))

    dupes = _scalar(con, "select count(*) - count(distinct encounter_key) from marts.fct_encounters")
    checks.append(_result("fact_grain::encounter_key_unique", dupes, dupes == 0, "0 duplicate encounter keys"))

    null_fks = _scalar(
        con,
        """
        select count(*) from marts.fct_encounters
        where patient_key is null or provider_key is null or clinic_key is null
          or payer_key is null or encounter_date_key is null
        """,
    )
    checks.append(_result("fact_integrity::foreign_keys_not_null", null_fks, null_fks == 0, "0 null required FKs"))

    negatives = _scalar(
        con,
        """
        select count(*) from marts.fct_encounters
        where billed_amount < 0 or allowed_amount < 0
           or reimbursement_amount < 0 or outstanding_amount < 0
        """,
    )
    checks.append(_result("financials::non_negative", negatives, negatives == 0, "0 negative financial measures"))

    current_dupes = _scalar(
        con,
        """
        select count(*) from (
          select patient_id
          from marts.dim_patient
          where is_current
          group by patient_id
          having count(*) > 1
        )
        """,
    )
    checks.append(_result("scd2::one_current_row", current_dupes, current_dupes == 0, "0 patients with multiple current rows"))

    con.close()
    return checks


def write_report(checks: list[CheckResult], output_path: str | Path) -> dict:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "pass" if all(c.status == "pass" or c.severity == "warning" for c in checks) else "fail",
        "failed_error_checks": sum(c.status == "fail" and c.severity == "error" for c in checks),
        "failed_warning_checks": sum(c.status == "fail" and c.severity == "warning" for c in checks),
        "checks": [asdict(c) for c in checks],
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
