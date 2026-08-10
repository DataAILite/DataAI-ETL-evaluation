package com.dataai.etl.spark.core;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.types.DataType;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;

import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.length;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.trim;
import static org.apache.spark.sql.functions.when;

public final class Normalizer {
    private Normalizer() {
    }

    public static Dataset<Row> normalize(Dataset<Row> input) {
        Dataset<Row> output = normalizeNames(input);
        for (StructField field : output.schema().fields()) {
            DataType type = field.dataType();
            if (DataTypes.StringType.equals(type)) {
                output = output.withColumn(
                        field.name(),
                        when(length(trim(col(field.name()))).equalTo(0), lit(null))
                                .otherwise(trim(col(field.name()))));
            }
        }
        return output;
    }

    private static Dataset<Row> normalizeNames(Dataset<Row> input) {
        Dataset<Row> output = input;
        Set<String> names = new HashSet<>();
        for (String original : input.columns()) {
            String normalized = original
                    .trim()
                    .replaceAll("([a-z0-9])([A-Z])", "$1_$2")
                    .replaceAll("[^A-Za-z0-9]+", "_")
                    .replaceAll("^_+|_+$", "")
                    .toLowerCase(Locale.ROOT);
            if (normalized.isBlank()) {
                throw new IllegalArgumentException("Column name cannot be normalized: " + original);
            }
            if (!names.add(normalized)) {
                throw new IllegalArgumentException(
                        "Column normalization creates duplicate name: " + normalized);
            }
            if (!original.equals(normalized)) {
                output = output.withColumnRenamed(original, normalized);
            }
        }
        return output;
    }
}

