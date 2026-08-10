package com.dataai.etl.spark.cli;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.core.DataAiPipeline;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;

import java.nio.file.Files;
import java.nio.file.Path;

public final class DataAiJob {
    private DataAiJob() {
    }

    public static void main(String[] args) throws Exception {
        String configPath = requiredArgument(args, "--config");
        DataAiJobConfiguration configuration = new ObjectMapper().readValue(
                Files.readString(Path.of(configPath)),
                DataAiJobConfiguration.class);
        SparkSession spark = SparkSession.builder()
                .appName("DataAI ETL - " + configuration.sourceTable())
                .getOrCreate();

        DataAiPipeline pipeline = DataAiPipeline.fromTable(spark, configuration.sourceTable())
                .recordKey(configuration.recordKeyColumns().toArray(String[]::new))
                .profile()
                .validate(configuration.rules());
        if (configuration.normalize()) {
            pipeline.normalize();
        }

        DataAiResult result = pipeline.execute();
        writeTable(result.rejectedRows(), configuration.rejectedTable());
        writeTable(result.fieldProfiles(), configuration.profileTable());
        writeTable(result.findings(), configuration.findingsTable());

        if (configuration.minimumQualityScore() != null) {
            result.requireMinimumQualityScore(configuration.minimumQualityScore());
        }
        writeTable(result.cleanRows(), configuration.cleanTable());

        System.out.printf(
                "DataAI run %s finished with quality score %.2f and %d rejected rows.%n",
                result.summary().runId(),
                result.summary().qualityScore(),
                result.summary().rowsRejected());
    }

    private static void writeTable(org.apache.spark.sql.Dataset<org.apache.spark.sql.Row> rows, String table) {
        if (table == null || table.isBlank()) {
            return;
        }
        rows.write()
                .format("delta")
                .mode(SaveMode.Overwrite)
                .option("overwriteSchema", "true")
                .saveAsTable(table);
    }

    private static String requiredArgument(String[] args, String name) {
        for (int i = 0; i < args.length - 1; i++) {
            if (name.equals(args[i])) {
                return args[i + 1];
            }
        }
        throw new IllegalArgumentException("Required argument is missing: " + name);
    }
}

