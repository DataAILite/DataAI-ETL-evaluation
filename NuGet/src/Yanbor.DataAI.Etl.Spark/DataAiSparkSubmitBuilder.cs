using Yanbor.DataAI.Etl.Spark.Runtime;

namespace Yanbor.DataAI.Etl.Spark;

/// <summary>Creates commands without starting processes or writing customer data.</summary>
public static class DataAiSparkSubmitBuilder
{
    public static DataAiSparkSubmitCommand BuildQualityJob(
        string configurationPath,
        DataAiSparkRuntimeLayout? runtime = null,
        DataAiSparkSubmitOptions? options = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(configurationPath);
        runtime ??= DataAiSparkRuntimeLayout.Discover();
        options ??= new DataAiSparkSubmitOptions();

        var arguments = BaseArguments(options);
        arguments.Add("--class");
        arguments.Add(DataAiRuntimePackage.CliMainClass);
        arguments.Add(runtime.CliJar);
        arguments.Add("--config");
        arguments.Add(Path.GetFullPath(configurationPath));
        arguments.AddRange(options.ApplicationArguments);
        return new DataAiSparkSubmitCommand(options.SparkSubmitExecutable, arguments);
    }

    public static DataAiSparkSubmitCommand BuildLibraryApplication(
        string applicationResource,
        DataAiSparkRuntimeLayout? runtime = null,
        DataAiSparkSubmitOptions? options = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(applicationResource);
        runtime ??= DataAiSparkRuntimeLayout.Discover();
        options ??= new DataAiSparkSubmitOptions();

        var arguments = BaseArguments(options);
        arguments.Add("--jars");
        arguments.Add(runtime.JarsArgument);
        arguments.Add(applicationResource);
        arguments.AddRange(options.ApplicationArguments);
        return new DataAiSparkSubmitCommand(options.SparkSubmitExecutable, arguments);
    }

    private static List<string> BaseArguments(DataAiSparkSubmitOptions options)
    {
        var arguments = new List<string>();
        if (!string.IsNullOrWhiteSpace(options.Master))
        {
            arguments.Add("--master");
            arguments.Add(options.Master);
        }

        if (!string.IsNullOrWhiteSpace(options.DeployMode))
        {
            arguments.Add("--deploy-mode");
            arguments.Add(options.DeployMode);
        }

        arguments.AddRange(options.SparkArguments);
        return arguments;
    }
}
