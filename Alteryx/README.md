# DataAI ETL for Alteryx

DataAI ETL is proprietary, source-available evaluation software from Yanbor
LLC, built with open-source technologies including Apache Spark.

This package adds **DataAI ETL Quality** to an Alteryx Designer workflow. The
tool launches the included DataAI Spark CLI with the customer's own
`spark-submit`, Spark catalog, compute, credentials, and output tables. It is
an embedded library adapter, not a Yanbor-hosted service.

## Included capability

The Alteryx tool UI exposes the runnable DataAI quality pipeline:

- optional string normalization;
- field profiling;
- DataAI validation rules;
- clean and rejected row separation;
- findings and profile outputs;
- overall quality scoring and an optional minimum-score gate.

The evaluation distribution also includes the DataAI Spark API, core, quality,
functions, and shaded CLI JARs. Advanced Java/Spark APIs—including analytics,
market, map, time-series, insight, and matrix-balancing functions—are listed in
`docs/FUNCTION_CATALOG.md`. Those advanced functions are libraries for a
customer Spark job; version 1.0 of the Alteryx UI does not expose each one as a
separate Designer tool.

## Data handling

- No DataAI hosted service is required.
- No customer data or credentials are sent to Yanbor LLC.
- No telemetry, remote license check, or required DataAI network call exists.
- The adapter starts `spark-submit` with an argument vector and `shell=False`.
- A temporary JSON job configuration is created locally and deleted when the
  process finishes.
- Named output tables are deliberately written with Delta `Overwrite` mode.
  Leave an output table blank to skip that write.

## Package status

`0.1.0-SNAPSHOT` is an evaluation/development build. The generated YXI targets
Alteryx Designer 2026.1 with AMP and embedded Python 3.13.11. Its code and
archive structure are validated offline, but it has not yet been executed in
Alteryx Designer in this environment. Complete `PROVIDER_CHECKLIST.md` before
submitting the version file to Alteryx Marketplace or granting production use.

## Start here

1. Read `LICENSE.md`.
2. Follow `docs/INSTALLATION_AND_USAGE.md`.
3. Install `distribution/DataAI_ETL_Alteryx_Evaluation.zip` contents.
4. Double-click the included `.yxi`, enable AMP, and configure the tool.
5. Run the sample test and record results in `PROVIDER_CHECKLIST.md`.

Yanbor LLC is the provider of the DataAI product. Commercial production rights
are available under a signed agreement based on
`COMMERCIAL_LICENSE_TEMPLATE.md`.
