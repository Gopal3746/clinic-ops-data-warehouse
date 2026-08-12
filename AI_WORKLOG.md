# AI Work Log

Use this file to document AI-assisted development accurately. Record what the assistant proposed, what you accepted, what you changed, and how you verified it.

## 2026-08-10 — Initial repository scaffold

**Tool:** ChatGPT

**Asked for:** A synthetic clinic-operations data warehouse portfolio project with API ingestion, S3-style raw landing, DuckDB, dbt/Kimball modeling, Airflow orchestration, Power BI reporting guidance, data-quality checks, and an AI context file.

**Assistant contribution:** Generated the initial repository structure, source contracts, synthetic-data generator, mock REST API, ingestion/storage abstractions, dbt model SQL/YAML, DQ scripts, orchestration DAG, Power BI measures, tests, and documentation.

**Human review required before portfolio use:**
- Run `make verify` locally.
- Inspect the source-to-fact joins for fanout.
- Confirm all dbt relationship tests pass.
- Inspect at least 20 generated encounter/claim rows manually.
- Build the Power BI file from the documented model rather than claiming a `.pbix` exists when it does not.
- Replace this section with the exact corrections you made.

**Verification status in this generated scaffold:** Not claimed. The repository includes verification commands, but results must be produced on the developer's machine with project dependencies installed.

---

## Template for later entries

### YYYY-MM-DD — Short change description

**Tool:** Claude Code / Copilot / ChatGPT / other

**Asked for:**  
Describe the prompt or task.

**Assistant proposed:**  
Describe the code or approach.

**What I changed/corrected:**  
Record any incorrect join, invented column, unsafe assumption, naming issue, performance issue, or test gap.

**How I verified it:**  
List commands, tests, row-count comparisons, or manual checks.

**Commit:**  
`<hash or commit message>`
