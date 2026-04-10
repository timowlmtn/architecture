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

output "raw_kms_key_arn" {
  description = "ARN of the KMS key for the raw bucket"
  value       = aws_kms_key.s3["raw"].arn
}

output "lakehouse_kms_key_arn" {
  description = "ARN of the KMS key for the lakehouse bucket"
  value       = aws_kms_key.s3["lakehouse"].arn
}

output "logs_kms_key_arn" {
  description = "ARN of the KMS key for the logs bucket"
  value       = aws_kms_key.s3["logs"].arn
}