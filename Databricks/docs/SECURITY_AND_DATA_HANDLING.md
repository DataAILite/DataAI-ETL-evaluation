# Security and Data Handling

## Execution boundary

DataAI ETL runs as Java code inside customer-selected Databricks compute. The
customer supplies input DataFrames and decides whether and where output
DataFrames are persisted.

The DataAI libraries do not require:

- A Yanbor-hosted runtime service.
- DataAI telemetry or analytics callbacks.
- Remote license validation.
- Transmission of source rows to Yanbor LLC.
- Automatic writes to Unity Catalog, Delta, cloud storage, or databases.

## Customer responsibilities

The customer controls workspace identity, compute and Job policies, Unity
Catalog objects and grants, network egress, secret storage, input retention,
output destinations, scheduling, and platform audit logs.

## Package controls

- Validate SHA-256 checksums before installing JARs.
- Install only artifacts received from an approved Yanbor distribution channel.
- Keep evaluation and production artifacts in separate governed paths.
- Grant consumers read-only access to shared evaluation files where practical.
- Never store credentials or license certificates in a notebook or shared volume.
- Scan artifacts under the customer's software-supply-chain policy.

## Logging

The examples do not log credentials, connection strings, or complete source
records. Notebook `display()` calls are for fictional evaluation data and
should be removed or restricted for sensitive datasets.

## Marketplace boundary

Databricks Marketplace and cloud-platform processing are governed by the
customer's agreements with Databricks and its cloud provider. Yanbor LLC must
publish accurate public privacy, support, and terms URLs before submission.
