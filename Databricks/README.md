# DataAI ETL for Databricks Marketplace

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

This directory is the Databricks Marketplace preparation and controlled
evaluation package for the DataAI Spark libraries. DataAI runs inside the
customer's Databricks compute. It is not a hosted DataAI service and does not
require DataAI network calls, telemetry, remote license checks, or transmission
of customer data.

## Package contents

| Path | Purpose |
| --- | --- |
| `listing/` | Marketplace-ready listing copy and field values |
| `notebooks/` | Importable Databricks source notebooks |
| `data/` | Fictional evaluation data, including matrix controls |
| `lib/` | Evaluation JARs copied from the verified Spark build |
| `sql/` | Provider and consumer Unity Catalog setup templates |
| `configs/` | Cluster-library and Databricks Job templates |
| `docs/` | Installation, compatibility, function, and security guidance |
| `assets/` | DataAI listing artwork |
| `screenshots/` | Draft design previews made with fictional data |
| `distribution/` | Customer evaluation ZIP |
| `scripts/` | Deterministic generation and offline validation |
| `CHECKSUMS.sha256` | Integrity manifest for package files |

The repository-root `DataAIETLDatabricks.zip` is the provider-review archive.
Its SHA-256 digest is stored in `DataAIETLDatabricks.zip.sha256`.

## Recommended Marketplace model

Use a personalized listing that requires provider approval. Share the
evaluation notebooks, fictional data, documentation, and evaluation JARs as
Unity Catalog files after the customer accepts the evaluation terms. Deliver
immutable production releases through Yanbor LLC's authenticated Maven
repository or another approved private artifact channel after commercial
licensing.

The Databricks listing is a discovery, evaluation, and controlled-fulfillment
surface. It does not change DataAI ETL into SaaS.

## Runtime validation target

- Java baseline: 17
- Spark build baseline: 3.5.0
- Scala binary baseline: 2.12
- Databricks validation target: Runtime 16.4 LTS, Scala 2.12 image
- Library source: Unity Catalog volume or authenticated Maven repository
- Recommended compute: standard or dedicated access mode

Databricks Runtime 16.4 LTS uses Spark 3.5.2 and offers a Scala 2.12 image. The
package has not been executed on an external Databricks workspace from this
repository. Complete the workspace validation checklist before marketplace
submission or any compatibility claim.

## Generate and validate

Build the Spark reactor first, then run:

```powershell
Set-Location C:\Projects\DataAI.Etl
& C:\Users\Irina\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\Databricks\scripts\generate_databricks_assets.py
& C:\Users\Irina\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe .\Databricks\scripts\validate_databricks_package.py
```

Generation is local and does not publish, upload, authenticate, or contact a
Databricks workspace.

## Start here

1. Read `MARKETPLACE_SUBMISSION.md` for the provider workflow.
2. Read `docs/INSTALLATION_AND_USAGE.md` for customer installation.
3. Import and run `notebooks/00_INSTALL_AND_VERIFY.py` first.
4. Use `docs/FUNCTION_CATALOG.md` for the complete DataAI function list.
5. Replace every bracketed Marketplace placeholder before submission.

## License

Evaluation is governed by `LICENSE.md`. Production, continued use,
redistribution, OEM, and managed-service use require separate written
commercial terms from Yanbor LLC. The software is provided **AS IS**, and the
customer is responsible for evaluating compatibility and suitability during
the permitted evaluation period.
