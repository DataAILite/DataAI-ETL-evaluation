package com.dataai.etl.spark.tableau;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.PipelineSummary;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

import java.sql.Timestamp;
import java.util.List;
import java.util.Objects;

import static org.apache.spark.sql.functions.coalesce;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.sum;
import static org.apache.spark.sql.functions.when;

/** Converts a DataAI pipeline result to Tableau-friendly Spark DataFrames. */
public final class TableauOutputs {
    private static final StructType PIPELINE_RUN_SCHEMA = new StructType()
            .add("run_id", DataTypes.StringType, false)
            .add("started_at", DataTypes.TimestampType, false)
            .add("completed_at", DataTypes.TimestampType, false)
            .add("status", DataTypes.StringType, false)
            .add("rows_read", DataTypes.LongType, false)
            .add("rows_accepted", DataTypes.LongType, false)
            .add("rows_rejected", DataTypes.LongType, false)
            .add("quality_score", DataTypes.DoubleType, false)
            .add("library_version", DataTypes.StringType, false);

    private TableauOutputs() {
    }

    /**
     * Builds lazy Tableau datasets and a one-row pipeline-run dataset.
     * The method performs no writes and no unbounded driver collections.
     */
    public static TableauOutputBundle from(DataAiResult result) {
        Objects.requireNonNull(result, "result");
        Objects.requireNonNull(result.cleanRows(), "result.cleanRows");
        Objects.requireNonNull(result.rejectedRows(), "result.rejectedRows");
        Objects.requireNonNull(result.findings(), "result.findings");
        Objects.requireNonNull(result.fieldProfiles(), "result.fieldProfiles");
        PipelineSummary summary = Objects.requireNonNull(result.summary(), "result.summary");

        SparkSession spark = result.cleanRows().sparkSession();
        Dataset<Row> pipelineRuns = pipelineRuns(spark, summary);

        Dataset<Row> severityCounts = result.findings().agg(
                coalesce(sum(when(col("severity").equalTo("CRITICAL"), 1L).otherwise(0L)), lit(0L))
                        .cast(DataTypes.LongType).alias("critical_findings"),
                coalesce(sum(when(col("severity").equalTo("ERROR"), 1L).otherwise(0L)), lit(0L))
                        .cast(DataTypes.LongType).alias("error_findings"),
                coalesce(sum(when(col("severity").equalTo("WARNING"), 1L).otherwise(0L)), lit(0L))
                        .cast(DataTypes.LongType).alias("warning_findings"),
                coalesce(sum(when(col("severity").equalTo("INFO"), 1L).otherwise(0L)), lit(0L))
                        .cast(DataTypes.LongType).alias("info_findings"));

        Dataset<Row> profileCounts = result.fieldProfiles().agg(
                count(lit(1)).cast(DataTypes.LongType).alias("fields_profiled"),
                coalesce(sum(col("null_count")), lit(0L))
                        .cast(DataTypes.LongType).alias("total_null_values"));

        Dataset<Row> dashboardMetrics = pipelineRuns
                .crossJoin(severityCounts)
                .crossJoin(profileCounts)
                .select(
                        col("run_id"),
                        col("completed_at"),
                        col("status"),
                        col("rows_read"),
                        col("rows_accepted"),
                        col("rows_rejected"),
                        col("quality_score"),
                        col("critical_findings"),
                        col("error_findings"),
                        col("warning_findings"),
                        col("info_findings"),
                        col("fields_profiled"),
                        col("total_null_values"));

        return new TableauOutputBundle(
                result.cleanRows(),
                result.rejectedRows(),
                result.findings(),
                result.fieldProfiles(),
                pipelineRuns,
                dashboardMetrics);
    }

    private static Dataset<Row> pipelineRuns(SparkSession spark, PipelineSummary summary) {
        Row row = RowFactory.create(
                Objects.requireNonNull(summary.runId(), "summary.runId"),
                Timestamp.from(Objects.requireNonNull(summary.startedAt(), "summary.startedAt")),
                Timestamp.from(Objects.requireNonNull(summary.completedAt(), "summary.completedAt")),
                Objects.requireNonNull(summary.status(), "summary.status"),
                summary.rowsRead(),
                summary.rowsAccepted(),
                summary.rowsRejected(),
                summary.qualityScore(),
                Objects.requireNonNull(summary.libraryVersion(), "summary.libraryVersion"));
        return spark.createDataFrame(List.of(row), PIPELINE_RUN_SCHEMA);
    }
}
