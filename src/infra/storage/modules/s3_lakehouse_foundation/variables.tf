variable "aws_region" {
  type        = string
  description = "AWS region for tagging/context."
}

variable "project" {
  type        = string
  description = "Project name used for tagging and identification."
}

variable "environment" {
  type        = string
  description = "Environment name, such as dev, test, or prod."
}

variable "force_destroy" {
  type        = bool
  description = "Whether to allow bucket deletion when non-empty."
}

variable "raw_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for raw landing data."
}

variable "lakehouse_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for lakehouse data."
}

variable "logs_bucket_name" {
  type        = string
  description = "Globally unique S3 bucket name for logs."
}

variable "lakehouse_readme_key" {
  type        = string
  description = "Object key for the README placed in the lakehouse bucket."
}

variable "lakehouse_readme_body" {
  type        = string
  description = "Markdown content for the README object in the lakehouse bucket."
}

variable "multipart_abort_days" {
  type        = number
  description = "Days before aborting incomplete multipart uploads."
}

variable "enable_versioning" {
  type        = bool
  description = "Whether to enable S3 versioning on all buckets."
}

variable "sse_algorithm" {
  type        = string
  description = "Server-side encryption algorithm for all buckets."
}

variable "block_public_acls" {
  type        = bool
  description = "Whether to block public ACLs."
}

variable "block_public_policy" {
  type        = bool
  description = "Whether to block public bucket policies."
}

variable "ignore_public_acls" {
  type        = bool
  description = "Whether to ignore public ACLs."
}

variable "restrict_public_buckets" {
  type        = bool
  description = "Whether to restrict public buckets."
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources."
}
