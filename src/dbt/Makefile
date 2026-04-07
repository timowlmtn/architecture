DBT ?= dbt
PROJECT_DIR := .
PROFILE_DIR ?= $(HOME)/.dbt

.PHONY: deps debug run test build clean compile docs serve

deps:
	$(DBT) deps --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

debug:
	$(DBT) debug --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

run:
	$(DBT) run --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

test:
	$(DBT) test --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

build:
	$(DBT) build --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

compile:
	$(DBT) compile --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

docs:
	$(DBT) docs generate --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

serve:
	$(DBT) docs serve --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)

clean:
	$(DBT) clean --project-dir $(PROJECT_DIR) --profiles-dir $(PROFILE_DIR)
	rm -rf logs target dbt_packages
