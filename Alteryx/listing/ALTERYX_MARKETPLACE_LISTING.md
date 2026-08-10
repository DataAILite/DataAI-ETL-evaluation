# Alteryx Marketplace Listing Draft

## Basic information

- **Listing name:** DataAI ETL Quality for Spark
- **Provider:** Yanbor LLC, provider of the DataAI product
- **Add-On type:** Custom Tool
- **Edition name:** Designer 2026.1 Evaluation
- **Version:** 0.1.0-SNAPSHOT evaluation candidate
- **Category:** Data Preparation and Data Quality
- **Search tags:** DataAI, ETL, Spark, data quality, profiling, validation,
  normalization, governed analytics

## Short description

Run DataAI normalization, profiling, validation, rejection, and quality scoring
from Alteryx in your customer-controlled Spark environment.

## Overview

DataAI ETL Quality adds a configurable Alteryx Designer tool that launches the
embedded DataAI Spark ETL libraries with your own `spark-submit`, Spark
catalog, compute, credentials, and selected output tables. There is no
Yanbor-hosted service, telemetry, remote license check, or customer-data
transfer to Yanbor LLC.

This download is a source-available evaluation build. Evaluate it with
representative non-sensitive data before acquiring commercial production
rights from Yanbor LLC.

## Benefits

- Add governed data-quality processing to an existing Alteryx workflow.
- Keep data, compute, credentials, and outputs in customer-controlled systems.
- Produce clean, rejected, profile, and findings tables for downstream tools.
- Apply a minimum quality score as an ETL release gate.
- Use an inspectable adapter with no shell command construction.
- Receive the wider DataAI Spark library set for customer Spark development.

## Features

- optional string normalization;
- field profiling and explainable findings;
- JSON-configured DataAI validation rules;
- clean and rejected row separation;
- quality score and minimum-score enforcement;
- optional Alteryx status output;
- Java 17, Spark 3.5, and Scala 2.12 build baseline;
- DataAI analytics, market, mapping, time-series, insight, and matrix-balancing
  APIs included as Spark libraries and documented separately.

The first Alteryx UI directly runs the quality pipeline. Advanced Spark
functions are not represented as separate Designer tools in this edition.

## Requirements

- Alteryx Designer 2026.1 with AMP enabled;
- Windows 64-bit and embedded Python 3.13.11;
- Java 17;
- customer-provided Spark 3.5 / Scala 2.12 and Delta support;
- local or reachable `spark-submit`;
- customer permissions for the selected Spark catalog tables.

## Data and security disclosure

The tool writes a transient local JSON configuration and deletes it after the
run. Each nonblank output table is intentionally overwritten in Delta format.
It does not return customer rows or raw Spark logs through its Status anchor.
Do not place credentials in tool configuration; use customer secret stores and
service identities.

## Pricing and license

The Marketplace download is free for evaluation under `LICENSE.md`. It does
not grant production use. Commercial production licensing, updates, and
support are available separately from Yanbor LLC under a signed agreement.

All software is provided **AS IS** and without obligations except those stated
in a signed agreement. Customers should complete evaluation and acceptance
testing before production licensing.

## Support

- **Support organization:** Yanbor LLC
- **Support URL:** replace with the final DataAI support page before submission
- **Support email:** replace with a monitored role address before submission
- **Documentation:** included installation, security, compatibility, function
  catalog, and release-gate guides

## Media

- `assets/dataai-alteryx-icon.png` — square listing logo
- `screenshots/alteryx-configuration-preview.png` — design preview only
- `screenshots/alteryx-workflow-preview.png` — design preview only

Replace design previews with actual screenshots from the validated YXI before
submission.

## Release notes — 0.1.0 evaluation candidate

- Initial DataAI ETL Quality Alteryx custom-tool adapter.
- Added local `spark-submit` execution without a command shell.
- Added normalization, profiling, rules, table outputs, and quality gate UI.
- Added inspectable source, examples, checksums, and Spark function catalog.
- External Designer and Server execution validation remains a release gate.
