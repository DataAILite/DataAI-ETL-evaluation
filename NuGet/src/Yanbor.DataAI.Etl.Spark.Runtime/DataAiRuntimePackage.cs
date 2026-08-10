namespace Yanbor.DataAI.Etl.Spark.Runtime;

/// <summary>Describes the DataAI Spark artifacts carried by this evaluation package.</summary>
public static class DataAiRuntimePackage
{
    public const string DataAiVersion = "0.1.0-SNAPSHOT";
    public const string JavaVersion = "17";
    public const string SparkVersion = "3.5.0";
    public const string ScalaBinaryVersion = "2.12";
    public const string CliMainClass = "com.dataai.etl.spark.cli.DataAiJob";

    public static IReadOnlyList<string> LibraryJarFileNames { get; } =
    [
        "dataai-spark-api-0.1.0-SNAPSHOT.jar",
        "dataai-spark-quality-0.1.0-SNAPSHOT.jar",
        "dataai-spark-core-0.1.0-SNAPSHOT.jar",
        "dataai-spark-functions-0.1.0-SNAPSHOT.jar"
    ];

    public const string CliJarFileName = "dataai-spark-cli-0.1.0-SNAPSHOT.jar";
}
