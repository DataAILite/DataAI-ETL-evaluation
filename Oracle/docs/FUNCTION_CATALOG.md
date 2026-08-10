# DataAI Spark Function Catalog

`dataai-spark-functions` contains the portable computational capabilities from
the DataAI application. The functions accept Spark `Dataset<Row>` objects and
return Spark DataFrames or small result records that contain DataFrames.

The library has no web server, database service, or external AI requirement.
It executes inside the customer's Spark application and leaves persistence,
scheduling, security, and orchestration under customer control.

## Add the functions artifact

```xml
<dependency>
  <groupId>com.dataai</groupId>
  <artifactId>dataai-spark-functions</artifactId>
  <version>0.1.0-SNAPSHOT</version>
</dependency>
```

Install all modules locally during source development:

```powershell
Set-Location C:\Projects\DataAI.Etl\spark
mvn clean install
```

## Function families

### ETL and quality

| DataAI capability | Spark API | Result |
| --- | --- | --- |
| Normalize fields | `DataAiPipeline.normalize()` | Snake-case names, trimmed strings, blank-to-null values |
| Deterministic record key | `DataAiPipeline.recordKey(...)` | SHA-256 `_dataai_record_key` |
| Field profiling | `FieldProfiler.profile(...)` | Counts, nulls, distinct values, range, mean, and standard deviation |
| Declarative validation | `DataAiPipeline.validate(...)` | Findings plus clean and rejected DataFrames |
| Automatic quality checks | `DataQualityFunctions.automaticChecks(...)` | Missing, duplicate, date, outlier, category, and text issues |
| Missing-value summary | `DataQualityFunctions.missingValueSummary(...)` | Affected fields and record counts |
| Duplicate-record summary | `DataQualityFunctions.duplicateRecordSummary(...)` | Complete duplicate count |
| Invalid-date summary | `DataQualityFunctions.invalidDateSummary(...)` | Invalid date-like text counts |
| Numeric-outlier summary | `DataQualityFunctions.numericOutlierSummary(...)` | Field-level outlier counts |
| Category consistency | `DataQualityFunctions.inconsistentCategorySummary(...)` | Case/spacing/punctuation variants |
| Suspicious text | `DataQualityFunctions.suspiciousTextSummary(...)` | Whitespace, control, markup, length, and repetition issues |

Declarative rule types are:

- `REQUIRED`
- `UNIQUE`
- `MINIMUM`
- `MAXIMUM`
- `BETWEEN`
- `IN_SET`
- `DATE_FORMAT`
- `LENGTH`
- `EQUALS`
- `REGEX`

Example:

```java
DataAiResult result = DataAiPipeline.fromDataset(input)
        .normalize()
        .recordKey("order_id")
        .profile()
        .validate(
                RuleSpec.required("customer-required", "customer_id"),
                RuleSpec.unique("order-unique", "order_id"),
                RuleSpec.between("amount-range", "amount", 0, 100000),
                RuleSpec.inSet("status-values", "status", List.of("Open", "Closed")),
                RuleSpec.dateFormat("order-date", "order_date", "yyyy-MM-dd"),
                RuleSpec.length("reference-length", "reference", 1, 40))
        .execute();
```

### General analytics

| DataAI capability | Spark API |
| --- | --- |
| Grouped descriptive statistics | `AnalyticsFunctions.groupedSummary(...)` |
| Pivot/cross-tab | `AnalyticsFunctions.pivot(...)` |
| Base/comparison variance | `AnalyticsFunctions.variance(...)` |
| Contribution to total | Included in `variance(...)` |
| Top/bottom/average-nearest ranking | `AnalyticsFunctions.ranking(...)` |
| Pairwise correlation | `AnalyticsFunctions.correlations(...)` |
| Correlation threshold | `AnalyticsFunctions.correlationThreshold(...)` |
| Linear regression and prediction | `AnalyticsFunctions.linearRegression(...)` |

Supported aggregations are `COUNT`, `COUNT_DISTINCT`, `SUM`, `MINIMUM`,
`MAXIMUM`, `AVERAGE`, and `STANDARD_DEVIATION`.

```java
Dataset<Row> variance = AnalyticsFunctions.variance(
        input,
        List.of("region"),
        "period",
        "2025",
        "2026",
        "revenue",
        Aggregation.SUM);

Dataset<Row> regression = AnalyticsFunctions.linearRegression(
        input, "units", "revenue", "region", 100.0);
```

### Time analysis

| DataAI capability | Spark API |
| --- | --- |
| Day/week/month/quarter/year summary | `TimeSeriesFunctions.summarize(...)` |
| Moving average | `TimeSeriesFunctions.rolling(..., MOVING_AVERAGE)` |
| Rolling total | `TimeSeriesFunctions.rolling(..., ROLLING_TOTAL)` |
| Period-over-period change | Included in `rolling(...)` |

```java
Dataset<Row> rolling = TimeSeriesFunctions.rolling(
        input,
        List.of("region"),
        "order_date",
        TimePeriod.MONTH,
        "revenue",
        Aggregation.SUM,
        3,
        RollingOperation.MOVING_AVERAGE);
```

### Business analytics

| DataAI capability | Spark API |
| --- | --- |
| Standard-deviation outliers | `BusinessFunctions.outliers(...)` |
| Percentage-difference outliers | `BusinessFunctions.outliers(...)` |
| Business minimum/maximum outliers | `BusinessFunctions.outliers(...)` |
| Transparent anomaly scores | `BusinessFunctions.anomalyScores(...)` |
| Distribution drift | `BusinessFunctions.drift(...)` |
| ABC/Pareto classification | `BusinessFunctions.pareto(...)` |
| Cohort retention | `BusinessFunctions.cohort(...)` |
| Funnel conversion/drop-off | `BusinessFunctions.funnel(...)` |
| KPI ratio/difference/sum/product | `BusinessFunctions.kpi(...)` |

```java
Dataset<Row> pareto = BusinessFunctions.pareto(
        input, "product", "revenue", Aggregation.SUM);

Dataset<Row> cohorts = BusinessFunctions.cohort(
        input, "customer_id", "activity_date", "revenue", TimePeriod.MONTH);
```

### Market models

| DataAI capability | Spark API |
| --- | --- |
| Demand and projected demand | `MarketFunctions.demand(...)` |
| Price-band sensitivity | `MarketFunctions.pricing(...)` |
| Price elasticity projection | `MarketFunctions.elasticity(...)` |
| Basket co-occurrence/support | `MarketFunctions.basket(...)` |
| Segment summaries | `MarketFunctions.segments(...)` |
| Churn/retention score | `MarketFunctions.churn(...)` |
| Relative exposure risk | `MarketFunctions.risk(...)` |
| Inventory velocity/reorder point | `MarketFunctions.inventory(...)` |
| Profit/margin/contribution | `MarketFunctions.profit(...)` |
| Downside/base/upside scenario | `MarketFunctions.scenario(...)` |

```java
Dataset<Row> demand = MarketFunctions.demand(
        input,
        List.of("region", "product"),
        "units",
        "order_date",
        TimePeriod.MONTH,
        10.0);

Dataset<Row> profit = MarketFunctions.profit(
        input,
        List.of("region", "product"),
        "revenue",
        "direct_cost",
        null,
        null,
        0);
```

Assumption arguments use percentage points: `10.0` means 10 percent.

### Geographic analysis

`MapFunctions.readiness(...)` returns a `MapReadinessResult` containing:

- classified source rows;
- a readiness summary;
- valid-coordinate rows;
- invalid-coordinate rows;
- suggested latitude fields;
- suggested longitude fields.

Checks classify missing coordinates, invalid latitude/longitude ranges,
duplicate locations, valid coordinates without a name, and KML-ready rows.

```java
MapReadinessResult map = MapFunctions.readiness(
        input, "latitude", "longitude", "location_name");
```

### Matrix analysis and balancing

`MatrixFunctions.crossTab(...)` produces a Spark pivot. `balance(...)` performs
iterative proportional fitting against row and column control totals.

```java
MatrixBalanceResult balanced = MatrixFunctions.balance(
        cells,
        "region",
        "category",
        "value",
        rowTargets,
        columnTargets,
        "target_total",
        50,
        0.001);

if (!balanced.converged()) {
    throw new IllegalStateException("Matrix controls did not converge");
}
```

The balanced output includes original and balanced values, balancing
coefficients, row/column targets, final totals, differences, and convergence
metadata.

### Data dictionary, recommendations, alerts, and narratives

| DataAI capability | Spark API |
| --- | --- |
| Data dictionary and detected roles | `InsightFunctions.dataDictionary(...)` |
| Chart recommendations | `InsightFunctions.chartRecommendations(...)` |
| Automated local narratives | `InsightFunctions.narratives(...)` |
| Rule-based alerts | `InsightFunctions.ruleBasedAlerts(...)` |

Narratives are deterministic and local. They do not send customer data to an
external AI endpoint. Customers can optionally send the returned, governed
summary DataFrame to their own approved AI integration.

## Platform output adapters

### Tableau output adapter

Add `com.dataai:dataai-spark-tableau:0.1.0-SNAPSHOT` when a Spark application
needs standardized DataAI outputs for Tableau. `TableauOutputs.from(...)`
accepts a `DataAiResult` and returns a `TableauOutputBundle` containing:

- `cleanRows()` and `rejectedRows()`;
- `qualityFindings()` and `fieldProfiles()`;
- a one-row `pipelineRuns()` DataFrame;
- a one-row `dashboardMetrics()` DataFrame with row totals, quality score,
  finding counts by severity, profile count, and total null values.

`TableauOutputNames` provides stable default table-name constants. The adapter
does not persist, cache, collect, connect to Tableau, or make network calls.
The customer explicitly writes the returned DataFrames to a format/catalog
visible through Tableau's native Spark SQL or Databricks connector.

The Tableau artifact depends on `dataai-spark-functions`, so the complete
function catalog in this document is available transitively. Use
`TableauFunctionOutputs.withRunMetadata(...)` with any function-result
DataFrame. It adds reserved result name, run ID, completion time, and library
version fields without executing or persisting the DataFrame.

`TableauFunctionOutputs.matrixBalance(...)` additionally converts a
`MatrixBalanceResult` and adds iteration count, maximum error, and convergence
fields. This makes matrix balancing explicitly available for Tableau heat maps,
target-difference analysis, and run filtering.

```java
TableauOutputBundle tableau = TableauOutputs.from(result);

tableau.dashboardMetrics().write()
        .format("delta")
        .mode(SaveMode.Append)
        .saveAsTable("analytics.dataai_dashboard_metrics");
```

The exact schemas and multi-run history guidance are in
[`Tableau/mapping/TABLEAU_OUTPUT_SCHEMA.md`](../Tableau/mapping/TABLEAU_OUTPUT_SCHEMA.md).
Complete function-to-Tableau coverage is documented in
[`Tableau/mapping/FUNCTION_OUTPUTS_FOR_TABLEAU.md`](../Tableau/mapping/FUNCTION_OUTPUTS_FOR_TABLEAU.md).

### InterSystems IRIS adapter

Add `com.dataai:dataai-spark-iris:0.1.0-SNAPSHOT` when DataAI must read from or
write approved outputs to InterSystems IRIS. `IrisJdbcOptions` creates a safe,
customer-controlled JDBC configuration; `IrisDataFrames` provides table,
partitioned-table, query, and explicitly invoked writer entry points.

`IrisPipelineOutputs.from(...)` converts a `DataAiResult` into clean, rejected,
finding, profile, and pipeline-run DataFrames with stable IRIS output names.
The adapter never chooses a target table or save mode and never invokes
`save()` for the customer.

The IRIS artifact depends transitively on `dataai-spark-functions`, so every
function in this catalog remains available. Use
`IrisFunctionOutputs.withRunMetadata(...)` for any result DataFrame. Use
`IrisFunctionOutputs.matrixBalance(...)` for matrix balancing; it adds run,
library, platform, convergence, iteration, and maximum-error metadata to the
balanced cells.

The complete contracts and examples are in
[`IRIS/mapping/FUNCTION_OUTPUTS_FOR_IRIS.md`](../IRIS/mapping/FUNCTION_OUTPUTS_FOR_IRIS.md)
and [`IRIS/README.md`](../IRIS/README.md). The adapter uses Spark's standard
JDBC source and does not bundle the InterSystems driver, persist automatically,
collect full data, call a DataAI service, or emit telemetry.

## Execution behavior

Most APIs return lazy Spark DataFrames. Spark executes them only when a caller
runs an action or writes the result. Two APIs intentionally perform actions:

- `AnalyticsFunctions.correlations(...)` calculates one Spark correlation for
  each requested field pair and builds a small result DataFrame on the driver.
- `MatrixFunctions.balance(...)` evaluates convergence after each balancing
  iteration.

Keep correlation field lists bounded and configure matrix iterations and
tolerance appropriate to the data size.

## Capabilities delegated to the customer's platform

The following DataAI application features are not copied into the computation
JAR because Spark or the customer's BI/orchestration platform already owns
them:

| Application feature | Spark ETL equivalent |
| --- | --- |
| CSV, JSON, Parquet, JDBC, and cloud import | `SparkSession.read()` and customer connectors |
| Scheduled imports and reports | Oracle AIDP, Airflow, Fabric, Databricks, or other job scheduler |
| Web dashboards and chart rendering | Power BI, Tableau, Oracle Analytics, or customer UI |
| CSV/Excel/PDF/ZIP downloads | Spark writers and downstream reporting tools |
| User accounts and report permissions | Customer identity, catalog, and platform policy |
| Interactive drill-back pages | Persist `_dataai_record_key` and query source records |
| External generative-AI interpretation | Optional customer-approved AI adapter |

This boundary keeps DataAI ETL an embeddable library rather than turning it
into a hosted service.
