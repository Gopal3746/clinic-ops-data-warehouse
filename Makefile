PYTHON ?= python
API_PORT ?= 8765
INGEST_DATE ?= 2026-08-10

.PHONY: setup generate api ingest stage dq-staging dbt dq-marts demo test verify clean

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e .

generate:
	$(PYTHON) scripts/generate_synthetic_sources.py --patients 1200 --encounters 6000 --seed 42

api:
	$(PYTHON) -m uvicorn clinic_ops.mock_api:app --host 127.0.0.1 --port $(API_PORT)

ingest:
	$(PYTHON) scripts/ingest.py --ingest-date $(INGEST_DATE)

stage:
	$(PYTHON) scripts/load_staging.py --ingest-date $(INGEST_DATE)

dq-staging:
	$(PYTHON) scripts/run_dq.py --phase staging --ingest-date $(INGEST_DATE)

dbt:
	cd transform && dbt build --profiles-dir .

dq-marts:
	$(PYTHON) scripts/run_dq.py --phase marts --ingest-date $(INGEST_DATE)

demo:
	$(PYTHON) scripts/demo_pipeline.py --ingest-date $(INGEST_DATE)

test:
	pytest

verify:
	$(PYTHON) scripts/verify_project.py --ingest-date $(INGEST_DATE)

clean:
	rm -rf fixtures data_lake warehouse/*.duckdb transform/target transform/logs .pytest_cache
