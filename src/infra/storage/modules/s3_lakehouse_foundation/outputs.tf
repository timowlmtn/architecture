output "raw_bucket_name" {
  value       = aws_s3_bucket.raw.bucket
  description = "Raw landing bucket name."
}

output "lakehouse_bucket_name" {
  value       = aws_s3_bucket.lakehouse.bucket
  description = "Primary lakehouse bucket name."
}

output "logs_bucket_name" {
  value       = aws_s3_bucket.logs.bucket
  description = "Logs bucket name."
}

output "lakehouse_readme_key" {
  value       = aws_s3_object.lakehouse_readme.key
  description = "README object created in the lakehouse bucket."
}
