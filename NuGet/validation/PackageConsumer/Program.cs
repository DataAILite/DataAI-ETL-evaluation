using Yanbor.DataAI.Etl.Spark;

DataAiSparkRuntimeLayout runtime = DataAiSparkRuntimeLayout.Discover();
if (runtime.LibraryJars.Count != 4 || runtime.LibraryJars.Any(path => !File.Exists(path)))
{
    throw new InvalidOperationException("The runtime package did not copy all four library JARs.");
}

if (!File.Exists(runtime.CliJar))
{
    throw new InvalidOperationException("The runtime package did not copy the shaded CLI JAR.");
}

if (!DataAiFunctionCatalog.All.Any(item => item.Capability == "Matrix balancing"))
{
    throw new InvalidOperationException("Matrix balancing is missing from the function catalog.");
}

var command = DataAiSparkSubmitBuilder.BuildQualityJob(
    "evaluation-job.json",
    runtime,
    new DataAiSparkSubmitOptions { Master = "local[2]" });

Console.WriteLine($"Package consumer found {runtime.LibraryJars.Count} library JARs and the CLI JAR.");
Console.WriteLine(command.ToDisplayString());
