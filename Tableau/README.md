# DataAI ETL for Tableau

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

This folder is the complete customer-side Tableau integration for DataAI ETL.
It is not a hosted service and it does not install a server, send telemetry, or
transmit customer data. The Java adapter converts `DataAiResult` into stable
Spark DataFrames; the customer chooses where and how to persist them. Tableau
then connects with its native Spark SQL or Databricks connector.

The included Accelerator (`accelerator/DataAI_ETL_Accelerator.twbx`) opens with
fictional embedded data for a fast, no-credential evaluation. It can then be
repointed to the customer's DataAI output tables.

## Contents

| Path | Purpose |
| --- | --- |
| `src/` | Optional `com.dataai:dataai-spark-tableau` Java adapter and tests |
| `accelerator/` | Tableau workbook source and packaged Accelerator |
| `sample-data/` | Fictional CSV data and a generated Tableau Hyper extract |
| `mapping/` | Stable output schemas, relationships, and complete function coverage |
| `examples/` | Java persistence, Spark SQL, and Databricks connection examples |
| `listing/` | Tableau Exchange listing copy and submission checklist |
| `assets/`, `screenshots/` | Listing icon and fictional-data design previews |
| `scripts/` | Deterministic asset generator and offline package validator |
| `manifest.json` | Package identity, compatibility, and artifact inventory |
| `LICENSE.md`, `COMMERCIAL_LICENSE_TEMPLATE.md` | Evaluation terms and non-binding commercial sample copied from the repository root |

## 1. Prerequisites

- DataAI ETL Spark `0.1.0-SNAPSHOT` evaluation build
- Java 17
- Apache Spark 3.5.0 with Scala 2.12
- Tableau Desktop or Tableau Cloud/Server for workbook use
- One of:
  - Spark Thrift Server reachable through Tableau's Spark SQL connector; or
  - a Databricks SQL warehouse reachable through Tableau's Databricks
    connector

`0.1.0-SNAPSHOT` is an evaluation/development version, not a production
release. Production distribution should use an immutable licensed version.

## 2. Build and test the adapter

From the Spark reactor root:

```powershell
Set-Location C:\Projects\DataAI.Etl\spark
mvn clean verify
```

The build includes this sibling module and creates:

```text
C:\Projects\DataAI.Etl\Tableau\target\dataai-spark-tableau-0.1.0-SNAPSHOT.jar
```

Spark and Hadoop are provided by the customer runtime and are not bundled in
the adapter JAR.

## 3. Add the adapter to a customer Spark application

Publish the licensed version to the customer's private Maven repository, then
add:

```xml
<dependency>
  <groupId>com.dataai</groupId>
  <artifactId>dataai-spark-tableau</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>
```

The Tableau artifact brings `dataai-spark-functions` transitively, including
all ETL, quality, analytics, time, business, market, map, matrix, and insight
APIs. Spark remains a `provided` dependency.

## 4. Create and persist Tableau outputs

```java
DataAiResult result = DataAiPipeline.fromDataset(input)
        .normalize()
        .recordKey("order_id")
        .profile()
        .validate(RuleSpec.required("customer-required", "customer_id"))
        .execute();

TableauOutputBundle tableau = TableauOutputs.from(result);

tableau.dashboardMetrics().write()
        .format("delta")
        .mode(SaveMode.Append)
        .saveAsTable("analytics.dataai_dashboard_metrics");

tableau.qualityFindings().write()
        .format("delta")
        .mode(SaveMode.Append)
        .saveAsTable("analytics.dataai_quality_findings");

tableau.fieldProfiles().write()
        .format("delta")
        .mode(SaveMode.Append)
        .saveAsTable("analytics.dataai_field_profiles");
```

The adapter itself performs no writes. The complete example is
`examples/java/TableauSparkExample.java`; exact schemas are in
`mapping/TABLEAU_OUTPUT_SCHEMA.md`.

## 5. Use all DataAI functions, including matrix balancing

All function results can be prepared for Tableau with the universal adapter:

```java
Dataset<Row> tableauResult = TableauFunctionOutputs.withRunMetadata(
        dataAiFunctionResult,
        "market_demand",
        runId,
        completedAt,
        libraryVersion);
```

Matrix balancing has a dedicated helper that carries convergence information
into the Tableau table:

```java
MatrixBalanceResult balance = MatrixFunctions.balance(
        cells, "region", "category", "value",
        rowTargets, columnTargets, "target_total", 50, 0.001);

Dataset<Row> tableauMatrix = TableauFunctionOutputs.matrixBalance(
        balance, runId, Instant.now(), libraryVersion);
```

See `mapping/FUNCTION_OUTPUTS_FOR_TABLEAU.md` for the complete family mapping
and `examples/java/TableauMatrixBalancingExample.java` for persistence.

## 6. Test-drive the Tableau experience

1. Copy `accelerator/DataAI_ETL_Accelerator.twbx` to a computer with Tableau
   Desktop.
2. Open it. The workbook uses fictional weekly DataAI run metrics included in
   the package, so no database credentials are required.
3. Review the run trend, acceptance/rejection totals, quality score, and
   finding-severity views.
4. When ready, replace the sample data source with the customer's
   `dataai_dashboard_metrics` table using Tableau's **Replace Data Source**
   command.
5. Add `dataai_quality_findings` and `dataai_field_profiles` for drill-down
   dashboards, relating them by `run_id`.
6. Validate field mappings, refresh behavior, row-level security, and workbook
   permissions in a non-production Tableau project.

The packaged workbook was generated and structurally validated without
Tableau Desktop. Before commercial publication, open it in the supported
Tableau Desktop versions, repair any version-specific metadata, refresh the
extract, and complete visual/accessibility QA.

## 7. Connect Tableau to production outputs

### Spark SQL

1. Persist the DataAI outputs as Spark catalog tables.
2. Make them visible to a Spark Thrift Server session.
3. In Tableau, select **Spark SQL** and enter the server, port, authentication,
   and transport settings supplied by the customer platform team.
4. Select the catalog/schema and the `dataai_*` tables.
5. Relate the run, findings, and profiles tables on `run_id`.

See `examples/spark-sql/README.md` and the official Tableau Spark SQL connector
documentation: https://help.tableau.com/current/pro/desktop/en-us/examples_sparksql.htm

### Databricks

1. Persist the outputs as governed Unity Catalog tables or views.
2. In Tableau, select **Databricks** and supply the server hostname and HTTP
   path for a SQL warehouse.
3. Use the customer's approved OAuth, personal access token, or service
   principal policy.
4. Select the output views and replace the Accelerator's sample source.

See `examples/databricks/README.md` and the official connector documentation:
https://help.tableau.com/current/pro/desktop/en-us/examples_databricks.htm

## 8. Regenerate and validate distribution artifacts

The generator needs Python 3.10+, Pillow, and the Tableau Hyper API. It uses
`Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU`.

```powershell
python .\scripts\generate_tableau_assets.py
python .\scripts\validate_tableau_package.py
```

The Hyper API is build tooling only; it is not a runtime dependency of the
Java adapter. See `THIRD_PARTY_NOTICES.md`.

## 9. Licensing and support boundary

Evaluation and commercial use are governed by `LICENSE.md` and any executed
commercial agreement/order form. The generator copies the canonical license
and commercial template from the repository root so the Tableau folder is
self-contained for evaluation packaging. DataAI software is provided **AS
IS**, with no obligations except those expressly accepted in a signed
commercial agreement.

Customers should evaluate the Accelerator, adapter, connector compatibility,
performance, security, and fitness during the permitted evaluation period
before production purchase or deployment.
