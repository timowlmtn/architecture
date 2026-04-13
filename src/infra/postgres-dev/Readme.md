# postgres-dev Terraform stack

This stack provisions a managed PostgreSQL source database in the `postgres-dev` AWS account for the DataWeave lakehouse project.

## What it creates

- RDS PostgreSQL instance
- DB subnet group
- Security group
- Custom DB parameter group with logical replication enabled
- Useful connection outputs

## Usage

```bash
cd src/infra/postgres-dev
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

---

## What I’d change next

A few improvements are worth doing right after the first apply:

### 1. Stop putting the password in tfvars
Use one of these instead:
- `TF_VAR_db_password`
- AWS Secrets Manager
- SSM Parameter Store

### 2. Create the schema and app user bootstrap
Terraform should create the infrastructure, but the SQL bootstrap can be separate:
- create `staging` schema
- create grants
- load your seed data

### 3. Tighten security group rules
If DMS will run in another account, the clean next move is:
- VPC peering between the source-account VPC and the lakehouse-account VPC
- security group ingress from the DMS subnets or a tightly-scoped CIDR
- keep the DB private, not public

### 4. Add option group / monitoring only if needed
For now, the above is enough to stand up a clean source RDS instance. CloudWatch log export is supported for PostgreSQL logs, and custom parameter groups are the right place to set engine parameters like logical replication. :contentReference[oaicite:2]{index=2}

---

## Why this matches your DMS plan

AWS’s PostgreSQL source guidance for DMS calls out that CDC from RDS PostgreSQL depends on logical replication being enabled. :contentReference[oaicite:3]{index=3}

So the important thing in this Terraform stack is not just “make an RDS instance,” but “make an RDS instance that is ready to become a DMS source.”

---

## My recommendation for your repo

Given your current structure, I’d keep this as a separate stack:

```text
src/infra/storage
src/infra/lakehouse
src/infra/postgres-dev