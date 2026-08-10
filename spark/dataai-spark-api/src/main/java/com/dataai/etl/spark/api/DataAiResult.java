package com.dataai.etl.spark.api;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

public record DataAiResult(
        Dataset<Row> cleanRows,
        Dataset<Row> rejectedRows,
        Dataset<Row> findings,
        Dataset<Row> fieldProfiles,
        PipelineSummary summary) {

    public void requireMinimumQualityScore(double minimumScore) {
        if (summary.qualityScore() < minimumScore) {
            throw new IllegalStateException(
                    "DataAI quality gate failed: score " + summary.qualityScore()
                            + " is below " + minimumScore + ".");
        }
    }
}

