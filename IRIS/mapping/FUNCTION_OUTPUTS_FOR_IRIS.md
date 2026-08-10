# Complete DataAI Function Coverage for IRIS

`dataai-spark-iris` depends on `dataai-spark-functions`, so it exposes the full
portable DataAI catalog without copying algorithms into the IRIS adapter.

| Family | APIs |
| --- | --- |
| ETL and declarative validation | `DataAiPipeline`, `RuleSpec` |
| Automatic quality diagnostics | `DataQualityFunctions` |
| Statistics, pivot, variance, ranking, correlation, regression | `AnalyticsFunctions` |
| Time summaries and rolling analysis | `TimeSeriesFunctions` |
| Outliers, anomalies, drift, Pareto, cohorts, funnels, KPIs | `BusinessFunctions` |
| Demand, pricing, elasticity, baskets, segments, churn, risk, inventory, profit, scenarios | `MarketFunctions` |
| Geographic readiness | `MapFunctions` |
| Cross-tabs and iterative matrix balancing | `MatrixFunctions` |
| Dictionaries, chart recommendations, local narratives, alerts | `InsightFunctions` |

Pass any result DataFrame to `IrisFunctionOutputs.withRunMetadata(...)`, then
use `IrisDataFrames.writer(...)` and explicitly select the IRIS table and save
mode. Result records containing several DataFrames, such as map readiness,
should be persisted as separate named IRIS tables.

The adapter does not execute external AI, host a service, or transmit data to
DataAI. Deterministic narratives remain local; a customer may separately send
governed summaries to its own approved AI integration.
