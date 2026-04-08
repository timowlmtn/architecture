module "s3_lakehouse_foundation" {
  source = "../../modules/s3_lakehouse_foundation"

  aws_region              = var.aws_region
  project                 = var.project
  environment             = var.environment
  force_destroy           = var.force_destroy
  raw_bucket_name         = var.raw_bucket_name
  lakehouse_bucket_name   = var.lakehouse_bucket_name
  logs_bucket_name        = var.logs_bucket_name
  lakehouse_readme_key    = var.lakehouse_readme_key
  lakehouse_readme_body   = var.lakehouse_readme_body
  multipart_abort_days    = var.multipart_abort_days
  enable_versioning       = var.enable_versioning
  sse_algorithm           = var.sse_algorithm
  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
  tags                    = var.tags
}
