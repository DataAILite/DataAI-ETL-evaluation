package com.dataai.etl.spark.iris;

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

/** Converts standard pipeline results into IRIS history-ready DataFrames. */
public final class IrisPipelineOutputs {
    private static final StructType RUN_SCHEMA = new StructType()
            .add("run_id", DataTypes.StringType, false)
            .add("started_at", DataTypes.TimestampType, false)
            .add("completed_at", DataTypes.TimestampType, false)
            .add("status", DataTypes.StringType, false)
            .add("rows_read", DataTypes.LongType, false)
            .add("rows_accepted", DataTypes.LongType, false)
            .add("rows_rejected", DataTypes.LongType, false)
            .add("quality_score", DataTypes.DoubleType, false)
            .add("library_version", DataTypes.StringType, false)
            .add("platform", DataTypes.StringType, false);

    private IrisPipelineOutputs() {
    }

    /** Performs no writes and no unbounded driver collection. */
    public static IrisPipelineOutputBundle from(DataAiResult result) {
        Objects.requireNonNull(result, "result");
        PipelineSummary summary = Objects.requireNonNull(result.summary(), "result.summary");
        Dataset<Row> clean = IrisFunctionOutputs.withRunMetadata(
                Objects.requireNonNull(result.cleanRows(), "result.cleanRows"),
                "clean_rows",
                summary);
        Dataset<Row> rejected = IrisFunctionOutputs.withRunMetadata(
                Objects.requireNonNull(result.rejectedRows(), "result.rejectedRows"),
                "rejected_rows",
                summary);
        Dataset<Row> findings = IrisFunctionOutputs.withRunMetadata(
                Objects.requireNonNull(result.findings(), "result.findings"),
                "quality_findings",
                summary);
        Dataset<Row> profiles = IrisFunctionOutputs.withRunMetadata(
                Objects.requireNonNull(result.fieldProfiles(), "result.fieldProfiles"),
                "field_profiles",
                summary);
        return new IrisPipelineOutputBundle(
                clean,
                rejected,
                findings,
                profiles,
                pipelineRuns(clean.sparkSession(), summary));
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
                Objects.requireNonNull(summary.libraryVersion(), "summary.libraryVersion"),
                "INTERSYSTEMS_IRIS");
        return spark.createDataFrame(List.of(row), RUN_SCHEMA);
    }
}
