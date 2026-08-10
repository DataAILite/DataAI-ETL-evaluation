# DataAI ETL Spark: Installation and Usage

This guide installs and runs `DataAI.Etl.Spark` version
`0.1.0-SNAPSHOT`. DataAI runs inside the customer's Spark job and does not
require a separate DataAI service.

DataAI ETL may be evaluated for less than 32 consecutive calendar days under
the PolyForm Free Trial License 1.0.0. Production, continued use, and
redistribution require separate written commercial terms. Review
[`LICENSE.md`](../LICENSE.md) before distributing or installing the package.
For production licensing, use a completed and signed commercial agreement and
order form. A non-binding starting template is available in
[`COMMERCIAL_LICENSE_TEMPLATE.md`](../COMMERCIAL_LICENSE_TEMPLATE.md).

## 1. Choose an integration mode

Use one of these modes:

1. **Configuration-driven job** — upload one shaded JAR and one JSON file,
   then run them with `spark-submit`. This is the fastest test-drive path.
2. **Embedded Java API** — add the DataAI Maven modules to an existing Spark
   application and call `DataAiPipeline` from application code.

Both modes use the same normalization, profiling, and quality engine. The
embedded API also exposes the full analytical function catalog documented in
[FUNCTION_CATALOG.md](FUNCTION_CATALOG.md).

## 2. Check the runtime prerequisites

The initial release is built and tested with:

- Java 17
- Apache Spark 3.5.0
- Scala binary version 2.12
- Maven 3.9 or later for building from source
- A Spark catalog with Delta Lake support when using the supplied CLI

Spark and Hadoop are `provided` dependencies. They are supplied by the
customer's Spark cluster and are not bundled in the DataAI JAR.

Run these checks on a build machine:

```powershell
java -version
mvn -version
spark-submit --version
```

Confirm that Java reports version 17 and Spark reports the 3.5/Scala 2.12
runtime line. The project was verified with Maven 3.9.9.

## 3. Build and test DataAI ETL

Open PowerShell and move to the Spark project:

```powershell
Set-Location C:\Projects\DataAI.Etl\spark
```

Compile every module and run the Spark integration test:

```powershell
mvn clean verify
```

A successful build ends with `BUILD SUCCESS`. The deployable CLI artifact is:

```text
C:\Projects\DataAI.Etl\spark\dataai-spark-cli\target\dataai-spark-cli-0.1.0-SNAPSHOT.jar
```

The file whose name begins with `original-` is the unshaded intermediate JAR.
Do not deploy that file as the standalone CLI.

To build only the CLI and the modules it needs, use:

```powershell
mvn -pl dataai-spark-cli -am package
```

Optionally calculate a checksum before sending the JAR to a customer:

```powershell
Get-FileHash .\dataai-spark-cli\target\dataai-spark-cli-0.1.0-SNAPSHOT.jar -Algorithm SHA256
```

## 4. Fast test drive with the configuration-driven job

### Step 4.1: Prepare a source table

The CLI reads a catalog table through `spark.table(...)`. Create or identify a
source table, for example:

```sql
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS quarantine;
CREATE SCHEMA IF NOT EXISTS dataai;

CREATE TABLE IF NOT EXISTS bronze.customer_orders (
    order_id STRING,
    customer_id STRING,
    amount DOUBLE,
    email STRING
) USING DELTA;
```

Insert a small test data set:

```sql
INSERT INTO bronze.customer_orders VALUES
    ('1001', 'C-100', 125.50, 'buyer@example.com'),
    ('1002', NULL, 50.00, 'missing-customer@example.com'),
    ('1003', 'C-300', -10.00, 'not-an-email'),
    ('1003', 'C-301', 75.00, 'duplicate@example.com');
```

Use dedicated output tables during evaluation. The current CLI writes target
tables in `Overwrite` mode.

### Step 4.2: Copy and edit the JSON configuration

Start with:

```text
C:\Projects\DataAI.Etl\examples\oracle-aidp\customer-orders.json
```

The supplied file contains:

```json
{
  "sourceTable": "bronze.customer_orders",
  "cleanTable": "silver.customer_orders",
  "rejectedTable": "quarantine.customer_orders",
  "profileTable": "dataai.customer_orders_field_profile",
  "findingsTable": "dataai.customer_orders_quality_finding",
  "normalize": true,
  "recordKeyColumns": ["order_id"],
  "minimumQualityScore": 90.0,
  "rules": [
    {
      "id": "customer-required",
      "type": "REQUIRED",
      "field": "customer_id",
      "severity": "ERROR"
    },
    {
      "id": "order-unique",
      "type": "UNIQUE",
      "field": "order_id",
      "severity": "CRITICAL"
    },
    {
      "id": "amount-nonnegative",
      "type": "MINIMUM",
      "field": "amount",
      "parameter": "0",
      "severity": "ERROR"
    },
    {
      "id": "email-format",
      "type": "REGEX",
      "field": "email",
      "parameter": "^[^@]+@[^@]+\\.[^@]+$",
      "severity": "WARNING"
    }
  ]
}
```

Configuration properties:

| Property | Required | Purpose |
| --- | --- | --- |
| `sourceTable` | Yes | Existing Spark catalog table to read. |
| `cleanTable` | No | Target for records with no findings. |
| `rejectedTable` | No | Target for records with one or more findings. |
| `profileTable` | No | Target for field-level profile metrics. |
| `findingsTable` | No | Target for rule violations. |
| `normalize` | No | Normalizes names and string values when `true`. |
| `recordKeyColumns` | No | Fields used to create the deterministic record key. |
| `minimumQualityScore` | No | Fails the job when the score is below this value. |
| `rules` | No | Quality rules evaluated against every record. |

If `recordKeyColumns` is empty, DataAI hashes the complete normalized record.
If `normalize` is `true`, rule fields and record-key fields must use the
normalized names. For example, `Customer ID` becomes `customer_id`.

### Step 4.3: Run locally or from an edge node

On Windows PowerShell:

```powershell
spark-submit `
  --class com.dataai.etl.spark.cli.DataAiJob `
  C:\Projects\DataAI.Etl\spark\dataai-spark-cli\target\dataai-spark-cli-0.1.0-SNAPSHOT.jar `
  --config C:\Projects\DataAI.Etl\examples\oracle-aidp\customer-orders.json
```

On Linux or macOS:

```shell
spark-submit \
  --class com.dataai.etl.spark.cli.DataAiJob \
  dataai-spark-cli-0.1.0-SNAPSHOT.jar \
  --config customer-orders.json
```

The configuration path is opened by the Spark driver as a local file. In
cluster deploy mode, distribute it with Spark and pass its localized name:

```shell
spark-submit \
  --class com.dataai.etl.spark.cli.DataAiJob \
  --files customer-orders.json \
  dataai-spark-cli-0.1.0-SNAPSHOT.jar \
  --config customer-orders.json
```

### Step 4.4: Verify the results

Inspect the output tables:

```sql
SELECT * FROM silver.customer_orders;
SELECT * FROM quarantine.customer_orders;
SELECT * FROM dataai.customer_orders_quality_finding;
SELECT * FROM dataai.customer_orders_field_profile;
```

The clean and rejected records include `_dataai_record_key`, a SHA-256 key used
to relate records to findings.

The current quality score is:

```text
accepted records / records read * 100
```

An empty source receives a score of `100.0`. The score is rounded to two
decimal places.

When `minimumQualityScore` is configured, the CLI writes the rejected,
findings, and profile tables first. It writes the clean table only if the
quality gate passes. A failed gate exits the job with an error.

## 5. Deploy to an Oracle AI Data Platform Spark environment

Use the following cluster-independent sequence; exact workspace labels can
vary by Oracle AIDP release.

1. Select a Spark 3.5, Java 17, Scala 2.12 runtime with Delta Lake/catalog
   support.
2. Upload `dataai-spark-cli-0.1.0-SNAPSHOT.jar` to a location available to the
   Spark job.
3. Upload the JSON configuration or make it available with Spark's `--files`
   option.
4. Give the job identity permission to read the source table and create or
   replace the four configured target tables.
5. Create the `silver`, `quarantine`, and `dataai` schemas if they do not
   already exist.
6. Create a Spark job with main class
   `com.dataai.etl.spark.cli.DataAiJob`.
7. Pass `--config customer-orders.json` as the application argument.
8. Run the job and inspect its driver log for the DataAI run identifier,
   quality score, and rejected-row count.
9. Query the four result tables to validate access and expected routing.

For the first AIDP evaluation, use separate test schemas because the current
CLI replaces tables named in the output configuration.

## 6. Embed DataAI in an existing Java Spark pipeline

### Step 6.1: Install the modules in a Maven repository

For development from this source tree, install all DataAI modules in the local
Maven repository:

```powershell
Set-Location C:\Projects\DataAI.Etl\spark
mvn clean install
```

For customer distribution, publish the same versioned modules to a private
Maven repository and give the customer read-only repository credentials.

### Step 6.2: Add the functions dependency

Add this dependency to the customer's Spark application's `pom.xml`. It brings
in the core, quality, and public API modules transitively:

```xml
<dependency>
  <groupId>com.dataai</groupId>
  <artifactId>dataai-spark-functions</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>
```

The customer's project must also compile against its own Spark 3.5/Scala 2.12
runtime. Spark should remain a `provided` dependency:

```xml
<dependency>
  <groupId>org.apache.spark</groupId>
  <artifactId>spark-sql_2.12</artifactId>
  <version>3.5.0</version>
  <scope>provided</scope>
</dependency>
```

### Step 6.3: Call the pipeline API

```java
import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.RuleSpec;
import com.dataai.etl.spark.core.DataAiPipeline;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;

SparkSession spark = SparkSession.builder()
        .appName("Customer orders with DataAI")
        .getOrCreate();

DataAiResult result = DataAiPipeline
        .fromTable(spark, "bronze.customer_orders")
        .normalize()
        .recordKey("order_id")
        .profile()
        .validate(
                RuleSpec.required("customer-required", "customer_id"),
                RuleSpec.unique("order-unique", "order_id"),
                RuleSpec.minimum("amount-nonnegative", "amount", 0),
                RuleSpec.regex(
                        "email-format",
                        "email",
                        "^[^@]+@[^@]+\\.[^@]+$"))
        .execute();

result.rejectedRows().write()
        .format("delta")
        .mode(SaveMode.Overwrite)
        .saveAsTable("quarantine.customer_orders");

result.findings().write()
        .format("delta")
        .mode(SaveMode.Overwrite)
        .saveAsTable("dataai.customer_orders_quality_finding");

result.fieldProfiles().write()
        .format("delta")
        .mode(SaveMode.Overwrite)
        .saveAsTable("dataai.customer_orders_field_profile");

result.requireMinimumQualityScore(90.0);

result.cleanRows().write()
        .format("delta")
        .mode(SaveMode.Overwrite)
        .saveAsTable("silver.customer_orders");
```

To start from an existing DataFrame instead of a catalog table, use:

```java
DataAiResult result = DataAiPipeline
        .fromDataset(inputDataFrame)
        .normalize()
        .profile()
        .execute();
```

The API returns Spark DataFrames and does not write them automatically. The
customer controls storage format, save mode, partitioning, catalog, and table
names.

## 7. Supported normalization and quality rules

When normalization is enabled, DataAI:

- converts column names to lower snake case;
- trims leading and trailing whitespace from string values;
- converts empty or whitespace-only strings to `null`;
- stops with an error if two source columns normalize to the same name.

Supported rule types:

| Rule type | `parameter` | Violation condition |
| --- | --- | --- |
| `REQUIRED` | Not used | Value is `null`, empty, or whitespace-only. |
| `UNIQUE` | Not used | A non-null value occurs more than once. |
| `MINIMUM` | Numeric value | Non-null numeric value is below the minimum. |
| `REGEX` | Regular expression | Non-null string does not match the expression. |

Supported severities are `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. In version
`0.1.0-SNAPSHOT`, severity is descriptive metadata: a finding at any severity
routes the associated record to the rejected result.

## 8. Understand the returned data

`DataAiResult` provides:

- `cleanRows()` — source records without findings;
- `rejectedRows()` — source records associated with at least one finding;
- `findings()` — record key, rule, field, severity, code, message, and values;
- `fieldProfiles()` — data type, counts, min/max, mean, and standard deviation;
- `summary()` — run ID, timestamps, status, row counts, score, and library
  version.

The run summary is currently returned to Java callers and printed by the CLI;
it is not yet written to a catalog table.

## 9. Add Tableau dashboards

The optional Tableau module turns `DataAiResult` into stable, Tableau-friendly
Spark DataFrames without adding a service or making automatic writes.
It depends transitively on `dataai-spark-functions`, so all DataAI computation
families—including matrix cross-tabs and iterative matrix balancing—are
available from the same customer dependency.

Build it with the complete reactor, then add this dependency to the customer's
Spark application:

```xml
<dependency>
  <groupId>com.dataai</groupId>
  <artifactId>dataai-spark-tableau</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>
```

Create the output bundle and explicitly persist the desired results:

```java
TableauOutputBundle tableau = TableauOutputs.from(result);

tableau.dashboardMetrics().write()
        .format("delta")
        .mode(SaveMode.Append)
        .saveAsTable("analytics.dataai_dashboard_metrics");
```

For a credential-free test drive, open
`Tableau/accelerator/DataAI_ETL_Accelerator.twbx` in Tableau Desktop. It
contains fictional data. For production, replace its sample data source with
the customer table/view using Tableau's native Spark SQL or Databricks
connector. Full instructions, schemas, examples, Hyper data, validation, and
Tableau Exchange preparation files are in `Tableau/README.md`.

For any analytical result DataFrame, use
`TableauFunctionOutputs.withRunMetadata(...)`. For matrix balancing, use
`TableauFunctionOutputs.matrixBalance(...)` to retain convergence, iteration,
and maximum-error metadata before persisting the balanced cells. See
`Tableau/mapping/FUNCTION_OUTPUTS_FOR_TABLEAU.md`.

The generated TWBX is structurally validated but must be opened, rendered,
and interaction-tested in supported Tableau Desktop versions before customer
or marketplace publication.

## 10. Add InterSystems IRIS

The optional IRIS module embeds the complete DataAI Spark function library and
connects to customer-controlled IRIS SQL tables through Spark JDBC. Build the
full reactor, then add this dependency to the customer's Spark application:

```xml
<dependency>
  <groupId>com.dataai</groupId>
  <artifactId>dataai-spark-iris</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>
```

Add a customer-approved InterSystems JDBC driver separately. The DataAI JAR
does not bundle or pin that driver. Configure IRIS from a secret manager, read
the source, run DataAI, then explicitly write only approved outputs:

```java
IrisJdbcOptions iris = IrisJdbcOptions
        .forServer("iris.internal", 1972, "DATAAI")
        .credentials(System.getenv("IRIS_USER"), System.getenv("IRIS_PASSWORD"))
        .fetchSize(5000)
        .batchSize(1000)
        .build();

Dataset<Row> input = IrisDataFrames.readTable(
        spark, iris, "Source.CustomerOrders");

DataAiResult result = DataAiPipeline.fromDataset(input)
        .normalize()
        .recordKey("order_id")
        .profile()
        .validate(RuleSpec.required("customer-required", "customer_id"))
        .execute();

IrisPipelineOutputBundle outputs = IrisPipelineOutputs.from(result);
IrisDataFrames.writer(outputs.qualityFindings(), iris)
        .option("dbtable", IrisOutputNames.QUALITY_FINDINGS)
        .mode(SaveMode.Append)
        .save();
```

All analytical results can be prepared with
`IrisFunctionOutputs.withRunMetadata(...)`. Matrix balancing uses
`IrisFunctionOutputs.matrixBalance(...)`, which retains iteration,
maximum-error, and convergence metadata. Complete setup, SQL, evaluation,
Open Exchange/IPM, licensing, and production-gate instructions are in
`IRIS/README.md`.

## 11. Troubleshooting

### `ClassNotFoundException` for a Spark class

Run the JAR with `spark-submit`, not plain `java -jar`. Confirm the cluster
supplies Spark 3.5 and Scala 2.12.

### `DATA_SOURCE_NOT_FOUND: delta`

The CLI writes Delta tables. Enable a compatible Delta Lake runtime on the
cluster, or use the embedded Java API and select a supported output format.

### Configuration file is not found in cluster mode

The driver must see the JSON as a local file. Use `--files` and pass the
localized filename to `--config`.

### Source or target schema is not found

Create the catalog schemas first and grant the Spark job identity permission
to read the source and replace the target tables.

### A rule reports a missing field

Check spelling and case. When normalization is enabled, configure the
normalized field name, such as `customer_id`, not `Customer ID`.

### Column normalization creates a duplicate name

Rename one of the source columns. For example, `Customer-ID` and `Customer ID`
both normalize to `customer_id`.

### The job fails after writing diagnostic tables

This is expected when `minimumQualityScore` is not met. Review the findings and
rejected tables, correct the source data or rule configuration, and rerun.

### Jackson/Scala module compatibility error

Use the provided shaded CLI JAR without replacing its Jackson libraries. The
project intentionally uses Jackson 2.15.3 for Spark 3.5 compatibility.

### Windows reports that `winutils.exe` is missing during tests

Local Spark may emit this warning on Windows. It is non-fatal when the Maven
tests finish with `BUILD SUCCESS`; production clusters should use their normal
Hadoop runtime configuration.

## 12. Production-readiness checklist

Before production use:

1. Replace `0.1.0-SNAPSHOT` with a released, immutable version.
2. Publish the JARs to an authenticated artifact repository.
3. Record and verify SHA-256 checksums.
4. Include `LICENSE.md` and verify that production users have a written DataAI
   commercial agreement, order form, or license certificate.
5. Test against the customer's exact Spark, Delta, and catalog runtime.
6. Replace evaluation output names with governed production schemas.
7. Decide whether outputs should overwrite, append, or merge by run.
8. Add monitoring around job failure and the minimum quality score.
9. Retain findings and profile tables according to customer policy.
10. Validate performance and partitioning with production-scale data.
11. For Tableau distribution, open/resave the Accelerator in a supported
    Tableau Desktop version, validate native connector replacement, and use an
    immutable licensed adapter version rather than the `SNAPSHOT` build.
12. For IRIS distribution, test the exact IRIS server, namespace, JDBC driver,
    Java, Spark, authentication, SQL types, read partitioning, write strategy,
    retry behavior, and least-privilege identity before release.
