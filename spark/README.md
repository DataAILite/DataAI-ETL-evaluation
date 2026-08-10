# DataAI Spark SDK

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

For the complete customer workflow, see
[Installation and Usage](../docs/INSTALLATION_AND_USAGE.md).
For the expanded analytical API, see the
[DataAI Spark Function Catalog](../docs/FUNCTION_CATALOG.md).

## Runtime baseline

- Apache Spark 3.5.0
- Java 17
- Scala binary version 2.12

This baseline matches the current Oracle AI Data Platform all-purpose cluster
runtime. Spark is a provided dependency and is not bundled into the product JAR.

## Build

```shell
mvn clean verify
```

Build the runnable customer artifact with:

```shell
mvn -pl dataai-spark-cli -am package
```

The shaded CLI JAR is written beneath `dataai-spark-cli/target/`.

The reactor also builds the optional sibling Tableau adapter:

```text
com.dataai:dataai-spark-tableau:0.1.0-SNAPSHOT
```

Its JAR is written beneath `../Tableau/target/`. It depends on the public
DataAI API and the customer-provided Spark runtime; core DataAI modules do not
depend on Tableau. See [DataAI ETL for Tableau](../Tableau/README.md).

The reactor also builds the optional sibling InterSystems IRIS adapter:

```text
com.dataai:dataai-spark-iris:0.1.0-SNAPSHOT
```

Its JAR is written beneath `../IRIS/target/`. It depends transitively on the
complete functions artifact and uses the customer-selected InterSystems JDBC
driver; the driver is not bundled. Core DataAI modules do not depend on IRIS.
See [DataAI ETL for InterSystems IRIS](../IRIS/README.md).

## Java API

```java
DataAiResult result = DataAiPipeline
    .fromTable(spark, "bronze.customer_orders")
    .normalize()
    .recordKey("order_id")
    .profile()
    .validate(
        RuleSpec.required("customer-required", "customer_id"),
        RuleSpec.minimum("amount-nonnegative", "amount", 0))
    .execute();
```

## Analytics and business functions

Add `com.dataai:dataai-spark-functions:0.1.0-SNAPSHOT` to embed the complete
function library. It includes grouped statistics, pivot, variance, ranking,
correlation, regression, time series, outliers, drift, Pareto, cohort, funnel,
KPI, market models, map readiness, matrix balancing, data dictionary, chart
recommendations, alerts, and local narratives.

## CLI

```shell
spark-submit \
  --class com.dataai.etl.spark.cli.DataAiJob \
  dataai-spark-cli-0.1.0-SNAPSHOT.jar \
  --config /Workspace/DataAI/customer-orders.json
```

The example configuration is in `../examples/oracle-aidp/`.
