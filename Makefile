mmd:
	python src/python/pg_to_mermaid.py --schema staging --output docs/staging_erd.mmd

reqs:
	pip install -r requirements.txt

fmt:
	ruff format src/python

petstore:
	PETSTORE_SCHEMA=staging PETSTORE_START_DATE=2024-01-01 PETSTORE_END_DATE=2026-04-09 PETSTORE_MODE=auto \
		python docs/load_petstore_data.py
