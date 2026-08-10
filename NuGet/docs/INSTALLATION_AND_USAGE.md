# DataAI ETL NuGet Installation and Usage

## Requirements

- .NET 8 SDK or runtime for the consuming application
- Java 17
- Apache Spark 3.5-compatible runtime
- Scala binary version 2.12
- Customer-controlled Spark catalog, storage, identity, and compute

## Install from a private feed

```powershell
dotnet nuget add source "<PRIVATE-FEED-URL>" --name DataAI
dotnet add package Yanbor.DataAI.Etl.Spark `
  --version 0.1.0-evaluation.1 `
  --source DataAI
```

`Yanbor.DataAI.Etl.Spark` depends on
`Yanbor.DataAI.Etl.Spark.Runtime`, so one command installs both packages. At
build and publish time, the runtime package copies four unshaded library JARs
to `dataai/jars` and the shaded CLI JAR to `dataai/cli`.

## Create a quality job

```csharp
using Yanbor.DataAI.Etl.Spark;

var configuration = new DataAiQualityJobConfiguration
{
    SourceTable = "evaluation.orders",
    CleanTable = "evaluation.orders_clean",
    RejectedTable = "evaluation.orders_rejected",
    ProfileTable = "evaluation.orders_profiles",
    FindingsTable = "evaluation.orders_findings",
    Normalize = true,
    RecordKeyColumns = ["order_id"],
    Rules =
    [
        DataAiRuleSpec.Required("customer-required", "customer_id"),
        DataAiRuleSpec.Between("amount-range", "amount", 0, 100000)
    ],
    MinimumQualityScore = 95
};

configuration.WriteJson("dataai-job.json");
var runtime = DataAiSparkRuntimeLayout.Discover();
var command = DataAiSparkSubmitBuilder.BuildQualityJob(
    "dataai-job.json",
    runtime,
    new DataAiSparkSubmitOptions { Master = "local[2]" });

Console.WriteLine(command.ToDisplayString());
```

The builder returns an executable name and argument list. The consuming
application decides whether, where, and under which identity to launch it.

## Use the libraries with another Spark application

```csharp
var command = DataAiSparkSubmitBuilder.BuildLibraryApplication(
    "customer-pipeline.jar",
    options: new DataAiSparkSubmitOptions
    {
        Master = "yarn",
        DeployMode = "cluster",
        ApplicationArguments = ["--input", "customer.orders"]
    });
```

This adds the four unshaded DataAI library JARs through `--jars`; it does not
bundle Spark or Hadoop classes.

## Function coverage

`DataAiFunctionCatalog.All` lists the DataAI ETL, quality, analytics,
time-series, business, market, geographic, insight, and matrix-balancing APIs
included in the runtime. The quality CLI is directly configurable from the
.NET helper. Other functions are invoked through the packaged Java APIs.

Direct Microsoft.Spark `DataFrame` extension methods are not claimed in this
evaluation release. They require a separately implemented and externally
validated JVM bridge. No external DataAI service is required.

## Customer control and writes

The package performs no installation-time or build-time network calls beyond
the customer's configured NuGet restore. The .NET helper does not launch Spark,
send telemetry, or write data. The shaded quality CLI writes only table names
explicitly supplied in the job configuration; blank output names disable the
corresponding write.
