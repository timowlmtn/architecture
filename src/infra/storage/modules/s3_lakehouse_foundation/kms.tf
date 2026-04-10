############################################
# KMS keys for lakehouse S3 bucket encryption
#
# Creates:
# - one KMS key for raw bucket
# - one KMS key for lakehouse bucket
# - one KMS key for logs bucket
# - aliases for each key
#
# Notes:
# - This assumes the caller identity data source exists.
# - If it does not, also add:
#
#   data "aws_caller_identity" "current" {}
#   data "aws_region" "current" {}
#
############################################

data "aws_iam_policy_document" "kms_key_policy" {
  for_each = {
    raw       = var.raw_bucket_name
    lakehouse = var.lakehouse_bucket_name
    logs      = var.logs_bucket_name
  }

  statement {
    sid    = "EnableRootPermissions"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions   = ["kms:*"]
    resources = ["*"]
  }

  statement {
    sid    = "AllowKeyAdministration"
    effect = "Allow"

    principals {
      type = "AWS"
      identifiers = concat(
        ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"],
        var.kms_admin_principal_arns
      )
    }

    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion",
      "kms:RotateKeyOnDemand"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "AllowBucketServiceUsageViaS3"
    effect = "Allow"

    principals {
      type = "AWS"
      identifiers = concat(
        ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"],
        var.kms_user_principal_arns
      )
    }

    actions = [
      "kms:Decrypt",
      "kms:DescribeKey",
      "kms:Encrypt",
      "kms:GenerateDataKey",
      "kms:GenerateDataKeyWithoutPlaintext",
      "kms:ReEncryptFrom",
      "kms:ReEncryptTo"
    ]

    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["s3.${data.aws_region.current.name}.amazonaws.com"]
    }
  }
}

resource "aws_kms_key" "s3" {
  for_each = {
    raw       = var.raw_bucket_name
    lakehouse = var.lakehouse_bucket_name
    logs      = var.logs_bucket_name
  }

  description             = "KMS key for ${each.value} bucket"
  deletion_window_in_days = var.kms_deletion_window_in_days
  enable_key_rotation     = var.kms_enable_key_rotation
  policy                  = data.aws_iam_policy_document.kms_key_policy[each.key].json

  tags = merge(local.default_tags, {
    Name        = "${each.value}-kms"
    Purpose     = "s3-encryption"
    Bucket      = each.value
    KeyCategory = each.key
  })
}

resource "aws_kms_alias" "s3" {
  for_each = aws_kms_key.s3

  name          = "alias/${var.project}-${var.environment}-s3-${each.key}"
  target_key_id = each.value.key_id
}