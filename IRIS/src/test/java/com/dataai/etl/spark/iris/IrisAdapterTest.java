package com.dataai.etl.spark.iris;

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
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class IrisAdapterTest {
    private static final StructType SIMPLE_SCHEMA = new StructType()
            .add("id", DataTypes.StringType, true);
    private static final StructType FINDINGS_SCHEMA = new StructType()
            .add("record_key", DataTypes.StringType, true)
            .add("severity", DataTypes.StringType, true);
    private static final StructType PROFILES_SCHEMA = new StructType()
            .add("field_name", DataTypes.StringType, true)
            .add("null_count", DataTypes.LongType, true);

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
    void buildsSafeIrisConnectionOptions() {
        IrisJdbcOptions options = IrisJdbcOptions
                .forServer("iris.internal", 1972, "DATAAI")
                .credentials("etl_user", "top-secret")
                .fetchSize(5000)
                .batchSize(1000)
                .property("SSL", "1")
                .build();

        assertEquals("jdbc:IRIS://iris.internal:1972/DATAAI", options.url());
        assertEquals(IrisJdbcOptions.DEFAULT_DRIVER, options.driver());
        assertTrue(options.toString().contains("credentialsConfigured=true"));
        assertFalse(options.toString().contains("top-secret"));
        assertFalse(options.toString().contains("etl_user"));
        assertThrows(
                IllegalArgumentException.class,
                () -> IrisJdbcOptions.builder("jdbc:IRIS://host:1972/USER")
                        .property("password", "not-allowed"));
    }

    @Test
    void preparesPipelineOutputsForIrisHistory() {
        Dataset<Row> clean = spark.createDataFrame(List.of(RowFactory.create("A")), SIMPLE_SCHEMA);
        Dataset<Row> rejected = spark.createDataFrame(List.of(RowFactory.create("B")), SIMPLE_SCHEMA);
        Dataset<Row> findings = spark.createDataFrame(
                List.of(RowFactory.create("B", "ERROR")),
                FINDINGS_SCHEMA);
        Dataset<Row> profiles = spark.createDataFrame(
                List.of(RowFactory.create("id", 1L)),
                PROFILES_SCHEMA);
        PipelineSummary summary = new PipelineSummary(
                "iris-run",
                Instant.parse("2026-08-06T13:00:00Z"),
                Instant.parse("2026-08-06T13:01:00Z"),
                "SUCCEEDED",
                2,
                1,
                1,
                50.0,
                "0.1.0-SNAPSHOT");

        IrisPipelineOutputBundle outputs = IrisPipelineOutputs.from(
                new DataAiResult(clean, rejected, findings, profiles, summary));
        Row finding = outputs.qualityFindings().head();
        Row run = outputs.pipelineRuns().head();

        assertEquals("iris-run", finding.getAs(IrisFunctionOutputs.RUN_ID));
        assertEquals("INTERSYSTEMS_IRIS", finding.getAs(IrisFunctionOutputs.PLATFORM));
        assertEquals("iris-run", run.getAs("run_id"));
        assertEquals(1L, (Long) run.getAs("rows_rejected"));
    }

    @Test
    void exposesMatrixBalancingForIris() {
        StructType cellsSchema = new StructType()
                .add("region", DataTypes.StringType, false)
                .add("category", DataTypes.StringType, false)
                .add("value", DataTypes.DoubleType, false);
        Dataset<Row> cells = spark.createDataFrame(List.of(
                RowFactory.create("North", "A", 10.0),
                RowFactory.create("North", "B", 20.0),
                RowFactory.create("South", "A", 30.0),
                RowFactory.create("South", "B", 40.0)), cellsSchema);
        Dataset<Row> rowTargets = spark.createDataFrame(List.of(
                RowFactory.create("North", 40.0),
                RowFactory.create("South", 60.0)), new StructType()
                .add("region", DataTypes.StringType, false)
                .add("target", DataTypes.DoubleType, false));
        Dataset<Row> columnTargets = spark.createDataFrame(List.of(
                RowFactory.create("A", 50.0),
                RowFactory.create("B", 50.0)), new StructType()
                .add("category", DataTypes.StringType, false)
                .add("target", DataTypes.DoubleType, false));

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
        Dataset<Row> iris = IrisFunctionOutputs.matrixBalance(
                balance,
                "matrix-run",
                Instant.parse("2026-08-06T13:02:00Z"),
                "0.1.0-SNAPSHOT");

        assertEquals(4L, iris.count());
        assertEquals("matrix_balance", iris.head().getAs(IrisFunctionOutputs.RESULT_NAME));
        assertTrue(iris.columns().length > balance.balancedCells().columns().length);
    }

    @Test
    void rejectsInvalidPartitionSettingsWithoutConnecting() {
        IrisJdbcOptions options = IrisJdbcOptions.builder("jdbc:IRIS://host:1972/USER").build();
        assertThrows(
                IllegalArgumentException.class,
                () -> IrisDataFrames.readTablePartitioned(
                        spark, options, "DataAI.Source", "invalid-name", 1, 10, 2));
        assertThrows(
                IllegalArgumentException.class,
                () -> IrisDataFrames.readTablePartitioned(
                        spark, options, "DataAI.Source", "RecordId", 10, 1, 2));
    }
}
