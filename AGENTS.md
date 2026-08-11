# AI/Agent Context for Clinic Ops Data Warehouse

This file is the source of truth for AI-assisted changes to this repository.

## Non-negotiable privacy rule

- This repository uses **synthetic data only**.
- Never add real patient data, real PHI, production exports, screenshots containing PHI, secrets, tokens, or credentials.
- Never describe the project as "HIPAA compliant." It is a portfolio implementation that demonstrates HIPAA-conscious design choices such as synthetic data, data minimization, separated raw/curated layers, and audit metadata.
- Synthetic patient identifiers must stay obviously synthetic (`PAT-...`).

## Naming conventions

- Python, SQL, files, and columns: `snake_case`.
- dbt staging models: `stg_...`
- intermediate models: `int_...`
- dimensions: `dim_...`
- facts: `fct_...`
- reporting marts: `mart_...`
- natural/source IDs: `*_id`
- warehouse surrogate keys: `*_key`

## Dimensional-model rules

- `fct_encounters` grain is exactly **one row per encounter/session**.
- `fct_referrals` grain is exactly **one row per referral**.
- Do not add measures that violate the declared grain.
- `dim_patient` is SCD Type 2. A fact must join to the patient version effective on the fact date.
- Do not silently turn a one-to-many source relationship into a one-to-one join.
- Claims are aggregated to encounter grain before joining to `fct_encounters`.

## Source-contract rules

- Do not invent source columns inside staging models.
- If a new source field is needed, add it first to the generator/API source contract and document it.
- Raw lake objects are immutable snapshots. Transformations happen after landing.
- Every ingested entity must create a manifest row with row count, SHA-256, byte count, source, entity, object key, and ingestion timestamp.

## Testing expectations

Before committing a change:

1. `python -m compileall src scripts orchestration`
2. `pytest`
3. Run the local demo pipeline if dependencies are installed: `make demo`
4. Run dbt tests: `cd transform && dbt build --profiles-dir .`
5. Confirm staging DQ and mart DQ pass.
6. Review generated row counts for unexpected fanout.
7. Do not commit generated raw data, DuckDB files, secrets, or credentials.

## Pull request / commit discipline

Prefer small commits that each have one purpose:

- source contracts / generators
- ingestion / lake
- staging / DQ
- dimensional model
- orchestration
- BI/reporting
- documentation

## Don't-touch list without explicit reason

- fact-table grain
- SCD2 effective-date logic
- raw object-key partition convention
- manifest fields
- synthetic-only privacy rule

If an AI assistant proposes changing any of these, require a written rationale and a regression test.
