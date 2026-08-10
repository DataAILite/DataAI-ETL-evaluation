using System.Text.Json;
using Yanbor.DataAI.Etl.Spark;
using Yanbor.DataAI.Etl.Spark.Runtime;

string repositoryRoot = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "..", ".."));
string sparkLibraryDirectory = Path.Combine(repositoryRoot, "SparkETL", "lib");
var runtime = new DataAiSparkRuntimeLayout(
    repositoryRoot,
    DataAiRuntimePackage.LibraryJarFileNames
        .Select(fileName => Path.Combine(sparkLibraryDirectory, fileName))
        .ToArray(),
    Path.Combine(sparkLibraryDirectory, DataAiRuntimePackage.CliJarFileName));

Assert(runtime.LibraryJars.All(File.Exists), "All four DataAI library JARs must exist.");
Assert(File.Exists(runtime.CliJar), "The shaded DataAI CLI JAR must exist.");
Assert(
    DataAiFunctionCatalog.All.Any(item => item.Capability == "Matrix balancing"),
    "The .NET catalog must include matrix balancing.");

var configuration = new DataAiQualityJobConfiguration
{
    SourceTable = "evaluation.orders",
    CleanTable = "evaluation.orders_clean",
    RejectedTable = "evaluation.orders_rejected",
    Normalize = true,
    RecordKeyColumns = ["order_id"],
    Rules =
    [
        DataAiRuleSpec.Required("customer-required", "customer_id"),
        DataAiRuleSpec.Between("amount-range", "amount", 0, 100000),
        DataAiRuleSpec.InSet("status-values", "status", "Open", "Closed")
    ],
    MinimumQualityScore = 95
};

string json = configuration.ToJson();
using JsonDocument document = JsonDocument.Parse(json);
Assert(document.RootElement.GetProperty("sourceTable").GetString() == "evaluation.orders", "JSON must use camelCase.");
Assert(document.RootElement.GetProperty("rules")[1].GetProperty("type").GetString() == "BETWEEN", "Rule enum must match Java JSON.");
Assert(document.RootElement.GetProperty("rules")[2].GetProperty("parameter").GetString() == "Open\u001fClosed", "IN_SET delimiter must match Java.");

var command = DataAiSparkSubmitBuilder.BuildQualityJob(
    "evaluation-job.json",
    runtime,
    new DataAiSparkSubmitOptions
    {
        Master = "local[2]",
        SparkArguments = ["--conf", "spark.sql.shuffle.partitions=2"]
    });

Assert(command.Arguments.Contains(DataAiRuntimePackage.CliMainClass), "CLI main class must be present.");
Assert(command.Arguments.Contains(runtime.CliJar), "CLI JAR must be the application resource.");
Assert(command.Arguments.Contains("--config"), "Configuration argument must be present.");

Console.WriteLine($"Validated {DataAiFunctionCatalog.All.Count} DataAI function catalog entries.");
Console.WriteLine(command.ToDisplayString());

static void Assert(bool condition, string message)
{
    if (!condition)
    {
        throw new InvalidOperationException(message);
    }
}
