# Lakehouse Terraform

This directory is reserved for the catalog, metadata, and higher-level lakehouse infrastructure.

Keep it separate from `src/infra/storage` so storage can be provisioned independently.

Recommended approach:
- Give `lakehouse/envs/<env>` its own `terraform.tfvars`
- Keep Glue, Lake Formation, IAM, and Iceberg-facing configuration here
- Leave S3 bucket creation in `src/infra/storage`
