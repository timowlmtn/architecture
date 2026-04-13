# DataWeave Dev Lakehouse README

## Overview

This repository currently provisions the foundational storage layer for the DataWeave 
development lakehouse in AWS. The environment is organized around three S3 buckets that 
separate raw ingestion, curated lakehouse storage, and operational logging.

## Buckets

Raw bucket: dataweave-dev-raw
Lakehouse bucket: dataweave-dev-lakehouse
Logs bucket: dataweave-dev-logs

This gives us the basic landing zones we need to support an S3-based lakehouse pattern:

the raw bucket receives source extracts and change data before transformation
the lakehouse bucket becomes the governed analytical storage layer
the log bucket captures service logs, replication logs, and operational diagnostics