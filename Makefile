mmd:
	python src/python/pg_to_mermaid.py --schema staging --output docs/staging_erd.mmd

reqs:
	pip install -r requirements.txt

fmt:
	ruff format src/python
