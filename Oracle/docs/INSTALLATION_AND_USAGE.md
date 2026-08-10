# Installation and Usage for Oracle Cloud Marketplace

## Delivery model

The container stores DataAI JARs in `/opt/dataai/lib`. For OCI Data Flow, the customer copies licensed artifacts to customer-controlled Object Storage and supplies their URIs as Spark job dependencies. No Yanbor-hosted runtime or customer-data transfer is required.

## Evaluation artifacts

Install these matching-version modules together:

- `dataai-spark-api-0.1.0-SNAPSHOT.jar`
- `dataai-spark-quality-0.1.0-SNAPSHOT.jar`
- `dataai-spark-core-0.1.0-SNAPSHOT.jar`
- `dataai-spark-functions-0.1.0-SNAPSHOT.jar`

The CLI JAR is optional. Spark and Hadoop are provided by the customer runtime and are not bundled by DataAI.

## Generic Spark usage

Add all required JARs to the Spark driver and executor classpaths using the target platform's supported library or `--jars` mechanism. Then call `DataAiPipeline` and the functions in `com.dataai.etl.spark.functions`. The complete inventory is in `FUNCTION_CATALOG.md`.

Customer code supplies `Dataset<Row>` inputs and decides whether returned DataFrames are written. DataAI performs no automatic persistence.

## Production

Do not deploy the included SNAPSHOT artifacts as production. After commercial licensing, use a Yanbor-authorized immutable release from the approved marketplace artifact, authenticated Maven repository, or customer artifact repository. Verify checksums and pin the exact version.

## Troubleshooting

- `UnsupportedClassVersionError`: select a Java 17-compatible runtime.
- Class not found: install API, quality, core, and functions at the same version.
- Scala linkage error: use a runtime compatible with Scala 2.12.
- Spark linkage error: validate against the documented Spark 3.5.x baseline.
- Permission failure: use customer-approved identity and storage permissions; DataAI does not bypass platform controls.
