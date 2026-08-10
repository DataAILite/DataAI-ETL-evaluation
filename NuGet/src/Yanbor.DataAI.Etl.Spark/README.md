# Yanbor.DataAI.Etl.Spark

.NET integration helpers for the embedded DataAI Spark libraries. The package
discovers the runtime JARs, builds `spark-submit` commands, writes JSON accepted
by the configuration-driven quality CLI, and exposes the complete function
catalog including matrix balancing.

```powershell
dotnet add package Yanbor.DataAI.Etl.Spark --version 0.1.0-evaluation.1
```

```csharp
var configuration = new DataAiQualityJobConfiguration
{
    SourceTable = "customer.orders",
    CleanTable = "customer.orders_clean",
    RejectedTable = "customer.orders_rejected",
    RecordKeyColumns = ["order_id"],
    Rules =
    [
        DataAiRuleSpec.Required("customer-required", "customer_id"),
        DataAiRuleSpec.Minimum("amount-minimum", "amount", 0)
    ]
};

configuration.WriteJson("dataai-job.json");
var command = DataAiSparkSubmitBuilder.BuildQualityJob("dataai-job.json");
Console.WriteLine(command.ToDisplayString());
```

The helper returns a command description and does not launch a process. The
customer retains control over execution, catalogs, table names, writes,
scheduling, identity, networking, and security.

This prerelease does not provide direct Microsoft.Spark `DataFrame` extension
methods. Complete analytics and matrix functions remain available through the
packaged Java API; direct C# DataFrame invocation requires a separately tested
JVM bridge. No external service is required.

DataAI ETL is proprietary, source-available evaluation software from Yanbor
LLC, built with open-source technologies including Apache Spark.
