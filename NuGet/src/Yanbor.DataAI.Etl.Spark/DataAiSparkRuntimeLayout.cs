using Yanbor.DataAI.Etl.Spark.Runtime;

namespace Yanbor.DataAI.Etl.Spark;

/// <summary>Resolved locations of the DataAI Spark library and CLI artifacts.</summary>
public sealed record DataAiSparkRuntimeLayout(
    string RootDirectory,
    IReadOnlyList<string> LibraryJars,
    string CliJar)
{
    public static DataAiSparkRuntimeLayout Discover(string? baseDirectory = null)
    {
        string root = Path.GetFullPath(baseDirectory ?? AppContext.BaseDirectory);
        string jarsDirectory = Path.Combine(root, "dataai", "jars");
        string cliDirectory = Path.Combine(root, "dataai", "cli");
        var libraryJars = DataAiRuntimePackage.LibraryJarFileNames
            .Select(fileName => Path.Combine(jarsDirectory, fileName))
            .ToArray();
        string cliJar = Path.Combine(cliDirectory, DataAiRuntimePackage.CliJarFileName);

        var missing = libraryJars.Append(cliJar).Where(path => !File.Exists(path)).ToArray();
        if (missing.Length > 0)
        {
            throw new FileNotFoundException(
                "DataAI Spark runtime artifacts were not found. Build or publish the consuming " +
                "project so the runtime package can copy its assets. Missing: " +
                string.Join(", ", missing));
        }

        return new DataAiSparkRuntimeLayout(root, libraryJars, cliJar);
    }

    public string JarsArgument => string.Join(",", LibraryJars);
}
