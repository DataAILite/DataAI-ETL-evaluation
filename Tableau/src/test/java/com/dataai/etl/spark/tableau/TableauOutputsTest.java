package com.dataai.etl.spark.tableau;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.PipelineSummary;
import com.dataai.etl.spark.functions.MatrixBalanceResult;
import com.dataai.etl.spark.functions.MatrixFunctions;
import com.dataai.etl.spark.testkit.SparkTestSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class TableauOutputsTest {
    private static final StructType FINDINGS_SCHEMA = new StructType()
            .add("record_key", DataTypes.StringType, true)
            .add("rule_id", DataTypes.StringType, true)
            .add("field_name", DataTypes.StringType, true)
            .add("severity", DataTypes.StringType, true)
            .add("finding_code", DataTypes.StringType, true)
            .add("message", DataTypes.StringType, true)
            .add("original_value", DataTypes.StringType, true)
            .add("normalized_value", DataTypes.StringType, true);
    private static final StructType PROFILES_SCHEMA = new StructType()
            .add("field_name", DataTypes.StringType, true)
            .add("source_type", DataTypes.StringType, true)
            .add("record_count", DataTypes.LongType, true)
            .add("null_count", DataTypes.LongType, true)
            .add("distinct_count", DataTypes.LongType, true)
            .add("minimum_value", DataTypes.StringType, true)
            .add("maximum_value", DataTypes.StringType, true)
            .add("mean_value", DataTypes.DoubleType, true)
            .add("standard_deviation", DataTypes.DoubleType, true);
    private static final StructType ROW_SCHEMA = new StructType()
            .add("id", DataTypes.StringType, true);

    private static SparkSession spark;

    @BeforeAll
    static void startSpark() {
        spark = SparkTestSession.create();
    }

    @AfterAll
    static void stopSpark() {
        if (spark != null) {
            spark.stop();
        }
    }

    @Test
    void createsTableauRunAndDashboardMetrics() {
        Dataset<Row> clean = spark.createDataFrame(List.of(RowFactory.create("A")), ROW_SCHEMA);
        Dataset<Row> rejected = spark.createDataFrame(List.of(RowFactory.create("B")), ROW_SCHEMA);
        Dataset<Row> findings = spark.createDataFrame(List.of(
                finding("A", "WARNING"),
                finding("B", "ERROR"),
                finding("B", "ERROR"),
                finding("C", "CRITICAL"),
                finding("D", "INFO")), FINDINGS_SCHEMA);
        Dataset<Row> profiles = spark.createDataFrame(List.of(
                profile("id", 1L),
                profile("amount", 2L)), PROFILES_SCHEMA);
        DataAiResult result = result(clean, rejected, findings, profiles);

        TableauOutputBundle outputs = TableauOutputs.from(result);
        Row metrics = outputs.dashboardMetrics().head();

        assertEquals(1L, outputs.pipelineRuns().count());
        assertEquals("tableau-test-run", metrics.getAs("run_id"));
        assertEquals(10L, (Long) metrics.getAs("rows_read"));
        assertEquals(8L, (Long) metrics.getAs("rows_accepted"));
        assertEquals(2L, (Long) metrics.getAs("rows_rejected"));
        assertEquals(80.0, (Double) metrics.getAs("quality_score"));
        assertEquals(1L, (Long) metrics.getAs("critical_findings"));
        assertEquals(2L, (Long) metrics.getAs("error_findings"));
        assertEquals(1L, (Long) metrics.getAs("warning_findings"));
        assertEquals(1L, (Long) metrics.getAs("info_findings"));
        assertEquals(2L, (Long) metrics.getAs("fields_profiled"));
        assertEquals(3L, (Long) metrics.getAs("total_null_values"));
    }

    @Test
    void reportsZerosWhenFindingsAndProfilesAreEmpty() {
        Dataset<Row> rows = spark.createDataFrame(List.of(RowFactory.create("A")), ROW_SCHEMA);
        Dataset<Row> findings = spark.createDataFrame(Collections.emptyList(), FINDINGS_SCHEMA);
        Dataset<Row> profiles = spark.createDataFrame(Collections.emptyList(), PROFILES_SCHEMA);

        Row metrics = TableauOutputs.from(result(rows, rows, findings, profiles))
                .dashboardMetrics()
                .head();

        assertEquals(0L, (Long) metrics.getAs("critical_findings"));
        assertEquals(0L, (Long) metrics.getAs("error_findings"));
        assertEquals(0L, (Long) metrics.getAs("warning_findings"));
        assertEquals(0L, (Long) metrics.getAs("info_findings"));
        assertEquals(0L, (Long) metrics.getAs("fields_profiled"));
        assertEquals(0L, (Long) metrics.getAs("total_null_values"));
    }

    @Test
    void exposesMatrixBalancingForTableau() {
        StructType cellSchema = new StructType()
                .add("region", DataTypes.StringType, false)
                .add("category", DataTypes.StringType, false)
                .add("value", DataTypes.DoubleType, false);
        Dataset<Row> cells = spark.createDataFrame(List.of(
                RowFactory.create("North", "A", 10.0),
                RowFactory.create("North", "B", 20.0),
                RowFactory.create("South", "A", 30.0),
                RowFactory.create("South", "B", 40.0)), cellSchema);
        StructType rowTargetSchema = new StructType()
                .add("region", DataTypes.StringType, false)
                .add("target", DataTypes.DoubleType, false);
        Dataset<Row> rowTargets = spark.createDataFrame(List.of(
                RowFactory.create("North", 40.0),
                RowFactory.create("South", 60.0)), rowTargetSchema);
        StructType columnTargetSchema = new StructType()
                .add("category", DataTypes.StringType, false)
                .add("target", DataTypes.DoubleType, false);
        Dataset<Row> columnTargets = spark.createDataFrame(List.of(
                RowFactory.create("A", 50.0),
                RowFactory.create("B", 50.0)), columnTargetSchema);

        MatrixBalanceResult balance = MatrixFunctions.balance(
                cells,
                "region",
                "category",
                "value",
                rowTargets,
                columnTargets,
                "target",
                20,
                0.001);
        Dataset<Row> tableau = TableauFunctionOutputs.matrixBalance(
                balance,
                "matrix-run",
                Instant.parse("2026-08-06T12:00:00Z"),
                "0.1.0-SNAPSHOT");
        Row first = tableau.head();

        assertEquals(4L, tableau.count());
        assertEquals("matrix_balance", first.getAs(TableauFunctionOutputs.RESULT_NAME));
        assertEquals("matrix-run", first.getAs(TableauFunctionOutputs.RUN_ID));
        assertEquals(balance.iterations(), (Integer) first.getAs("balance_iterations"));
        assertEquals(balance.converged(), (Boolean) first.getAs("balance_converged"));
    }

    private static Row finding(String recordKey, String severity) {
        return RowFactory.create(
                recordKey, "rule", "field", severity, "CODE", "message", "old", "new");
    }

    private static Row profile(String fieldName, long nullCount) {
        return RowFactory.create(
                fieldName, "string", 10L, nullCount, 8L, "A", "Z", null, null);
    }

    private static DataAiResult result(
            Dataset<Row> clean,
            Dataset<Row> rejected,
            Dataset<Row> findings,
            Dataset<Row> profiles) {
        PipelineSummary summary = new PipelineSummary(
                "tableau-test-run",
                Instant.parse("2026-08-06T10:00:00Z"),
                Instant.parse("2026-08-06T10:01:00Z"),
                "SUCCEEDED",
                10L,
                8L,
                2L,
                80.0,
                "0.1.0-SNAPSHOT");
        return new DataAiResult(clean, rejected, findings, profiles, summary);
    }
}
