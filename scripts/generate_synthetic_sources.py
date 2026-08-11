from __future__ import annotations

import argparse
from datetime import date

from clinic_ops.synthetic import generate_fixture_bundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--patients", type=int, default=1200)
    parser.add_argument("--encounters", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--as-of-date", default="2026-08-10")
    parser.add_argument("--output-dir", default="fixtures")
    args = parser.parse_args()

    metadata = generate_fixture_bundle(
        output_dir=args.output_dir,
        patient_count=args.patients,
        encounter_count=args.encounters,
        seed=args.seed,
        as_of_date=date.fromisoformat(args.as_of_date),
    )
    print("Generated synthetic-only source fixtures:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
