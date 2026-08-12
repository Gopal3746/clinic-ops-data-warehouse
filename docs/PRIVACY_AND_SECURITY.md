# Privacy and Security Notes

## Scope

This is a portfolio project using synthetic records only. It is not a HIPAA compliance certification and is not intended to process production PHI.

## Design choices demonstrated

- synthetic-only patient records;
- identifiers clearly marked as synthetic;
- no patient names required for analytical use;
- immutable raw snapshots;
- separation of raw, landing/staging, and curated marts;
- ingestion manifests with hashes and row counts;
- `.env` and credentials excluded from Git;
- optional AWS credential resolution through standard boto3 mechanisms;
- minimal source fields rather than copying every available clinical field;
- audit-friendly transformation and DQ outputs.

## What a production implementation would additionally need

- organization-approved security architecture;
- encryption/key-management policy;
- IAM least privilege and role separation;
- private networking and endpoint controls;
- centralized audit logging and alerting;
- retention/deletion policy;
- BAAs where required;
- formal risk assessment;
- access reviews;
- incident response;
- production secrets management;
- data classification and DLP controls;
- PHI-safe observability and logging.
