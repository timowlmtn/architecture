aws_region    = "us-east-2"
project       = "dataweave"
environment   = "dev"
force_destroy = false

raw_bucket_name       = "dataweave-dev-raw"
lakehouse_bucket_name = "dataweave-dev-lakehouse"
logs_bucket_name      = "dataweave-dev-logs"

lakehouse_readme_key  = "README.md"
lakehouse_readme_body = <<-EOT
# Lakehouse storage initialized

This bucket is intentionally almost empty.

Recommended next steps:
1. Create your catalog layer under src/infra/lakehouse
2. Add Iceberg / Glue / permissions
3. Establish warehouse prefixes such as warehouse/, bronze/, silver/, and checkpoints/
4. Load your first tables through dbt, Spark, or ingestion jobs
EOT

multipart_abort_days    = 7
enable_versioning       = true
sse_algorithm           = "AES256"
block_public_acls       = true
block_public_policy     = true
ignore_public_acls      = true
restrict_public_buckets = true

tags = {
  Owner      = "dataweave"
  CostCenter = "data-platform"
  ManagedBy  = "Terraform"
  Layer      = "storage"
}
