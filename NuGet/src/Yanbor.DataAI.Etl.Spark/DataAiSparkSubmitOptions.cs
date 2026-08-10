namespace Yanbor.DataAI.Etl.Spark;

/// <summary>Customer-controlled spark-submit settings.</summary>
public sealed class DataAiSparkSubmitOptions
{
    public string SparkSubmitExecutable { get; init; } = "spark-submit";
    public string? Master { get; init; }
    public string? DeployMode { get; init; }
    public IReadOnlyList<string> SparkArguments { get; init; } = Array.Empty<string>();
    public IReadOnlyList<string> ApplicationArguments { get; init; } = Array.Empty<string>();
}
