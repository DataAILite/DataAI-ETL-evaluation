# Complete DataAI Function Coverage for Tableau

The `dataai-spark-tableau` Maven artifact depends on
`dataai-spark-functions`, so adding the Tableau artifact makes the complete
DataAI computational catalog available transitively. Algorithms are not copied
into Tableau code; they remain tested once in the portable functions module.

Every DataAI function result is already a Spark `Dataset<Row>` or a small
record containing DataFrames. Pass any result DataFrame to
`TableauFunctionOutputs.withRunMetadata(...)`, persist it under a governed
table/view, and connect Tableau through Spark SQL or Databricks.

## Coverage

| Function family | DataAI APIs available to Tableau pipelines | Suggested result name |
| --- | --- | --- |
| ETL pipeline | `DataAiPipeline`, declarative `RuleSpec` validation | `pipeline_*` |
| Data quality | `DataQualityFunctions` automatic, missing, duplicate, date, outlier, category, and text checks | `quality_*` |
| General analytics | `AnalyticsFunctions` summaries, pivot, variance, ranking, correlations, regression | `analytics_*` |
| Time analysis | `TimeSeriesFunctions` summaries, moving averages, rolling totals, period changes | `time_*` |
| Business analytics | `BusinessFunctions` outliers, anomalies, drift, Pareto, cohort, funnel, KPI | `business_*` |
| Market models | `MarketFunctions` demand, pricing, elasticity, basket, segments, churn, risk, inventory, profit, scenario | `market_*` |
| Geographic | `MapFunctions.readiness(...)` and all returned readiness DataFrames | `map_*` |
| Matrix | `MatrixFunctions.crossTab(...)` and `MatrixFunctions.balance(...)` | `matrix_cross_tab`, `matrix_balance` |
| Insights | `InsightFunctions` dictionary, chart recommendations, narratives, and alerts | `insight_*` |

## Universal adapter

```java
Dataset<Row> tableauResult = TableauFunctionOutputs.withRunMetadata(
        dataAiFunctionResult,
        "market_demand",
        runId,
        completedAt,
        libraryVersion);

tableauResult.write()
        .format("delta")
        .mode(SaveMode.Overwrite)
        .saveAsTable("analytics.dataai_market_demand");
```

The added reserved columns are:

- `_dataai_result_name`
- `_dataai_run_id`
- `_dataai_completed_at`
- `_dataai_library_version`

The adapter rejects a result that already contains one of these names instead
of silently overwriting customer data.

## Matrix balancing

Matrix balancing is explicitly supported. Use
`TableauFunctionOutputs.matrixBalance(...)` to expose `balancedCells()` plus:

- `balance_iterations`
- `balance_maximum_error`
- `balance_converged`

The output retains the DataAI matrix fields: original value, balanced value,
row and column targets, balanced totals, differences, and coefficients. The
complete persistence example is
`../examples/java/TableauMatrixBalancingExample.java`.

Tableau can visualize the balanced values as a heat map, highlight target
differences, filter to non-converged runs, and compare original versus balanced
values. The customer's Spark job remains responsible for convergence policy and
must decide whether a non-converged result may be published.
