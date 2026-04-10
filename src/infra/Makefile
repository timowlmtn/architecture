ENV ?= dev
COMPONENT ?= storage
TF_DIR := $(COMPONENT)/envs/$(ENV)
TFVARS ?= terraform.tfvars

.PHONY: fmt init validate plan apply destroy all show-vars

fmt:
	terraform -chdir=$(TF_DIR) fmt -recursive
	terraform -chdir=$(COMPONENT)/modules fmt -recursive


init:
	terraform -chdir=$(TF_DIR) init

validate:
	terraform -chdir=$(TF_DIR) validate -var-file=$(TFVARS)

plan:
	terraform -chdir=$(TF_DIR) plan -var-file=$(TFVARS)

apply:
	terraform -chdir=$(TF_DIR) apply -auto-approve -var-file=$(TFVARS)

destroy:
	terraform -chdir=$(TF_DIR) destroy -auto-approve -var-file=$(TFVARS)

show-vars:
	@echo "Using component: $(COMPONENT)"
	@echo "Using environment: $(ENV)"
	@echo "Using tfvars: $(TF_DIR)/$(TFVARS)"

all: fmt init validate plan
