package com.dataai.etl.spark.api;

public enum RuleType {
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
