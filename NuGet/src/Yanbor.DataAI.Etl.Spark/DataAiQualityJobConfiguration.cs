using System.Text.Json;
using System.Text.Json.Serialization;

namespace Yanbor.DataAI.Etl.Spark;

/// <summary>Configuration accepted by the embedded DataAI Spark CLI.</summary>
public sealed class DataAiQualityJobConfiguration
{
    public required string SourceTable { get; init; }
    public string? CleanTable { get; init; }
    public string? RejectedTable { get; init; }
    public string? ProfileTable { get; init; }
    public string? FindingsTable { get; init; }
    public bool Normalize { get; init; } = true;
    public IReadOnlyList<string> RecordKeyColumns { get; init; } = Array.Empty<string>();
    public IReadOnlyList<DataAiRuleSpec> Rules { get; init; } = Array.Empty<DataAiRuleSpec>();
    public double? MinimumQualityScore { get; init; }

    public string ToJson(bool indented = true)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(SourceTable);
        return JsonSerializer.Serialize(this, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = indented,
            DefaultIgnoreCondition = JsonIgnoreCondition.Never,
            Converters = { new JsonStringEnumConverter() }
        });
    }

    public void WriteJson(string path, bool indented = true)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        File.WriteAllText(path, ToJson(indented));
    }
}
