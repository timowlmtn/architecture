variable "aws_profile" {
  description = "AWS CLI profile to use, e.g. postgres-dev"
  type        = string
}

variable "aws_region" {
  description = "AWS region for the RDS instance"
  type        = string
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "dataweave"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "postgres_name" {
  description = "Initial database name"
  type        = string
  default     = "azrius"
}

variable "postgres_username" {
  description = "Master username for the RDS instance"
  type        = string
  default     = "svc_azrius"
}

variable "postgres_password" {
  description = "Master password for the RDS instance"
  type        = string
  sensitive   = true
}

variable "postgres_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16.3"
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to connect to PostgreSQL"
  type        = list(string)
  default     = []
}

variable "backup_retention_period" {
  description = "Backup retention in days"
  type        = number
  default     = 7
}

variable "multi_az" {
  description = "Whether to enable Multi-AZ"
  type        = bool
  default     = false
}

variable "deletion_protection" {
  description = "Whether to enable deletion protection"
  type        = bool
  default     = false
}

variable "postgres_host" {
  type        = string
  description = "Postgres host"
}

variable "postgres_port" {
  type        = number
  description = "Postgres port"
}

variable "postgres_user" {
  type        = string
  description = "Postgres username"
}


variable "postgres_db" {
  type        = string
  description = "Postgres database"
}

variable "postgres_schema" {
  type        = string
  description = "Postgres schema"
}

variable "vpc_cidr" {
  description = "CIDR block for the postgres-dev VPC"
  type        = string
  default     = "10.30.0.0/16"
}