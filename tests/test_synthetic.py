from datetime import date
import json

from clinic_ops.synthetic import generate_fixture_bundle


def test_generated_contracts_and_ids_are_synthetic(tmp_path):
    metadata = generate_fixture_bundle(
        output_dir=tmp_path,
        patient_count=100,
        encounter_count=300,
        seed=7,
        as_of_date=date(2026, 8, 10),
    )
    assert metadata["synthetic_only"] is True
    patients = json.loads((tmp_path / "clinical/patients.json").read_text())
    encounters = json.loads((tmp_path / "clinical/encounters.json").read_text())
    assert len(patients) == 100
    assert len(encounters) == 300
    assert len({p["patient_id"] for p in patients}) == 100
    assert all(p["patient_id"].startswith("PAT-") for p in patients)
    assert len({e["encounter_id"] for e in encounters}) == 300


def test_scd2_has_exactly_one_current_row_per_patient(tmp_path):
    generate_fixture_bundle(
        output_dir=tmp_path,
        patient_count=120,
        encounter_count=250,
        seed=9,
        as_of_date=date(2026, 8, 10),
    )
    history = json.loads((tmp_path / "crm/patient_profile_history.json").read_text())
    current_counts = {}
    for row in history:
        if row["is_current"]:
            current_counts[row["patient_id"]] = current_counts.get(row["patient_id"], 0) + 1
    assert len(current_counts) == 120
    assert set(current_counts.values()) == {1}
