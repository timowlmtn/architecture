locals {
  ssm_prefix = "/${var.project}/${var.environment}/postgres"


}

#
# Core connection parameters
#

resource "aws_ssm_parameter" "postgres_host" {
  name  = "${local.ssm_prefix}/host"
  type  = "String"
  value = var.postgres_host

  tags = local.common_tags
}

resource "aws_ssm_parameter" "postgres_port" {
  name  = "${local.ssm_prefix}/port"
  type  = "String"
  value = tostring(var.postgres_port)

  tags = local.common_tags
}

resource "aws_ssm_parameter" "postgres_db" {
  name  = "${local.ssm_prefix}/db_name"
  type  = "String"
  value = var.postgres_db

  tags = local.common_tags
}

resource "aws_ssm_parameter" "postgres_schema" {
  name  = "${local.ssm_prefix}/schema"
  type  = "String"
  value = var.postgres_schema

  tags = local.common_tags
}

resource "aws_ssm_parameter" "postgres_username" {
  name  = "${local.ssm_prefix}/username"
  type  = "String"
  value = var.postgres_user

  tags = local.common_tags
}

#
# Sensitive parameter
#

resource "aws_ssm_parameter" "postgres_password" {
  name  = "${local.ssm_prefix}/password"
  type  = "SecureString"
  value = var.postgres_password

  # Optional: use a custom KMS key
  # key_id = var.kms_key_id

  tags = local.common_tags
}