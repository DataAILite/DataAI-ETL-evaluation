# DataAI ETL for Oracle Cloud Marketplace

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

This directory is the Oracle Cloud Marketplace review, packaging, and controlled-evaluation kit for the DataAI Spark libraries. DataAI remains embedded software that runs inside customer-controlled compute. It is not a required hosted service.

## Recommended delivery model

Start with an Oracle lead-generation listing for private JAR fulfillment, or use an OCI container image only after Oracle approves the library-delivery model and an immutable release.

## Current status

The included `0.1.0-SNAPSHOT` artifacts are evaluation-development builds. This package is intentionally marked **not submission-ready** until the channel-specific release and partner gates in `PROVIDER_CHECKLIST.md` are complete. Nothing in this directory publishes, uploads, authenticates, or contacts Oracle Cloud Marketplace.

## Contents

| Path | Purpose |
| --- | --- |
| `listing/` | Draft marketplace or repository metadata |
| `docs/` | Installation, release-gate, security, and function documentation |
| `lib/` | Verified DataAI evaluation artifacts |
| `assets/` | DataAI listing artwork |
| `screenshots/` | Fictional-data design previews |
| `distribution/` | Customer evaluation ZIP |
| `scripts/` | Deterministic generation and offline validation |
| `CHECKSUMS.sha256` | Package integrity manifest |

The repository-root `DataAIETLOracle.zip` is the provider-review ZIP. Its sidecar is `DataAIETLOracle.zip.sha256`.

## Start here

1. Read `MARKETPLACE_SUBMISSION.md`.
2. Complete `PROVIDER_CHECKLIST.md`.
3. Review `docs/INSTALLATION_AND_USAGE.md` and `docs/RELEASE_GATES.md`.
4. Replace all bracketed placeholders.
5. Generate and validate locally before any external submission.

## License

Evaluation use is governed by `LICENSE.md`. Production, continued use, redistribution, OEM, and managed-service use require separate written commercial terms from Yanbor LLC. The software is provided **AS IS**, and the customer is responsible for evaluating compatibility and suitability during the permitted evaluation period.
