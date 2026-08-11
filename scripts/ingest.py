from __future__ import annotations

import argparse

from clinic_ops.ingest import ingest_snapshot


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest-date", required=True)
    args = parser.parse_args()
    manifest = ingest_snapshot(args.ingest_date)
    for row in manifest:
        print(
            f"{row['source']}.{row['entity']}: "
            f"{row['row_count']} rows -> {row['object_key']} "
            f"sha256={row['sha256'][:12]}..."
        )


if __name__ == "__main__":
    main()
