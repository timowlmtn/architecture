variable "aws_region" {
  description = "AWS region for tagging/context."
  type        = string
}

variable "project" {
  description = "Project name used for tagging and identification."
  type        = string
}

variable "environment" {
  description = "Environment name, such as dev, test, or prod."
  type        = string
}

variable "force_destroy" {
  description = "Whether to allow bucket deletion when non-empty."
  type        = bool
}

variable "raw_bucket_name" {
  description = "Globally unique S3 bucket name for raw landing data."
  type        = string
}

variable "lakehouse_bucket_name" {
  description = "Globally unique S3 bucket name for lakehouse data."
  type        = string
}

variable "logs_bucket_name" {
  description = "Globally unique S3 bucket name for logs."
  type        = string
}

variable "lakehouse_readme_key" {
  description = "Object key for the README placed in the lakehouse bucket."
  type        = string
}

variable "lakehouse_readme_body" {
  description = "Markdown content for the README object in the lakehouse bucket."
  type        = string
}

variable "multipart_abort_days" {
  description = "Days before aborting incomplete multipart uploads."
  type        = number
}

variable "enable_versioning" {
  description = "Whether to enable S3 versioning on all buckets."
  type        = bool
}

variable "sse_algorithm" {
  description = "Server-side encryption algorithm for all buckets."
  type        = string
}

variable "block_public_acls" {
  description = "Whether to block public ACLs."
  type        = bool
}

variable "block_public_policy" {
  description = "Whether to block public bucket policies."
  type        = bool
}

variable "ignore_public_acls" {
  description = "Whether to ignore public ACLs."
  type        = bool
}

variable "restrict_public_buckets" {
  description = "Whether to restrict public buckets."
  type        = bool
}

variable "tags" {
  description = "Tags to apply to resources."
  type        = map(string)
}

variable "kms_enable_key_rotation" {
  description = "Whether to enable automatic KMS key rotation."
  type        = bool
  default     = true
}

variable "kms_deletion_window_in_days" {
  description = "Number of days before KMS key deletion if scheduled."
  type        = number
  default     = 30
}

variable "kms_admin_principal_arns" {
  description = "Additional IAM principal ARNs allowed to administer the KMS keys."
  type        = list(string)
  default     = []
}

variable "kms_user_principal_arns" {
  description = "Additional IAM principal ARNs allowed to use the KMS keys through S3."
  type        = list(string)
  default     = []
}