TF_DIR := $(PWD)
TFVARS := $(TF_DIR)/terraform.tfvars

fmt:
	terraform -chdir=$(TF_DIR) fmt -recursive

init:
	terraform -chdir=$(TF_DIR) init

validate:
	terraform -chdir=$(TF_DIR) validate -var-file=$(TFVARS)

plan:
	terraform -chdir=$(TF_DIR) plan -var-file=$(TFVARS)

apply:
	terraform -chdir=$(TF_DIR) apply -auto-approve -var-file=$(TFVARS)
