package com.dataai.etl.spark.iris;

import org.apache.spark.sql.DataFrameReader;
import org.apache.spark.sql.DataFrameWriter;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

import java.util.Objects;

/** Explicit Spark JDBC entry points for customer-controlled IRIS access. */
public final class IrisDataFrames {
    private IrisDataFrames() {
    }

    /** Returns a configured reader; no query is run until the caller loads data. */
    public static DataFrameReader reader(SparkSession spark, IrisJdbcOptions options) {
        Objects.requireNonNull(spark, "spark");
        Objects.requireNonNull(options, "options");
        return options.apply(spark.read());
    }

    public static Dataset<Row> readTable(
            SparkSession spark,
            IrisJdbcOptions options,
            String table) {
        return reader(spark, options)
                .option("dbtable", requireText(table, "table"))
                .load();
    }

    public static Dataset<Row> readTablePartitioned(
            SparkSession spark,
            IrisJdbcOptions options,
            String table,
            String partitionColumn,
            long lowerBound,
            long upperBound,
            int numPartitions) {
        if (upperBound <= lowerBound) {
            throw new IllegalArgumentException("upperBound must be greater than lowerBound.");
        }
        if (numPartitions < 1) {
            throw new IllegalArgumentException("numPartitions must be at least one.");
        }
        return reader(spark, options)
                .option("dbtable", requireText(table, "table"))
                .option("partitionColumn", requireIdentifier(partitionColumn, "partitionColumn"))
                .option("lowerBound", lowerBound)
                .option("upperBound", upperBound)
                .option("numPartitions", numPartitions)
                .load();
    }

    public static Dataset<Row> readQuery(
            SparkSession spark,
            IrisJdbcOptions options,
            String query) {
        return reader(spark, options)
                .option("query", requireText(query, "query"))
                .load();
    }

    /**
     * Returns a configured writer without selecting a table, mode, or calling
     * save. The customer must explicitly provide those choices.
     */
    public static DataFrameWriter<Row> writer(
            Dataset<Row> output,
            IrisJdbcOptions options) {
        Objects.requireNonNull(output, "output");
        Objects.requireNonNull(options, "options");
        return options.apply(output.write());
    }

    private static String requireIdentifier(String value, String name) {
        String text = requireText(value, name);
        if (!text.matches("[A-Za-z_][A-Za-z0-9_]*")) {
            throw new IllegalArgumentException(name + " must be a simple SQL identifier.");
        }
        return text;
    }

    private static String requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " cannot be blank.");
        }
        return value;
    }
}
