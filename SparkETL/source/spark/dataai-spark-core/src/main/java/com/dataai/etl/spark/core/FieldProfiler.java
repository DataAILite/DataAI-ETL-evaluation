package com.dataai.etl.spark.core;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.types.StructField;

import java.util.ArrayList;
import java.util.List;

import static org.apache.spark.sql.functions.approx_count_distinct;
import static org.apache.spark.sql.functions.array;
import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.explode;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.max;
import static org.apache.spark.sql.functions.min;
import static org.apache.spark.sql.functions.stddev_pop;
import static org.apache.spark.sql.functions.struct;

public final class FieldProfiler {
    private FieldProfiler() {
    }

    public static Dataset<Row> profile(Dataset<Row> input) {
        StructField[] fields = input.schema().fields();
        if (fields.length == 0) {
            throw new IllegalArgumentException("Cannot profile a dataset without fields.");
        }

        List<Column> aggregates = new ArrayList<>();
        aggregates.add(count(lit(1)).alias("_record_count"));
        for (int i = 0; i < fields.length; i++) {
            String name = fields[i].name();
            aggregates.add(count(col(name)).alias(alias(i, "non_null")));
            aggregates.add(approx_count_distinct(col(name)).alias(alias(i, "distinct")));
            aggregates.add(min(col(name).cast("string")).alias(alias(i, "minimum")));
            aggregates.add(max(col(name).cast("string")).alias(alias(i, "maximum")));
            aggregates.add(avg(col(name).cast("double")).alias(alias(i, "mean")));
            aggregates.add(stddev_pop(col(name).cast("double")).alias(alias(i, "stddev")));
        }

        Dataset<Row> aggregate = input.agg(
                aggregates.get(0),
                aggregates.subList(1, aggregates.size()).toArray(Column[]::new));

        List<Column> profiles = new ArrayList<>();
        for (int i = 0; i < fields.length; i++) {
            StructField field = fields[i];
            profiles.add(struct(
                    lit(field.name()).alias("field_name"),
                    lit(field.dataType().typeName()).alias("source_type"),
                    col("_record_count").alias("record_count"),
                    col("_record_count").minus(col(alias(i, "non_null"))).alias("null_count"),
                    col(alias(i, "distinct")).alias("distinct_count"),
                    col(alias(i, "minimum")).alias("minimum_value"),
                    col(alias(i, "maximum")).alias("maximum_value"),
                    col(alias(i, "mean")).alias("mean_value"),
                    col(alias(i, "stddev")).alias("standard_deviation")));
        }

        return aggregate
                .select(explode(array(profiles.toArray(Column[]::new))).alias("profile"))
                .select("profile.*");
    }

    private static String alias(int fieldIndex, String metric) {
        return "_f" + fieldIndex + "_" + metric;
    }
}
