terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

locals {
  default_tags = merge({
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "Terraform"
    Layer       = "storage"
  }, var.tags)
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}


resource "aws_s3_bucket" "raw" {
  bucket        = var.raw_bucket_name
  force_destroy = var.force_destroy

  tags = merge(local.default_tags, {
    Name = var.raw_bucket_name
    Role = "raw"
  })
}

resource "aws_s3_bucket" "lakehouse" {
  bucket        = var.lakehouse_bucket_name
  force_destroy = var.force_destroy

  tags = merge(local.default_tags, {
    Name = var.lakehouse_bucket_name
    Role = "lakehouse"
  })
}

resource "aws_s3_bucket" "logs" {
  bucket        = var.logs_bucket_name
  force_destroy = var.force_destroy

  tags = merge(local.default_tags, {
    Name = var.logs_bucket_name
    Role = "logs"
  })
}

resource "aws_s3_bucket_public_access_block" "raw" {
  bucket                  = aws_s3_bucket.raw.id
  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}

resource "aws_s3_bucket_public_access_block" "lakehouse" {
  bucket                  = aws_s3_bucket.lakehouse.id
  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}

resource "aws_s3_bucket_public_access_block" "logs" {
  bucket                  = aws_s3_bucket.logs.id
  block_public_acls       = var.block_public_acls
  block_public_policy     = var.block_public_policy
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}

resource "aws_s3_bucket_versioning" "raw" {
  bucket = aws_s3_bucket.raw.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_versioning" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw" {
  bucket = aws_s3_bucket.raw.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.sse_algorithm
      kms_master_key_id = var.sse_algorithm == "aws:kms" ? aws_kms_key.raw.arn : null
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.sse_algorithm
      kms_master_key_id = var.sse_algorithm == "aws:kms" ? aws_kms_key.lakehouse.arn : null
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.sse_algorithm
      kms_master_key_id = var.sse_algorithm == "aws:kms" ? aws_kms_key.logs.arn : null
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "raw" {
  bucket = aws_s3_bucket.raw.id

  rule {
    id     = "abort-incomplete-multipart-upload"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = var.multipart_abort_days
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lakehouse" {
  bucket = aws_s3_bucket.lakehouse.id

  rule {
    id     = "abort-incomplete-multipart-upload"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload {
      days_after_initiation = var.multipart_abort_days
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "logs" {
  bucket = aws_s3_bucket.logs.id

  rule {
    id     = "abort-incomplete-multipart-upload"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload {
      days_after_initiation = var.multipart_abort_days
    }
  }
}

resource "aws_s3_object" "lakehouse_readme" {
  bucket       = aws_s3_bucket.lakehouse.id
  key          = var.lakehouse_readme_key
  content      = var.lakehouse_readme_body
  content_type = "text/markdown"
}

############################################
# KMS Keys for S3 Encryption
############################################

resource "aws_kms_key" "raw" {
  description             = "KMS key for ${var.raw_bucket_name}"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "EnableRootPermissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "AllowS3Usage"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "kms:ViaService" = "s3.${data.aws_region.current.name}.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = merge(local.default_tags, {
    Name = "${var.raw_bucket_name}-kms"
  })
}

resource "aws_kms_key" "lakehouse" {
  description             = "KMS key for ${var.lakehouse_bucket_name}"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = aws_kms_key.raw.policy

  tags = merge(local.default_tags, {
    Name = "${var.lakehouse_bucket_name}-kms"
  })
}

resource "aws_kms_key" "logs" {
  description             = "KMS key for ${var.logs_bucket_name}"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = aws_kms_key.raw.policy

  tags = merge(local.default_tags, {
    Name = "${var.logs_bucket_name}-kms"
  })
}

############################################
# KMS Aliases (important for humans + future refactors)
############################################

resource "aws_kms_alias" "raw" {
  name          = "alias/${var.project}-${var.environment}-raw"
  target_key_id = aws_kms_key.raw.key_id
}

resource "aws_kms_alias" "lakehouse" {
  name          = "alias/${var.project}-${var.environment}-lakehouse"
  target_key_id = aws_kms_key.lakehouse.key_id
}

resource "aws_kms_alias" "logs" {
  name          = "alias/${var.project}-${var.environment}-logs"
  target_key_id = aws_kms_key.logs.key_id
}

