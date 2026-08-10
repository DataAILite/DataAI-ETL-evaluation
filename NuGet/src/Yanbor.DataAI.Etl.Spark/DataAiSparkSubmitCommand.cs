namespace Yanbor.DataAI.Etl.Spark;

/// <summary>A process-safe spark-submit command description.</summary>
public sealed record DataAiSparkSubmitCommand(string FileName, IReadOnlyList<string> Arguments)
{
    public string ToDisplayString() => string.Join(
        " ",
        new[] { Quote(FileName) }.Concat(Arguments.Select(Quote)));

    private static string Quote(string value) =>
        value.Any(char.IsWhiteSpace) || value.Contains('"')
            ? '"' + value.Replace("\"", "\\\"") + '"'
            : value;
}
