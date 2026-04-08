output "raw_bucket_name" {
  value = module.s3_lakehouse_foundation.raw_bucket_name
}

output "lakehouse_bucket_name" {
  value = module.s3_lakehouse_foundation.lakehouse_bucket_name
}

output "logs_bucket_name" {
  value = module.s3_lakehouse_foundation.logs_bucket_name
}

output "lakehouse_readme_key" {
  value = module.s3_lakehouse_foundation.lakehouse_readme_key
}
