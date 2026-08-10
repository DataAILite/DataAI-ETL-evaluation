# DataAI ETL for InterSystems IRIS

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

`dataai-spark-iris` is an optional customer-side adapter that connects DataAI
Spark pipelines to InterSystems IRIS through Spark's standard JDBC data source.
It is an embedded library, not a service. It performs no telemetry, credential
logging, automatic persistence, or customer-data transmission.

The artifact depends transitively on `dataai-spark-functions`, so every DataAI
ETL, quality, analytics, time-series, business, market, map, matrix, and insight
function is available to IRIS pipelines.

## Contents

| Path | Purpose |
| --- | --- |
| `src/` | Java IRIS JDBC adapter, function-output metadata, and Spark tests |
| `examples/` | Java, SQL, and `spark-submit` customer examples |
| `mapping/` | IRIS table contracts and complete function coverage |
| `sample-data/` | Fictional evaluation orders and matrix targets |
| `ipm/` | Optional free IRIS-native IPM bootstrap module |
| `listing/` | InterSystems Open Exchange listing copy and checklist |
| `assets/`, `screenshots/` | Generated marketplace icon and fictional-data previews |
| `scripts/` | Deterministic asset generation and offline validation |
| `distribution/` | Generated evaluation ZIP; never publish it anonymously |

## 1. Runtime baseline

- Java 17
- Apache Spark 3.5.0
- Scala binary version 2.12
- InterSystems IRIS reachable through its Superserver JDBC port
- A customer-approved InterSystems JDBC driver compatible with the target IRIS
  and Java versions

The adapter does not bundle the InterSystems JDBC driver. Customers can use
the driver shipped with their IRIS installation or an approved
`com.intersystems:intersystems-jdbc` version. Confirm its license and exact
server/Java compatibility before production use.

## 2. Build and test

```powershell
Set-Location C:\Projects\DataAI.Etl\spark
mvn clean verify
```

The reactor creates:

```text
C:\Projects\DataAI.Etl\IRIS\target\dataai-spark-iris-0.1.0-SNAPSHOT.jar
```

`0.1.0-SNAPSHOT` is an evaluation/development version, not a production
release.

## 3. Add customer dependencies

```xml
<dependency>
  <groupId>com.dataai</groupId>
  <artifactId>dataai-spark-iris</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>

<dependency>
  <groupId>com.intersystems</groupId>
  <artifactId>intersystems-jdbc</artifactId>
  <version>${customer.approved.iris.jdbc.version}</version>
  <scope>runtime</scope>
</dependency>
```

Spark remains `provided`. Do not force a JDBC driver version that conflicts
with the customer's supported IRIS runtime.

## 4. Configure IRIS without logging credentials

```java
IrisJdbcOptions iris = IrisJdbcOptions
        .forServer("iris.internal", 1972, "DATAAI")
        .credentials(
                System.getenv("IRIS_USER"),
                System.getenv("IRIS_PASSWORD"))
        .fetchSize(5000)
        .batchSize(1000)
        .build();
```

`IrisJdbcOptions.toString()` reports only whether credentials are configured;
it never returns the user or password. Use the customer's secret manager in
production rather than embedding credentials in source code or job arguments.

## 5. Read IRIS data

For bounded sources:

```java
Dataset<Row> input = IrisDataFrames.readTable(
        spark, iris, "Source.CustomerOrders");
```

For a large table with a suitable numeric partition field:

```java
Dataset<Row> input = IrisDataFrames.readTablePartitioned(
        spark,
        iris,
        "Source.CustomerOrders",
        "OrderSequence",
        1,
        10_000_000,
        16);
```

Bounds divide the range; they do not filter source rows. Choose the partition
column and concurrency with the IRIS administrator after testing connection and
workload limits.

## 6. Run DataAI

```java
DataAiResult result = DataAiPipeline.fromDataset(input)
        .normalize()
        .recordKey("order_id")
        .profile()
        .validate(
                RuleSpec.required("customer-required", "customer_id"),
                RuleSpec.minimum("amount-nonnegative", "amount", 0))
        .execute();

IrisPipelineOutputBundle outputs = IrisPipelineOutputs.from(result);
```

The prepared outputs contain run, completion, library-version, result-name,
and platform metadata. The adapter still performs no write.

## 7. Persist explicitly

```java
IrisDataFrames.writer(outputs.qualityFindings(), iris)
        .option("dbtable", IrisOutputNames.QUALITY_FINDINGS)
        .mode(SaveMode.Append)
        .save();
```

The caller must choose the table, save mode, and invoke `save()`. For
production, prefer staging tables plus an IRIS-controlled merge procedure over
unreviewed overwrite operations.

## 8. Use all functions, including matrix balancing

Every result DataFrame can receive consistent IRIS audit fields:

```java
Dataset<Row> irisResult = IrisFunctionOutputs.withRunMetadata(
        functionResult,
        "market_demand",
        runId,
        Instant.now(),
        libraryVersion);
```

Matrix balancing has a dedicated conversion:

```java
Dataset<Row> irisMatrix = IrisFunctionOutputs.matrixBalance(
        matrixBalanceResult,
        runId,
        Instant.now(),
        libraryVersion);
```

It retains balanced cells and adds convergence, iteration, and maximum-error
metadata. See `examples/java/IrisMatrixBalancingExample.java`.

## 9. Evaluation

1. Review `LICENSE.md`; the standard evaluation is less than 32 consecutive
   calendar days.
2. Use an isolated IRIS namespace and non-production Spark cluster.
3. Load only `sample-data/` or customer-approved non-production data.
4. Grant a dedicated identity minimum source-read and output-write privileges.
5. Run the pipeline example and inspect the six suggested result tables.
6. Test representative analytical functions and matrix convergence.
7. Measure JDBC partitioning, fetch size, batch size, and connection count.
8. Complete security and suitability acceptance before commercial purchase.

## 10. Open Exchange and IPM boundary

InterSystems Open Exchange is the discovery and approval channel. The listing
must point to DataAI's controlled evaluation/commercial fulfillment page; do
not upload licensed production JARs or credentials publicly.

The optional IPM module installs only free IRIS-native bootstrap metadata. It
does not include or download the commercial Spark JAR. Publish it to the public
IPM registry only after testing `module.xml` in the supported IRIS/IPM versions.

See `listing/INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md` and `ipm/README.md`.

## 11. Generate and validate distribution assets

```powershell
python .\scripts\generate_iris_assets.py
python .\scripts\validate_iris_package.py
```

The generated evaluation ZIP is for controlled delivery. Regenerate it after
the final Maven build so it contains the adapter JAR and current checksums.

## 12. Production gates

- Replace `SNAPSHOT` with an immutable licensed version.
- Test the exact Java, Spark, IRIS server, JDBC driver, namespace, and SQL
  configuration.
- Confirm third-party driver licensing.
- Scan dependencies and produce an SBOM.
- Verify SHA-256 checksums and JAR contents.
- Establish staging/merge, retry, transaction, and partial-failure behavior.
- Complete customer security, privacy, healthcare, and performance review.
- Publish only after explicit release approval.

DataAI software is provided **AS IS**, with no obligations except those
expressly accepted in a signed commercial agreement or order form.
