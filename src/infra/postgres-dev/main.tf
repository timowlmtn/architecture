locals {
  name_prefix = "${var.project}-${var.environment}-postgres"
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
    Stack       = "postgres-dev"
  }
}

resource "aws_security_group" "postgres" {
  name        = "${local.name_prefix}-sg"
  description = "Security group for postgres-dev RDS"
  vpc_id      = aws_vpc.postgres.id

  ingress {
    description = "PostgreSQL access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-sg"
  })
}

resource "aws_db_subnet_group" "postgres" {
  name       = "${local.name_prefix}-subnet-group"
  subnet_ids = [for s in aws_subnet.private : s.id]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-subnet-group"
  })
}

resource "aws_db_parameter_group" "postgres" {
  name        = "${local.name_prefix}-pg"
  family      = "postgres16"
  description = "Custom parameter group for postgres-dev"

  # Needed later for AWS DMS CDC / logical replication
  parameter {
    name         = "rds.logical_replication"
    value        = "1"
    apply_method = "pending-reboot"

  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-pg"
  })
}

resource "aws_db_instance" "postgres" {
  identifier = "${local.name_prefix}-db"

  engine            = "postgres"
  engine_version    = var.engine_version
  instance_class    = var.postgres_instance_class
  allocated_storage = var.allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.postgres_name
  username = var.postgres_username
  password = var.postgres_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.postgres.name
  vpc_security_group_ids = [aws_security_group.postgres.id]
  parameter_group_name   = aws_db_parameter_group.postgres.name

  backup_retention_period = var.backup_retention_period
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  multi_az            = var.multi_az
  publicly_accessible = false

  deletion_protection = var.deletion_protection
  skip_final_snapshot = true
  apply_immediately   = true

  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db"
  })
}