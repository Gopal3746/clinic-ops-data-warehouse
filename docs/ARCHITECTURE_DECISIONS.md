# Architecture Decisions

## ADR-001 — Synthetic data only

**Decision:** Use synthetic-only data and avoid real PHI.

**Why:** The project demonstrates healthcare operations engineering without creating privacy or compliance risk.

## ADR-002 — Local lake mirrors S3

**Decision:** Use a filesystem backend by default with exactly the same keys used by the boto3 S3 backend.

**Why:** The repository remains free to run locally while still containing real S3 put/get/list logic.

## ADR-003 — Raw JSONL snapshots

**Decision:** Persist API records as immutable JSONL objects partitioned by ingestion date.

**Why:** This preserves the source snapshot before any casting or business logic.

## ADR-004 — DuckDB for portfolio warehouse

**Decision:** Use DuckDB rather than a managed database in the default run.

**Why:** It keeps the project reproducible and nearly cost-free. The dimensional SQL remains transferable to a cloud warehouse.

## ADR-005 — Patient SCD Type 2

**Decision:** Preserve profile/payer history in `dim_patient`.

**Why:** Historical reports should resolve patient profile context as it existed on the encounter/referral date.

## ADR-006 — Aggregate claims before fact join

**Decision:** Claims are grouped to encounter grain in `int_claims_by_encounter`.

**Why:** A direct one-to-many claim join could multiply encounter rows and corrupt utilization measures.
