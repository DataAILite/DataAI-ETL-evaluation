package com.dataai.etl.spark.functions;

import com.dataai.etl.spark.core.FieldProfiler;
import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.types.DataType;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import static org.apache.spark.sql.functions.abs;
import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.coalesce;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.concat;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.countDistinct;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.lower;
import static org.apache.spark.sql.functions.regexp_replace;
import static org.apache.spark.sql.functions.stddev_pop;
import static org.apache.spark.sql.functions.sum;
import static org.apache.spark.sql.functions.to_timestamp;
import static org.apache.spark.sql.functions.trim;
import static org.apache.spark.sql.functions.when;

public final class DataQualityFunctions {
    private DataQualityFunctions() {
    }

    public static Dataset<Row> automaticChecks(Dataset<Row> input, double standardDeviationThreshold) {
        if (standardDeviationThreshold <= 0) {
            throw new IllegalArgumentException("Standard-deviation threshold must be positive.");
        }
        return missingValueSummary(input)
                .unionByName(duplicateRecordSummary(input))
                .unionByName(invalidDateSummary(input))
                .unionByName(numericOutlierSummary(input, standardDeviationThreshold))
                .unionByName(inconsistentCategorySummary(input))
                .unionByName(suspiciousTextSummary(input))
                .orderBy(col("severity").desc(), col("affected_records").desc(), col("field_name"));
    }

    public static Dataset<Row> missingValueSummary(Dataset<Row> input) {
        return FieldProfiler.profile(input)
                .filter(col("null_count").gt(0))
                .select(
                        lit("MISSING_VALUES").alias("issue_type"),
                        col("field_name"),
                        col("null_count").cast("long").alias("affected_records"),
                        lit("ERROR").alias("severity"),
                        concat(lit("Field contains missing values: "), col("field_name")).alias("description"));
    }

    public static Dataset<Row> duplicateRecordSummary(Dataset<Row> input) {
        Column[] fields = java.util.Arrays.stream(input.columns())
                .map(org.apache.spark.sql.functions::col)
                .toArray(Column[]::new);
        Dataset<Row> duplicates = input.groupBy(fields)
                .agg(count(lit(1)).alias("_duplicate_count"))
                .filter(col("_duplicate_count").gt(1));
        return duplicates
                .agg(coalesce(sum(col("_duplicate_count").minus(1)), lit(0L)).cast("long").alias("affected_records"))
                .filter(col("affected_records").gt(0))
                .select(
                        lit("DUPLICATE_RECORDS").alias("issue_type"),
                        lit("*").alias("field_name"),
                        col("affected_records"),
                        lit("ERROR").alias("severity"),
                        lit("Complete source records occur more than once.").alias("description"));
    }

    public static Dataset<Row> invalidDateSummary(Dataset<Row> input) {
        List<Dataset<Row>> issues = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            String name = field.name().toLowerCase(Locale.ROOT);
            if (!DataTypes.StringType.equals(field.dataType())
                    || !(name.contains("date") || name.contains("time") || name.endsWith("_at"))) {
                continue;
            }
            Column value = trim(col(field.name()));
            Dataset<Row> issue = input.agg(sum(when(
                            value.notEqual("").and(to_timestamp(value).isNull()), 1).otherwise(0))
                            .cast("long").alias("affected_records"))
                    .filter(col("affected_records").gt(0))
                    .select(
                            lit("INVALID_DATE").alias("issue_type"),
                            lit(field.name()).alias("field_name"),
                            col("affected_records"),
                            lit("ERROR").alias("severity"),
                            lit("Date-like text values cannot be parsed as timestamps.").alias("description"));
            issues.add(issue);
        }
        return unionOrEmpty(input, issues);
    }

    public static Dataset<Row> numericOutlierSummary(Dataset<Row> input, double threshold) {
        List<Dataset<Row>> issues = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            if (!isNumeric(field.dataType())) {
                continue;
            }
            Column value = col(field.name()).cast("double");
            Dataset<Row> scored = input
                    .withColumn("_value", value)
                    .withColumn("_average", avg(value).over(Window.partitionBy(lit(1))))
                    .withColumn("_stddev", stddev_pop(value).over(Window.partitionBy(lit(1))));
            Dataset<Row> issue = scored
                    .filter(col("_value").isNotNull()
                            .and(col("_stddev").gt(0))
                            .and(abs(col("_value").minus(col("_average")))
                                    .gt(col("_stddev").multiply(threshold))))
                    .agg(count(lit(1)).cast("long").alias("affected_records"))
                    .filter(col("affected_records").gt(0))
                    .select(
                            lit("NUMERIC_OUTLIER").alias("issue_type"),
                            lit(field.name()).alias("field_name"),
                            col("affected_records"),
                            lit("WARNING").alias("severity"),
                            lit("Values exceed the configured standard-deviation threshold.").alias("description"));
            issues.add(issue);
        }
        return unionOrEmpty(input, issues);
    }

    public static Dataset<Row> inconsistentCategorySummary(Dataset<Row> input) {
        List<Dataset<Row>> issues = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            if (!DataTypes.StringType.equals(field.dataType())) {
                continue;
            }
            Column normalized = lower(regexp_replace(trim(col(field.name())), "[^\\p{L}\\p{N}]", ""));
            Dataset<Row> variants = input
                    .filter(col(field.name()).isNotNull().and(trim(col(field.name())).notEqual("")))
                    .groupBy(normalized.alias("_normalized"))
                    .agg(
                            countDistinct(col(field.name())).alias("_variant_count"),
                            count(lit(1)).alias("_records"))
                    .filter(col("_variant_count").gt(1));
            Dataset<Row> issue = variants
                    .agg(coalesce(sum("_records"), lit(0L)).cast("long").alias("affected_records"))
                    .filter(col("affected_records").gt(0))
                    .select(
                            lit("INCONSISTENT_CATEGORY").alias("issue_type"),
                            lit(field.name()).alias("field_name"),
                            col("affected_records"),
                            lit("WARNING").alias("severity"),
                            lit("Category variants differ only by case, spacing, or punctuation.").alias("description"));
            issues.add(issue);
        }
        return unionOrEmpty(input, issues);
    }

    public static Dataset<Row> suspiciousTextSummary(Dataset<Row> input) {
        List<Dataset<Row>> issues = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            if (!DataTypes.StringType.equals(field.dataType())) {
                continue;
            }
            Column value = col(field.name()).cast("string");
            Column suspicious = value.notEqual(trim(value))
                    .or(value.rlike("[\\p{Cntrl}]") )
                    .or(value.rlike("<[^>]+>"))
                    .or(value.rlike("(.)\\1{5,}"))
                    .or(org.apache.spark.sql.functions.length(value).gt(4000));
            Dataset<Row> issue = input
                    .agg(sum(when(value.isNotNull().and(suspicious), 1).otherwise(0))
                            .cast("long").alias("affected_records"))
                    .filter(col("affected_records").gt(0))
                    .select(
                            lit("SUSPICIOUS_TEXT").alias("issue_type"),
                            lit(field.name()).alias("field_name"),
                            col("affected_records"),
                            lit("WARNING").alias("severity"),
                            lit("Text contains extra whitespace, control characters, markup, excessive length, or repeated characters.").alias("description"));
            issues.add(issue);
        }
        return unionOrEmpty(input, issues);
    }

    private static Dataset<Row> unionOrEmpty(Dataset<Row> input, List<Dataset<Row>> issues) {
        Dataset<Row> result = missingValueSummary(input).limit(0);
        for (Dataset<Row> issue : issues) {
            result = result.unionByName(issue);
        }
        return result;
    }

    private static boolean isNumeric(DataType type) {
        return DataTypes.ByteType.equals(type)
                || DataTypes.ShortType.equals(type)
                || DataTypes.IntegerType.equals(type)
                || DataTypes.LongType.equals(type)
                || DataTypes.FloatType.equals(type)
                || DataTypes.DoubleType.equals(type)
                || type.typeName().startsWith("decimal");
    }
}
