# Storage Terraform

This Terraform stack creates the base S3 storage artifacts for a lakehouse.

## Design choice
This version is fully driven by `terraform.tfvars`.

There are no convenience defaults in the environment-level variables. That means bucket names, behavior flags, tags, encryption settings, and the README object content all come from the selected tfvars file.

## What it creates
- A raw bucket for landing data
- A lakehouse bucket for curated or warehouse data
- A logs bucket for access or application logs
- Server-side encryption
- Versioning
- Public access blocks
- Lifecycle rules for incomplete multipart uploads
- A small README object in the lakehouse bucket so the bucket is intentionally empty except for guidance

## Usage
From `src/infra`:

```bash
cp storage/envs/dev/terraform.tfvars.example storage/envs/dev/terraform.tfvars
make COMPONENT=storage init
make COMPONENT=storage plan
make COMPONENT=storage apply
```

You can also point at another vars file:

```bash
make COMPONENT=storage ENV=dev TFVARS=my-team.tfvars plan
```

## Notes
- S3 bucket names must be globally unique, so you should set all three bucket names explicitly in the tfvars file.
- The lakehouse bucket is created empty except for the README object.
- The Makefile lives at `src/infra`, keeping storage and future lakehouse stacks separate.
