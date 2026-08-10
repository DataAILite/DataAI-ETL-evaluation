package com.dataai.etl.spark.quality;

import com.dataai.etl.spark.api.RuleSpec;
import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

import java.util.List;
import java.util.regex.Pattern;

import static org.apache.spark.sql.functions.broadcast;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.length;
import static org.apache.spark.sql.functions.not;
import static org.apache.spark.sql.functions.to_timestamp;
import static org.apache.spark.sql.functions.trim;

public final class QualityEvaluator {
    public static final String RECORD_KEY = "_dataai_record_key";

    private QualityEvaluator() {
    }

    public static Dataset<Row> evaluate(Dataset<Row> input, List<RuleSpec> rules) {
        Dataset<Row> findings = emptyFindings(input.sparkSession());
        for (RuleSpec rule : rules) {
            requireField(input, rule.field());
            Dataset<Row> violations = switch (rule.type()) {
                case REQUIRED -> input.filter(
                        col(rule.field()).isNull()
                                .or(trim(col(rule.field()).cast("string")).equalTo("")));
                case MINIMUM -> input.filter(
                        col(rule.field()).isNotNull()
                                .and(col(rule.field()).cast("double")
                                        .lt(Double.parseDouble(rule.parameter()))));
                case MAXIMUM -> input.filter(
                        col(rule.field()).isNotNull()
                                .and(col(rule.field()).cast("double")
                                        .gt(Double.parseDouble(rule.parameter()))));
                case BETWEEN -> {
                    double[] bounds = numericBounds(rule);
                    yield input.filter(
                            col(rule.field()).isNotNull()
                                    .and(col(rule.field()).cast("double").lt(bounds[0])
                                            .or(col(rule.field()).cast("double").gt(bounds[1]))));
                }
                case IN_SET -> {
                    Object[] accepted = rule.parameter().split(Pattern.quote("\u001f"), -1);
                    yield input.filter(
                            col(rule.field()).isNotNull()
                                    .and(not(col(rule.field()).cast("string").isin(accepted))));
                }
                case DATE_FORMAT -> input.filter(
                        col(rule.field()).isNotNull()
                                .and(to_timestamp(col(rule.field()).cast("string"), rule.parameter()).isNull()));
                case LENGTH -> {
                    int[] bounds = integerBounds(rule);
                    yield input.filter(
                            col(rule.field()).isNotNull()
                                    .and(length(col(rule.field()).cast("string")).lt(bounds[0])
                                            .or(length(col(rule.field()).cast("string")).gt(bounds[1]))));
                }
                case EQUALS -> input.filter(
                        col(rule.field()).isNotNull()
                                .and(col(rule.field()).cast("string").notEqual(rule.parameter())));
                case REGEX -> input.filter(
                        col(rule.field()).isNotNull()
                                .and(not(col(rule.field()).cast("string")
                                        .rlike(rule.parameter()))));
                case UNIQUE -> duplicateRows(input, rule.field());
            };

            Dataset<Row> ruleFindings = violations.select(
                    col(RECORD_KEY).cast("string").alias("record_key"),
                    lit(rule.id()).alias("rule_id"),
                    lit(rule.field()).alias("field_name"),
                    lit(rule.severity().name()).alias("severity"),
                    lit(rule.type().name()).alias("finding_code"),
                    lit(message(rule)).alias("message"),
                    col(rule.field()).cast("string").alias("original_value"),
                    lit(null).cast("string").alias("normalized_value"));
            findings = findings.unionByName(ruleFindings);
        }
        return findings;
    }

    private static Dataset<Row> duplicateRows(Dataset<Row> input, String field) {
        Dataset<Row> duplicateValues = input
                .filter(col(field).isNotNull())
                .groupBy(col(field))
                .count()
                .filter(col("count").gt(1))
                .select(col(field));
        return input.join(broadcast(duplicateValues), field, "inner");
    }

    private static void requireField(Dataset<Row> input, String field) {
        if (!List.of(input.columns()).contains(field)) {
            throw new IllegalArgumentException("Quality rule references missing field: " + field);
        }
    }

    private static String message(RuleSpec rule) {
        return "Field '" + rule.field() + "' failed DataAI rule '" + rule.id() + "'.";
    }

    private static double[] numericBounds(RuleSpec rule) {
        String[] values = requiredPair(rule);
        return new double[]{Double.parseDouble(values[0]), Double.parseDouble(values[1])};
    }

    private static int[] integerBounds(RuleSpec rule) {
        String[] values = requiredPair(rule);
        return new int[]{Integer.parseInt(values[0]), Integer.parseInt(values[1])};
    }

    private static String[] requiredPair(RuleSpec rule) {
        String[] values = rule.parameter() == null ? new String[0] : rule.parameter().split("\\|", -1);
        if (values.length != 2) {
            throw new IllegalArgumentException(rule.type() + " rule requires two pipe-separated parameters: " + rule.id());
        }
        return values;
    }

    private static Dataset<Row> emptyFindings(SparkSession spark) {
        StructType schema = new StructType()
                .add("record_key", DataTypes.StringType, false)
                .add("rule_id", DataTypes.StringType, false)
                .add("field_name", DataTypes.StringType, false)
                .add("severity", DataTypes.StringType, false)
                .add("finding_code", DataTypes.StringType, false)
                .add("message", DataTypes.StringType, false)
                .add("original_value", DataTypes.StringType, true)
                .add("normalized_value", DataTypes.StringType, true);
        return spark.createDataFrame(List.of(), schema);
    }
}
