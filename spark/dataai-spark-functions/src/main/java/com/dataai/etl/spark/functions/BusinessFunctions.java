package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.expressions.WindowSpec;

import java.util.ArrayList;
import java.util.List;

import static org.apache.spark.sql.functions.abs;
import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.countDistinct;
import static org.apache.spark.sql.functions.datediff;
import static org.apache.spark.sql.functions.first;
import static org.apache.spark.sql.functions.floor;
import static org.apache.spark.sql.functions.lag;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.max;
import static org.apache.spark.sql.functions.min;
import static org.apache.spark.sql.functions.months_between;
import static org.apache.spark.sql.functions.stddev_pop;
import static org.apache.spark.sql.functions.sum;
import static org.apache.spark.sql.functions.when;

public final class BusinessFunctions {
    private BusinessFunctions() {
    }

    public static Dataset<Row> pareto(
            Dataset<Row> input,
            String dimensionField,
            String valueField,
            Aggregation aggregation) {
        Dataset<Row> grouped = AnalyticsFunctions.groupedSummary(
                input, List.of(dimensionField), valueField, aggregation);
        WindowSpec all = Window.partitionBy(lit(1));
        WindowSpec cumulative = Window.orderBy(col("value").desc_nulls_last(), col(dimensionField))
                .rowsBetween(Window.unboundedPreceding(), Window.currentRow());
        return grouped
                .withColumn("total_value", sum(col("value")).over(all))
                .withColumn("share_percent", SparkFunctionSupport.safeDivide(col("value"), col("total_value")).multiply(100.0))
                .withColumn("cumulative_value", sum(col("value")).over(cumulative))
                .withColumn("cumulative_percent", SparkFunctionSupport.safeDivide(col("cumulative_value"), col("total_value")).multiply(100.0))
                .withColumn(
                        "abc_class",
                        when(col("cumulative_percent").leq(80), "A")
                                .when(col("cumulative_percent").leq(95), "B")
                                .otherwise("C"));
    }

    public static Dataset<Row> drift(
            Dataset<Row> input,
            String comparedField,
            String segmentField,
            String baseSegment,
            String comparisonSegment) {
        SparkFunctionSupport.requireFields(input, comparedField, segmentField);
        Column base = col(segmentField).cast("string").equalTo(baseSegment);
        Column comparison = col(segmentField).cast("string").equalTo(comparisonSegment);
        Dataset<Row> counts = input.groupBy(col(comparedField)).agg(
                sum(when(base, 1).otherwise(0)).alias("base_records"),
                sum(when(comparison, 1).otherwise(0)).alias("comparison_records"));
        WindowSpec all = Window.partitionBy(lit(1));
        return counts
                .withColumn("base_total", sum(col("base_records")).over(all))
                .withColumn("comparison_total", sum(col("comparison_records")).over(all))
                .withColumn("base_share_percent", SparkFunctionSupport.safeDivide(col("base_records"), col("base_total")).multiply(100.0))
                .withColumn("comparison_share_percent", SparkFunctionSupport.safeDivide(col("comparison_records"), col("comparison_total")).multiply(100.0))
                .withColumn("drift_points", col("comparison_share_percent").minus(col("base_share_percent")))
                .orderBy(abs(col("drift_points")).desc());
    }

    public static Dataset<Row> outliers(
            Dataset<Row> input,
            List<String> groupFields,
            String valueField,
            OutlierMethod method,
            double threshold,
            Double businessMinimum,
            Double businessMaximum) {
        List<String> groups = groupFields == null ? List.of() : List.copyOf(groupFields);
        SparkFunctionSupport.requireFields(input, valueField);
        SparkFunctionSupport.requireFields(input, groups.toArray(String[]::new));
        WindowSpec partition = groups.isEmpty()
                ? Window.partitionBy(lit(1))
                : Window.partitionBy(SparkFunctionSupport.columns(groups));
        Dataset<Row> scored = input
                .withColumn("_dataai_numeric_value", col(valueField).cast("double"))
                .withColumn("_dataai_average", avg(col("_dataai_numeric_value")).over(partition))
                .withColumn("_dataai_standard_deviation", stddev_pop(col("_dataai_numeric_value")).over(partition))
                .withColumn("_dataai_difference", col("_dataai_numeric_value").minus(col("_dataai_average")))
                .withColumn(
                        "_dataai_z_score",
                        SparkFunctionSupport.safeDivide(abs(col("_dataai_difference")), col("_dataai_standard_deviation")))
                .withColumn(
                        "_dataai_percent_difference",
                        SparkFunctionSupport.safeDivide(abs(col("_dataai_difference")), abs(col("_dataai_average"))).multiply(100.0));
        Column violation = switch (method) {
            case STANDARD_DEVIATION -> col("_dataai_z_score").geq(threshold);
            case PERCENT_DIFFERENCE -> col("_dataai_percent_difference").geq(threshold);
            case BUSINESS_RANGE -> {
                Column below = businessMinimum == null ? lit(false) : col("_dataai_numeric_value").lt(businessMinimum);
                Column above = businessMaximum == null ? lit(false) : col("_dataai_numeric_value").gt(businessMaximum);
                yield below.or(above);
            }
        };
        return scored
                .filter(col("_dataai_numeric_value").isNotNull().and(violation))
                .withColumn("_dataai_outlier_method", lit(method.name()))
                .withColumn("_dataai_threshold", lit(threshold));
    }

    public static Dataset<Row> anomalyScores(
            Dataset<Row> input,
            List<String> groupFields,
            String valueField,
            double minimumScore) {
        return outliers(
                        input,
                        groupFields,
                        valueField,
                        OutlierMethod.STANDARD_DEVIATION,
                        minimumScore,
                        null,
                        null)
                .withColumnRenamed("_dataai_z_score", "anomaly_score")
                .withColumn("anomaly_type", lit("UNUSUAL_VALUE_WITHIN_GROUP"))
                .orderBy(col("anomaly_score").desc());
    }

    public static Dataset<Row> kpi(
            Dataset<Row> input,
            List<String> dimensionFields,
            String numeratorField,
            String denominatorField,
            KpiOperation operation) {
        List<String> dimensions = dimensionFields == null ? List.of() : List.copyOf(dimensionFields);
        SparkFunctionSupport.requireFields(input, numeratorField, denominatorField);
        SparkFunctionSupport.requireFields(input, dimensions.toArray(String[]::new));
        Dataset<Row> values = input.groupBy(SparkFunctionSupport.columns(dimensions)).agg(
                count(lit(1)).alias("records"),
                sum(col(numeratorField).cast("double")).alias("numerator"),
                sum(col(denominatorField).cast("double")).alias("denominator"));
        Column result = switch (operation) {
            case RATIO -> SparkFunctionSupport.safeDivide(col("numerator"), col("denominator"));
            case DIFFERENCE -> col("numerator").minus(col("denominator"));
            case SUM -> col("numerator").plus(col("denominator"));
            case PRODUCT -> col("numerator").multiply(col("denominator"));
        };
        return values
                .withColumn("operation", lit(operation.name()))
                .withColumn("kpi_value", result)
                .orderBy(col("kpi_value").desc_nulls_last());
    }

    public static Dataset<Row> funnel(
            Dataset<Row> input,
            String stageField,
            String entityField,
            String valueField,
            List<String> orderedStages) {
        SparkFunctionSupport.requireFields(input, stageField, entityField, valueField);
        Column stageOrder = lit(orderedStages == null ? 1 : orderedStages.size() + 1);
        if (orderedStages != null) {
            for (int i = orderedStages.size() - 1; i >= 0; i--) {
                stageOrder = when(col(stageField).cast("string").equalTo(orderedStages.get(i)), i + 1)
                        .otherwise(stageOrder);
            }
        }
        Dataset<Row> prepared = input.withColumn("stage_order", stageOrder);
        Column entities = entityField == null || entityField.isBlank()
                ? count(lit(1))
                : countDistinct(col(entityField));
        Column value = valueField == null || valueField.isBlank()
                ? count(lit(1)).cast("double")
                : sum(col(valueField).cast("double"));
        Dataset<Row> stages = prepared.groupBy(col(stageField), col("stage_order")).agg(
                count(lit(1)).alias("records"),
                entities.alias("entities"),
                value.alias("value"));
        WindowSpec ordered = Window.orderBy(col("stage_order"), col(stageField).cast("string"));
        WindowSpec complete = ordered.rowsBetween(Window.unboundedPreceding(), Window.unboundedFollowing());
        return stages
                .withColumn("previous_entities", lag(col("entities"), 1).over(ordered))
                .withColumn("first_stage_entities", first(col("entities"), true).over(complete))
                .withColumn("drop_off", col("previous_entities").minus(col("entities")))
                .withColumn("stage_conversion_percent", SparkFunctionSupport.safeDivide(col("entities"), col("previous_entities")).multiply(100.0))
                .withColumn("overall_conversion_percent", SparkFunctionSupport.safeDivide(col("entities"), col("first_stage_entities")).multiply(100.0))
                .orderBy("stage_order");
    }

    public static Dataset<Row> cohort(
            Dataset<Row> input,
            String entityField,
            String activityDateField,
            String valueField,
            TimePeriod period) {
        SparkFunctionSupport.requireFields(input, entityField, activityDateField, valueField);
        Dataset<Row> activity = input
                .withColumn("activity_period", SparkFunctionSupport.period(activityDateField, period))
                .filter(col(entityField).isNotNull().and(col("activity_period").isNotNull()));
        Dataset<Row> entityCohorts = activity.groupBy(col(entityField))
                .agg(min(col("activity_period")).alias("cohort_period"));
        Dataset<Row> joined = activity.join(entityCohorts, entityField, "inner");
        Column value = valueField == null || valueField.isBlank()
                ? count(lit(1)).cast("double")
                : sum(col(valueField).cast("double"));
        Dataset<Row> summary = joined.groupBy("cohort_period", "activity_period").agg(
                countDistinct(col(entityField)).alias("entities"),
                count(lit(1)).alias("records"),
                value.alias("value"));
        Dataset<Row> sizes = entityCohorts.groupBy("cohort_period")
                .agg(countDistinct(col(entityField)).alias("cohort_size"));
        Column periodNumber = switch (period) {
            case DAY -> datediff(col("activity_period"), col("cohort_period"));
            case WEEK -> floor(datediff(col("activity_period"), col("cohort_period")).divide(7));
            case MONTH -> floor(months_between(col("activity_period"), col("cohort_period")));
            case QUARTER -> floor(months_between(col("activity_period"), col("cohort_period")).divide(3));
            case YEAR -> floor(months_between(col("activity_period"), col("cohort_period")).divide(12));
        };
        return summary.join(sizes, "cohort_period")
                .withColumn("period_number", periodNumber.cast("integer"))
                .withColumn("retention_percent", SparkFunctionSupport.safeDivide(col("entities"), col("cohort_size")).multiply(100.0))
                .orderBy("cohort_period", "activity_period");
    }
}
