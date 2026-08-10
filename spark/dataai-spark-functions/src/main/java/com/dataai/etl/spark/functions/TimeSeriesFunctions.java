package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.expressions.WindowSpec;

import java.util.ArrayList;
import java.util.List;

import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.lag;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.sum;

public final class TimeSeriesFunctions {
    private TimeSeriesFunctions() {
    }

    public static Dataset<Row> summarize(
            Dataset<Row> input,
            List<String> groupFields,
            String dateField,
            TimePeriod period,
            String valueField,
            Aggregation aggregation) {
        List<String> groups = groupFields == null ? List.of() : List.copyOf(groupFields);
        SparkFunctionSupport.requireFields(input, dateField, valueField);
        SparkFunctionSupport.requireFields(input, groups.toArray(String[]::new));
        Dataset<Row> prepared = input
                .withColumn("period_start", SparkFunctionSupport.period(dateField, period))
                .filter(col("period_start").isNotNull());
        List<String> keys = new ArrayList<>(groups);
        keys.add("period_start");
        Column measure = aggregation == Aggregation.COUNT ? lit(1) : col(valueField);
        return prepared.groupBy(SparkFunctionSupport.columns(keys))
                .agg(
                        aggregation.apply(measure).alias("period_value"),
                        count(lit(1)).alias("records"))
                .orderBy(SparkFunctionSupport.columns(keys));
    }

    public static Dataset<Row> rolling(
            Dataset<Row> input,
            List<String> groupFields,
            String dateField,
            TimePeriod period,
            String valueField,
            Aggregation aggregation,
            int windowPeriods,
            RollingOperation operation) {
        if (windowPeriods < 1) {
            throw new IllegalArgumentException("Rolling window must be at least one period.");
        }
        List<String> groups = groupFields == null ? List.of() : List.copyOf(groupFields);
        Dataset<Row> periods = summarize(input, groups, dateField, period, valueField, aggregation);
        WindowSpec ordered = groups.isEmpty()
                ? Window.partitionBy(lit(1)).orderBy(col("period_start"))
                : Window.partitionBy(SparkFunctionSupport.columns(groups)).orderBy(col("period_start"));
        WindowSpec rolling = ordered.rowsBetween(-(windowPeriods - 1L), 0);
        Column calculation = operation == RollingOperation.MOVING_AVERAGE
                ? avg(col("period_value")).over(rolling)
                : sum(col("period_value")).over(rolling);
        return periods
                .withColumn("rolling_operation", lit(operation.name()))
                .withColumn("window_periods", lit(windowPeriods))
                .withColumn("rolling_value", calculation)
                .withColumn("previous_value", lag(col("period_value"), 1).over(ordered))
                .withColumn("period_change", col("period_value").minus(col("previous_value")))
                .withColumn(
                        "period_change_percent",
                        SparkFunctionSupport.safeDivide(
                                col("period_value").minus(col("previous_value")),
                                org.apache.spark.sql.functions.abs(col("previous_value"))).multiply(100.0));
    }
}
