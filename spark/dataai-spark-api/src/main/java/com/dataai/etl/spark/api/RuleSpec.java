package com.dataai.etl.spark.api;

import java.util.Objects;
import java.util.List;

public record RuleSpec(
        String id,
        RuleType type,
        String field,
        String parameter,
        Severity severity) {

    public RuleSpec {
        if (id == null || id.isBlank()) {
            throw new IllegalArgumentException("Rule id is required.");
        }
        Objects.requireNonNull(type, "Rule type is required.");
        if (field == null || field.isBlank()) {
            throw new IllegalArgumentException("Rule field is required.");
        }
        severity = severity == null ? Severity.ERROR : severity;
    }

    public static RuleSpec required(String id, String field) {
        return new RuleSpec(id, RuleType.REQUIRED, field, null, Severity.ERROR);
    }

    public static RuleSpec unique(String id, String field) {
        return new RuleSpec(id, RuleType.UNIQUE, field, null, Severity.ERROR);
    }

    public static RuleSpec minimum(String id, String field, double value) {
        return new RuleSpec(id, RuleType.MINIMUM, field, Double.toString(value), Severity.ERROR);
    }

    public static RuleSpec maximum(String id, String field, double value) {
        return new RuleSpec(id, RuleType.MAXIMUM, field, Double.toString(value), Severity.ERROR);
    }

    public static RuleSpec between(String id, String field, double minimum, double maximum) {
        return new RuleSpec(
                id, RuleType.BETWEEN, field,
                Double.toString(minimum) + "|" + Double.toString(maximum), Severity.ERROR);
    }

    public static RuleSpec inSet(String id, String field, List<String> acceptedValues) {
        if (acceptedValues == null || acceptedValues.isEmpty()) {
            throw new IllegalArgumentException("IN_SET requires at least one accepted value.");
        }
        return new RuleSpec(
                id, RuleType.IN_SET, field,
                String.join("\u001f", acceptedValues), Severity.ERROR);
    }

    public static RuleSpec dateFormat(String id, String field, String sparkDateFormat) {
        return new RuleSpec(id, RuleType.DATE_FORMAT, field, sparkDateFormat, Severity.ERROR);
    }

    public static RuleSpec length(String id, String field, int minimum, int maximum) {
        return new RuleSpec(
                id, RuleType.LENGTH, field,
                Integer.toString(minimum) + "|" + Integer.toString(maximum), Severity.ERROR);
    }

    public static RuleSpec equalsValue(String id, String field, String expectedValue) {
        return new RuleSpec(id, RuleType.EQUALS, field, expectedValue, Severity.ERROR);
    }

    public static RuleSpec regex(String id, String field, String expression) {
        return new RuleSpec(id, RuleType.REGEX, field, expression, Severity.ERROR);
    }
}
