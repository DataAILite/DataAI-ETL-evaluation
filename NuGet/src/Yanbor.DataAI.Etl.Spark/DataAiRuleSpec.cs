using System.Globalization;
using System.Text.Json.Serialization;

namespace Yanbor.DataAI.Etl.Spark;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum DataAiRuleType
{
    REQUIRED,
    UNIQUE,
    MINIMUM,
    MAXIMUM,
    BETWEEN,
    IN_SET,
    DATE_FORMAT,
    LENGTH,
    EQUALS,
    REGEX
}

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum DataAiSeverity
{
    INFO,
    WARNING,
    ERROR,
    CRITICAL
}

/// <summary>A JSON-compatible DataAI declarative quality rule.</summary>
public sealed record DataAiRuleSpec(
    string Id,
    DataAiRuleType Type,
    string Field,
    string? Parameter,
    DataAiSeverity Severity = DataAiSeverity.ERROR)
{
    public static DataAiRuleSpec Required(string id, string field) =>
        Create(id, DataAiRuleType.REQUIRED, field, null);

    public static DataAiRuleSpec Unique(string id, string field) =>
        Create(id, DataAiRuleType.UNIQUE, field, null);

    public static DataAiRuleSpec Minimum(string id, string field, double value) =>
        Create(id, DataAiRuleType.MINIMUM, field, value.ToString(CultureInfo.InvariantCulture));

    public static DataAiRuleSpec Maximum(string id, string field, double value) =>
        Create(id, DataAiRuleType.MAXIMUM, field, value.ToString(CultureInfo.InvariantCulture));

    public static DataAiRuleSpec Between(string id, string field, double minimum, double maximum) =>
        Create(
            id,
            DataAiRuleType.BETWEEN,
            field,
            minimum.ToString(CultureInfo.InvariantCulture) + "|" +
            maximum.ToString(CultureInfo.InvariantCulture));

    public static DataAiRuleSpec InSet(string id, string field, params string[] acceptedValues)
    {
        ArgumentNullException.ThrowIfNull(acceptedValues);
        if (acceptedValues.Length == 0)
        {
            throw new ArgumentException("IN_SET requires at least one accepted value.", nameof(acceptedValues));
        }

        return Create(id, DataAiRuleType.IN_SET, field, string.Join('\u001f', acceptedValues));
    }

    public static DataAiRuleSpec DateFormat(string id, string field, string sparkDateFormat) =>
        Create(id, DataAiRuleType.DATE_FORMAT, field, RequiredValue(sparkDateFormat, nameof(sparkDateFormat)));

    public static DataAiRuleSpec Length(string id, string field, int minimum, int maximum) =>
        minimum <= maximum
            ? Create(id, DataAiRuleType.LENGTH, field, $"{minimum}|{maximum}")
            : throw new ArgumentException("Minimum length cannot exceed maximum length.");

    public static DataAiRuleSpec EqualsValue(string id, string field, string expectedValue) =>
        Create(id, DataAiRuleType.EQUALS, field, expectedValue);

    public static DataAiRuleSpec Regex(string id, string field, string expression) =>
        Create(id, DataAiRuleType.REGEX, field, RequiredValue(expression, nameof(expression)));

    private static DataAiRuleSpec Create(string id, DataAiRuleType type, string field, string? parameter)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(id);
        ArgumentException.ThrowIfNullOrWhiteSpace(field);
        return new DataAiRuleSpec(id, type, field, parameter);
    }

    private static string RequiredValue(string value, string parameterName)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(value, parameterName);
        return value;
    }
}
