package com.dataai.etl.spark.iris;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/** DataAI pipeline outputs prepared for explicit customer-controlled IRIS persistence. */
public record IrisPipelineOutputBundle(
        Dataset<Row> cleanRows,
        Dataset<Row> rejectedRows,
        Dataset<Row> qualityFindings,
        Dataset<Row> fieldProfiles,
        Dataset<Row> pipelineRuns) {
}
