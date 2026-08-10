package com.dataai.customer.examples;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.RuleSpec;
import com.dataai.etl.spark.core.DataAiPipeline;
import com.dataai.etl.spark.iris.IrisDataFrames;
import com.dataai.etl.spark.iris.IrisJdbcOptions;
import com.dataai.etl.spark.iris.IrisOutputNames;
import com.dataai.etl.spark.iris.IrisPipelineOutputBundle;
import com.dataai.etl.spark.iris.IrisPipelineOutputs;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;

/** Fictional customer example; obtain credentials from an approved secret manager. */
public final class IrisDataAiPipelineExample {
    private IrisDataAiPipelineExample() {
    }

    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
                .appName("DataAI ETL for InterSystems IRIS")
                .getOrCreate();
        IrisJdbcOptions iris = IrisJdbcOptions
                .builder(requiredEnvironment("IRIS_JDBC_URL"))
                .credentials(
                        requiredEnvironment("IRIS_USER"),
                        requiredEnvironment("IRIS_PASSWORD"))
                .fetchSize(5000)
                .batchSize(1000)
                .build();

        Dataset<Row> input = IrisDataFrames.readTablePartitioned(
                spark,
                iris,
                "Source.CustomerOrders",
                "OrderSequence",
                1,
                10_000_000,
                16);
        DataAiResult result = DataAiPipeline.fromDataset(input)
                .normalize()
                .recordKey("order_id")
                .profile()
                .validate(
                        RuleSpec.required("customer-required", "customer_id"),
                        RuleSpec.minimum("amount-nonnegative", "amount", 0))
                .execute();
        IrisPipelineOutputBundle output = IrisPipelineOutputs.from(result);

        append(output.pipelineRuns(), iris, IrisOutputNames.PIPELINE_RUNS);
        append(output.qualityFindings(), iris, IrisOutputNames.QUALITY_FINDINGS);
        append(output.fieldProfiles(), iris, IrisOutputNames.FIELD_PROFILES);
        append(output.rejectedRows(), iris, IrisOutputNames.REJECTED_ROWS);
        result.requireMinimumQualityScore(90.0);
        append(output.cleanRows(), iris, IrisOutputNames.CLEAN_ROWS);
    }

    private static void append(Dataset<Row> output, IrisJdbcOptions iris, String table) {
        IrisDataFrames.writer(output, iris)
                .option("dbtable", table)
                .mode(SaveMode.Append)
                .save();
    }

    private static String requiredEnvironment(String name) {
        String value = System.getenv(name);
        if (value == null || value.isBlank()) {
            throw new IllegalStateException("Required environment variable is missing: " + name);
        }
        return value;
    }
}
