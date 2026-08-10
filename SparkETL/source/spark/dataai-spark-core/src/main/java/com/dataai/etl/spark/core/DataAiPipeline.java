package com.dataai.etl.spark.core;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.PipelineSummary;
import com.dataai.etl.spark.api.RuleSpec;
import com.dataai.etl.spark.quality.QualityEvaluator;
import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

import static org.apache.spark.sql.functions.coalesce;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.concat_ws;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.sha2;
import static org.apache.spark.sql.functions.struct;
import static org.apache.spark.sql.functions.to_json;

public final class DataAiPipeline {
    public static final String LIBRARY_VERSION = "0.1.0-SNAPSHOT";

    private final Dataset<Row> source;
    private final List<RuleSpec> rules = new ArrayList<>();
    private final List<String> recordKeyFields = new ArrayList<>();
    private boolean normalize;
    private boolean profile;

    private DataAiPipeline(Dataset<Row> source) {
        this.source = source;
    }

    public static DataAiPipeline fromTable(SparkSession spark, String table) {
        return new DataAiPipeline(spark.table(table));
    }

    public static DataAiPipeline fromDataset(Dataset<Row> source) {
        return new DataAiPipeline(source);
    }

    public DataAiPipeline normalize() {
        this.normalize = true;
        return this;
    }

    public DataAiPipeline profile() {
        this.profile = true;
        return this;
    }

    public DataAiPipeline recordKey(String... fields) {
        this.recordKeyFields.clear();
        this.recordKeyFields.addAll(Arrays.asList(fields));
        return this;
    }

    public DataAiPipeline validate(RuleSpec... rules) {
        this.rules.addAll(Arrays.asList(rules));
        return this;
    }

    public DataAiPipeline validate(List<RuleSpec> rules) {
        this.rules.addAll(rules);
        return this;
    }

    public DataAiResult execute() {
        Instant startedAt = Instant.now();
        String runId = UUID.randomUUID().toString();
        Dataset<Row> working = normalize ? Normalizer.normalize(source) : source;
        working = addRecordKey(working);

        Dataset<Row> findings = QualityEvaluator.evaluate(working, rules);
        Dataset<Row> rejectedKeys = findings.select("record_key").distinct();
        Dataset<Row> rejected = working.join(
                rejectedKeys,
                working.col(QualityEvaluator.RECORD_KEY)
                        .equalTo(rejectedKeys.col("record_key")),
                "left_semi");
        Dataset<Row> clean = working.join(
                rejectedKeys,
                working.col(QualityEvaluator.RECORD_KEY)
                        .equalTo(rejectedKeys.col("record_key")),
                "left_anti");
        Dataset<Row> profiles = profile ? FieldProfiler.profile(working) : FieldProfiler.profile(working.limit(0));

        long rowsRead = working.count();
        long rowsRejected = rejected.count();
        long rowsAccepted = rowsRead - rowsRejected;
        double qualityScore = rowsRead == 0
                ? 100.0
                : Math.round((rowsAccepted * 10000.0 / rowsRead)) / 100.0;
        PipelineSummary summary = new PipelineSummary(
                runId,
                startedAt,
                Instant.now(),
                rowsRejected == 0 ? "PASSED" : "COMPLETED_WITH_FINDINGS",
                rowsRead,
                rowsAccepted,
                rowsRejected,
                qualityScore,
                LIBRARY_VERSION);
        return new DataAiResult(clean, rejected, findings, profiles, summary);
    }

    private Dataset<Row> addRecordKey(Dataset<Row> input) {
        Column keyExpression;
        if (recordKeyFields.isEmpty()) {
            Column[] fields = Arrays.stream(input.columns()).map(org.apache.spark.sql.functions::col).toArray(Column[]::new);
            keyExpression = sha2(to_json(struct(fields)), 256);
        } else {
            Column[] fields = recordKeyFields.stream()
                    .map(field -> {
                        requireField(input, field);
                        return coalesce(col(field).cast("string"), lit("<null>"));
                    })
                    .toArray(Column[]::new);
            keyExpression = sha2(concat_ws("||", fields), 256);
        }
        return input.withColumn(QualityEvaluator.RECORD_KEY, keyExpression);
    }

    private static void requireField(Dataset<Row> input, String field) {
        if (!List.of(input.columns()).contains(field)) {
            throw new IllegalArgumentException("Record key references missing field: " + field);
        }
    }
}
