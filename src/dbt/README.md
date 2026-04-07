# DataLake dbt Bootstrap

This project bootstraps an initial PostgreSQL schema using dbt.

## Prerequisites

- Python 3.11+
- `dbt-postgres`
- A running PostgreSQL instance

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp profiles.yml ~/.dbt/profiles.yml
make debug
make build
```

This creates the following tables in the target schema:

- `customers`
- `products`
- `orders`
- `order_items`
- `cdc_events`

All tables are created empty with the intended column structure, ready for local development and later migration to AWS.

## Common commands

```bash
make deps      # install dbt packages
make debug     # validate dbt connection
make run       # create the tables
make test      # run dbt tests
make build     # run + test together
make clean     # remove target artifacts
```

## Notes for AWS migration

When you move to AWS, you can keep the same dbt model layer and swap the adapter/target profile:

- PostgreSQL/RDS or Aurora PostgreSQL: use `dbt-postgres`
- Redshift: use `dbt-redshift`
- Spark/Iceberg based lakehouse: use `dbt-spark` or `dbt-athena` depending on the execution engine

The model contract and naming approach in this starter project are intentionally simple so they can evolve into raw/bronze/silver style layers later.
