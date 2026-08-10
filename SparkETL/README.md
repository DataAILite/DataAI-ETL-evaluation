# DataAI ETL Spark Marketplace Kit

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

This directory is the complete submission and controlled-evaluation kit for
the DataAI ETL Spark libraries. DataAI executes inside the customer's Spark
application. It is not a hosted service and does not require telemetry,
call-home licensing, customer-data transmission, or automatic persistence.

## Contents

| Path | Purpose |
| --- | --- |
| `MARKETPLACE_SUBMISSION.md` | Channel selection, upload map, and release gates |
| `listing/` | Marketplace and artifact-catalog listing copy |
| `lib/` | Verified binary, source, and Javadoc JARs |
| `poms/` | Maven parent and module build descriptors |
| `docs/` | Installation guide and complete function catalog |
| `examples/` | Oracle AIDP and customer configuration examples |
| `source/` | Evaluation/reviewer source and tests |
| `assets/`, `screenshots/` | DataAI-branded marketplace media |
| `distribution/` | Controlled customer evaluation ZIP |
| `scripts/` | Deterministic generation and offline validation |
| `CHECKSUMS.sha256` | Integrity manifest for the submission kit |
| `../SparkETL.zip` | Final marketplace-review archive at the repository root |
| `../SparkETL.zip.sha256` | SHA-256 digest for the final archive at the repository root |

## Runtime baseline

- Apache Spark 3.5.0
- Java 17
- Scala binary version 2.12
- Spark and Hadoop supplied by the customer runtime

## Customer Maven coordinates

```text
com.dataai:dataai-spark-api:0.1.0-SNAPSHOT
com.dataai:dataai-spark-quality:0.1.0-SNAPSHOT
com.dataai:dataai-spark-core:0.1.0-SNAPSHOT
com.dataai:dataai-spark-functions:0.1.0-SNAPSHOT
com.dataai:dataai-spark-cli:0.1.0-SNAPSHOT
```

The `SNAPSHOT` coordinate is for evaluation only. A commercial or public
release must use an immutable released version and a namespace controlled by
Yanbor LLC.

## Build and verify

```powershell
Set-Location C:\Projects\DataAI.Etl\spark
mvn clean verify
```

## Embedded use

Add `dataai-spark-core` for the pipeline API and `dataai-spark-functions` for
the complete analytical library. Spark remains a `provided` dependency.

```java
DataAiResult result = DataAiPipeline
        .fromTable(spark, "bronze.customer_orders")
        .normalize()
        .recordKey("order_id")
        .profile()
        .validate(RuleSpec.required("customer-required", "customer_id"))
        .execute();
```

## CLI use

```shell
spark-submit \
  --class com.dataai.etl.spark.cli.DataAiJob \
  dataai-spark-cli-0.1.0-SNAPSHOT.jar \
  --config customer-orders.json
```

## Generate and validate

Run after the complete Maven build:

```powershell
python .\scripts\generate_spark_marketplace_assets.py
python .\scripts\validate_spark_marketplace_package.py
```

## License

Evaluation is governed by `LICENSE.md`. Production, continued use,
redistribution, OEM use, managed-service use, and commercial source rights
require written terms from Yanbor LLC. Software is provided **AS IS**, with no
obligations except those expressly accepted in a signed commercial agreement
or order form.
