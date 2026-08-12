# Changelog

All notable project changes should be recorded here.

## [0.1.0] - 2026-08-10

### Added
- Synthetic clinical, CRM/referral, and finance/claims source generators.
- Paginated mock REST APIs for three source domains.
- Local data-lake and boto3 S3 storage backends.
- Raw `ingest_date=YYYY-MM-DD` partitioning and ingestion manifests.
- DuckDB landing schemas and manifest audit table.
- Staging and mart data-quality checks.
- dbt Kimball model with SCD Type 2 patient dimension.
- Encounter and referral fact tables plus utilization/financial/funnel marts.
- Airflow TaskFlow DAG.
- Power BI model guidance and DAX measures.
- AI-agent context file and AI work log.
