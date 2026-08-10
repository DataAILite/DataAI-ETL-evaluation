package com.dataai.etl.spark.cli;

import com.dataai.etl.spark.api.RuleSpec;

import java.util.List;

public record DataAiJobConfiguration(
        String sourceTable,
        String cleanTable,
        String rejectedTable,
        String profileTable,
        String findingsTable,
        boolean normalize,
        List<String> recordKeyColumns,
        List<RuleSpec> rules,
        Double minimumQualityScore) {

    public DataAiJobConfiguration {
        recordKeyColumns = recordKeyColumns == null ? List.of() : List.copyOf(recordKeyColumns);
        rules = rules == null ? List.of() : List.copyOf(rules);
    }
}
