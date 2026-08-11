from __future__ import annotations

import argparse
import subprocess
import sys


def run(command: list[str], cwd: str | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest-date", default="2026-08-10")
    args = parser.parse_args()

    run([sys.executable, "-m", "compileall", "-q", "src", "scripts", "orchestration"])
    run([sys.executable, "-m", "pytest", "-q"])
    run([sys.executable, "scripts/demo_pipeline.py", "--ingest-date", args.ingest_date])
    print("Verification passed. See artifacts/verification_report.json")


if __name__ == "__main__":
    main()
