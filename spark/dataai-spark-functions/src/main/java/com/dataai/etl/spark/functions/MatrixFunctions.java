package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import static org.apache.spark.sql.functions.abs;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.max;
import static org.apache.spark.sql.functions.sum;
import static org.apache.spark.sql.functions.when;

public final class MatrixFunctions {
    private MatrixFunctions() {
    }

    public static Dataset<Row> crossTab(
            Dataset<Row> input,
            String rowField,
            String columnField,
            String valueField,
            Aggregation aggregation) {
        return AnalyticsFunctions.pivot(input, rowField, columnField, valueField, aggregation);
    }

    public static MatrixBalanceResult balance(
            Dataset<Row> input,
            String rowField,
            String columnField,
            String valueField,
            Dataset<Row> rowTargets,
            Dataset<Row> columnTargets,
            String targetColumn,
            int maximumIterations,
            double tolerance) {
        if (maximumIterations < 1) {
            throw new IllegalArgumentException("Maximum iterations must be at least one.");
        }
        if (tolerance < 0) {
            throw new IllegalArgumentException("Tolerance cannot be negative.");
        }
        SparkFunctionSupport.requireFields(input, rowField, columnField, valueField);
        SparkFunctionSupport.requireFields(rowTargets, rowField, targetColumn);
        SparkFunctionSupport.requireFields(columnTargets, columnField, targetColumn);

        Dataset<Row> rowControls = rowTargets
                .select(
                        col(rowField).alias("_row"),
                        col(targetColumn).cast("double").alias("_row_target"));
        Dataset<Row> columnControls = columnTargets
                .select(
                        col(columnField).alias("_column"),
                        col(targetColumn).cast("double").alias("_column_target"));
        Dataset<Row> cells = input
                .groupBy(col(rowField), col(columnField))
                .agg(sum(col(valueField).cast("double")).alias("original_value"))
                .select(
                        col(rowField).alias("_row"),
                        col(columnField).alias("_column"),
                        col("original_value"),
                        col("original_value").alias("balanced_value"));

        int iterations = 0;
        double maximumError = Double.POSITIVE_INFINITY;
        while (iterations < maximumIterations && maximumError > tolerance) {
            Dataset<Row> rowSums = cells.groupBy("_row")
                    .agg(sum("balanced_value").alias("_row_sum"));
            cells = cells
                    .join(rowControls, "_row", "left")
                    .join(rowSums, "_row", "left")
                    .withColumn(
                            "balanced_value",
                            when(col("_row_target").isNotNull().and(col("_row_sum").notEqual(0)),
                                    col("balanced_value").multiply(col("_row_target")).divide(col("_row_sum")))
                                    .otherwise(col("balanced_value")))
                    .select("_row", "_column", "original_value", "balanced_value");

            Dataset<Row> columnSums = cells.groupBy("_column")
                    .agg(sum("balanced_value").alias("_column_sum"));
            cells = cells
                    .join(columnControls, "_column", "left")
                    .join(columnSums, "_column", "left")
                    .withColumn(
                            "balanced_value",
                            when(col("_column_target").isNotNull().and(col("_column_sum").notEqual(0)),
                                    col("balanced_value").multiply(col("_column_target")).divide(col("_column_sum")))
                                    .otherwise(col("balanced_value")))
                    .select("_row", "_column", "original_value", "balanced_value");
            iterations++;
            maximumError = maximumError(cells, rowControls, columnControls);
        }

        Dataset<Row> finalRowSums = cells.groupBy("_row")
                .agg(sum("balanced_value").alias("balanced_row_total"));
        Dataset<Row> finalColumnSums = cells.groupBy("_column")
                .agg(sum("balanced_value").alias("balanced_column_total"));
        Dataset<Row> output = cells
                .join(rowControls, "_row", "left")
                .join(columnControls, "_column", "left")
                .join(finalRowSums, "_row", "left")
                .join(finalColumnSums, "_column", "left")
                .withColumn("balancing_coefficient", SparkFunctionSupport.safeDivide(
                        col("balanced_value"), col("original_value")))
                .withColumn("row_difference", col("balanced_row_total").minus(col("_row_target")))
                .withColumn("column_difference", col("balanced_column_total").minus(col("_column_target")))
                .withColumn("iterations", lit(iterations))
                .withColumn("converged", lit(maximumError <= tolerance))
                .withColumnRenamed("_row", rowField)
                .withColumnRenamed("_column", columnField)
                .withColumnRenamed("_row_target", "row_target")
                .withColumnRenamed("_column_target", "column_target");
        return new MatrixBalanceResult(output, iterations, maximumError, maximumError <= tolerance);
    }

    private static double maximumError(
            Dataset<Row> cells,
            Dataset<Row> rowControls,
            Dataset<Row> columnControls) {
        Dataset<Row> rowErrors = cells.groupBy("_row")
                .agg(sum("balanced_value").alias("actual"))
                .join(rowControls, "_row", "inner")
                .select(abs(col("actual").minus(col("_row_target"))).alias("error"));
        Dataset<Row> columnErrors = cells.groupBy("_column")
                .agg(sum("balanced_value").alias("actual"))
                .join(columnControls, "_column", "inner")
                .select(abs(col("actual").minus(col("_column_target"))).alias("error"));
        Row row = rowErrors.unionByName(columnErrors)
                .agg(max("error").alias("maximum_error"))
                .first();
        Object value = row.get(0);
        return value == null ? 0.0 : ((Number) value).doubleValue();
    }
}
