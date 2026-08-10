package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.expressions.WindowSpec;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import static org.apache.spark.sql.functions.abs;
import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.max;
import static org.apache.spark.sql.functions.min;
import static org.apache.spark.sql.functions.pow;
import static org.apache.spark.sql.functions.sqrt;
import static org.apache.spark.sql.functions.sum;
import static org.apache.spark.sql.functions.when;

public final class AnalyticsFunctions {
    private AnalyticsFunctions() {
    }

    public static Dataset<Row> groupedSummary(
            Dataset<Row> input,
            List<String> groupFields,
            String valueField,
            Aggregation aggregation) {
        List<String> groups = groupFields == null ? List.of() : List.copyOf(groupFields);
        SparkFunctionSupport.requireFields(input, valueField);
        SparkFunctionSupport.requireFields(input, groups.toArray(String[]::new));
        Column measure = aggregation == Aggregation.COUNT ? lit(1) : col(valueField);
        return input.groupBy(SparkFunctionSupport.columns(groups))
                .agg(
                        aggregation.apply(measure).alias("value"),
                        count(lit(1)).alias("records"));
    }

    public static Dataset<Row> pivot(
            Dataset<Row> input,
            String rowField,
            String columnField,
            String valueField,
            Aggregation aggregation) {
        SparkFunctionSupport.requireFields(input, rowField, columnField, valueField);
        Column measure = aggregation == Aggregation.COUNT ? lit(1) : col(valueField);
        return input.groupBy(col(rowField))
                .pivot(columnField)
                .agg(aggregation.apply(measure));
    }

    public static Dataset<Row> variance(
            Dataset<Row> input,
            List<String> groupFields,
            String compareField,
            String baseValue,
            String comparisonValue,
            String valueField,
            Aggregation aggregation) {
        List<String> groups = groupFields == null ? List.of() : List.copyOf(groupFields);
        SparkFunctionSupport.requireFields(input, compareField, valueField);
        SparkFunctionSupport.requireFields(input, groups.toArray(String[]::new));

        Column rawMeasure = aggregation == Aggregation.COUNT ? lit(1) : col(valueField);
        Column baseCondition = col(compareField).cast("string").equalTo(baseValue);
        Column comparisonCondition = col(compareField).cast("string").equalTo(comparisonValue);
        Dataset<Row> result = input.groupBy(SparkFunctionSupport.columns(groups)).agg(
                aggregation.apply(when(baseCondition, rawMeasure)).alias("base_value"),
                aggregation.apply(when(comparisonCondition, rawMeasure)).alias("comparison_value"),
                sum(when(baseCondition, 1).otherwise(0)).alias("base_records"),
                sum(when(comparisonCondition, 1).otherwise(0)).alias("comparison_records"));
        return result
                .withColumn("variance", col("comparison_value").minus(col("base_value")))
                .withColumn(
                        "percent_change",
                        SparkFunctionSupport.safeDivide(
                                col("comparison_value").minus(col("base_value")),
                                abs(col("base_value"))).multiply(100.0))
                .withColumn(
                        "contribution_percent",
                        SparkFunctionSupport.safeDivide(
                                col("comparison_value"),
                                sum(col("comparison_value")).over(Window.partitionBy(lit(1))))
                                .multiply(100.0));
    }

    public static Dataset<Row> ranking(
            Dataset<Row> input,
            String rankField,
            List<String> withinGroupFields,
            String valueField,
            Aggregation aggregation,
            RankMode mode,
            int limitPerGroup) {
        if (limitPerGroup < 1) {
            throw new IllegalArgumentException("Ranking limit must be at least one.");
        }
        List<String> within = withinGroupFields == null ? List.of() : List.copyOf(withinGroupFields);
        Set<String> fields = new LinkedHashSet<>(within);
        fields.add(rankField);
        Dataset<Row> summary = groupedSummary(input, List.copyOf(fields), valueField, aggregation);
        WindowSpec partition = within.isEmpty()
                ? Window.partitionBy(lit(1))
                : Window.partitionBy(SparkFunctionSupport.columns(within));
        Column sort = switch (mode) {
            case TOP -> col("value").desc_nulls_last();
            case BOTTOM -> col("value").asc_nulls_last();
            case AVERAGE_NEAREST -> abs(col("value").minus(avg(col("value")).over(partition))).asc_nulls_last();
        };
        WindowSpec rankingWindow = partition.orderBy(sort, col(rankField).cast("string").asc());
        return summary
                .withColumn("rank", org.apache.spark.sql.functions.row_number().over(rankingWindow))
                .withColumn("rank_mode", lit(mode.name()))
                .filter(col("rank").leq(limitPerGroup));
    }

    public static Dataset<Row> correlations(Dataset<Row> input, List<String> numericFields) {
        if (numericFields == null || numericFields.size() < 2) {
            throw new IllegalArgumentException("Correlation requires at least two numeric fields.");
        }
        SparkFunctionSupport.requireFields(input, numericFields.toArray(String[]::new));
        List<Row> rows = new ArrayList<>();
        for (int i = 0; i < numericFields.size(); i++) {
            for (int j = i + 1; j < numericFields.size(); j++) {
                String left = numericFields.get(i);
                String right = numericFields.get(j);
                double correlation = input.select(
                                col(left).cast("double").alias(left),
                                col(right).cast("double").alias(right))
                        .na().drop()
                        .stat().corr(left, right);
                rows.add(RowFactory.create(
                        left,
                        right,
                        correlation,
                        correlation > 0 ? "POSITIVE" : correlation < 0 ? "NEGATIVE" : "NONE",
                        strength(correlation)));
            }
        }
        StructType schema = new StructType()
                .add("field_a", DataTypes.StringType, false)
                .add("field_b", DataTypes.StringType, false)
                .add("correlation", DataTypes.DoubleType, true)
                .add("direction", DataTypes.StringType, false)
                .add("strength", DataTypes.StringType, false);
        return input.sparkSession().createDataFrame(rows, schema);
    }

    public static Dataset<Row> correlationThreshold(
            Dataset<Row> input,
            List<String> numericFields,
            double minimumAbsoluteCorrelation,
            String direction) {
        Dataset<Row> result = correlations(input, numericFields)
                .filter(abs(col("correlation")).geq(minimumAbsoluteCorrelation));
        if (direction == null || direction.isBlank() || direction.equalsIgnoreCase("BOTH")) {
            return result;
        }
        return result.filter(col("direction").equalTo(direction.toUpperCase()));
    }

    public static Dataset<Row> linearRegression(
            Dataset<Row> input,
            String xField,
            String yField,
            String groupField,
            Double predictionX) {
        SparkFunctionSupport.requireFields(input, xField, yField, groupField);
        Column group = groupField == null || groupField.isBlank()
                ? lit("All Records")
                : col(groupField).cast("string");
        Dataset<Row> points = input
                .select(
                        group.alias("group_value"),
                        col(xField).cast("double").alias("x"),
                        col(yField).cast("double").alias("y"))
                .filter(col("x").isNotNull().and(col("y").isNotNull()));
        Dataset<Row> stats = points.groupBy("group_value").agg(
                count(lit(1)).alias("records"),
                sum("x").alias("sum_x"),
                sum("y").alias("sum_y"),
                sum(col("x").multiply(col("x"))).alias("sum_xx"),
                sum(col("y").multiply(col("y"))).alias("sum_yy"),
                sum(col("x").multiply(col("y"))).alias("sum_xy"),
                avg("x").alias("average_x"),
                avg("y").alias("average_y"),
                min("x").alias("minimum_x"),
                max("x").alias("maximum_x"));

        Column n = col("records").cast("double");
        Column xDenominator = n.multiply(col("sum_xx")).minus(pow(col("sum_x"), 2));
        Column yDenominator = n.multiply(col("sum_yy")).minus(pow(col("sum_y"), 2));
        Column numerator = n.multiply(col("sum_xy")).minus(col("sum_x").multiply(col("sum_y")));
        Dataset<Row> fitted = stats
                .withColumn("slope", SparkFunctionSupport.safeDivide(numerator, xDenominator))
                .withColumn(
                        "intercept",
                        SparkFunctionSupport.safeDivide(
                                col("sum_y").minus(col("slope").multiply(col("sum_x"))), n))
                .withColumn(
                        "correlation",
                        SparkFunctionSupport.safeDivide(
                                numerator,
                                sqrt(xDenominator.multiply(yDenominator))))
                .withColumn("r_squared", pow(col("correlation"), 2))
                .withColumn("equation", org.apache.spark.sql.functions.concat(
                        lit("y = "), col("intercept"), lit(" + "), col("slope"), lit(" * x")));
        Column predicted = predictionX == null
                ? lit(null).cast("double")
                : col("intercept").plus(col("slope").multiply(predictionX));
        return fitted
                .withColumn("prediction_x", predictionX == null ? lit(null).cast("double") : lit(predictionX))
                .withColumn("predicted_y", predicted)
                .select(
                        "group_value", "records", "equation", "slope", "intercept",
                        "correlation", "r_squared", "average_x", "average_y",
                        "minimum_x", "maximum_x", "prediction_x", "predicted_y");
    }

    private static String strength(double correlation) {
        if (Double.isNaN(correlation)) {
            return "UNDEFINED";
        }
        double absolute = Math.abs(correlation);
        if (absolute >= 0.9) return "VERY_STRONG";
        if (absolute >= 0.7) return "STRONG";
        if (absolute >= 0.5) return "MODERATE";
        if (absolute >= 0.3) return "WEAK";
        return "VERY_WEAK";
    }
}
