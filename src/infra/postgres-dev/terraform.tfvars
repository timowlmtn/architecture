aws_profile = "postgres-dev"
aws_region  = "us-east-2"

project     = "dataweave"
environment = "dev"

postgres_instance_class = "db.t4g.micro"
allocated_storage       = 20
engine_version          = "16.12"

vpc_cidr            = "10.30.0.0/16"
allowed_cidr_blocks = ["10.30.0.0/16"]


backup_retention_period = 7
multi_az                = false
deletion_protection     = false