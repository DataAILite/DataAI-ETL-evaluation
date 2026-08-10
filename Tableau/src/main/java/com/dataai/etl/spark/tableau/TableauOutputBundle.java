package com.dataai.etl.spark.tableau;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

/**
 * DataFrames intended for customer-controlled persistence and Tableau access.
 * No member is written, cached, collected, or transmitted by this adapter.
 */
public record TableauOutputBundle(
        Dataset<Row> cleanRows,
        Dataset<Row> rejectedRows,
        Dataset<Row> qualityFindings,
        Dataset<Row> fieldProfiles,
        Dataset<Row> pipelineRuns,
        Dataset<Row> dashboardMetrics) {
}
