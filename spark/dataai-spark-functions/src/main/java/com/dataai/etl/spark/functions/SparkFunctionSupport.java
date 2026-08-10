package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import java.util.Arrays;
import java.util.List;

import static org.apache.spark.sql.functions.coalesce;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.concat_ws;
import static org.apache.spark.sql.functions.date_trunc;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.when;

final class SparkFunctionSupport {
    private SparkFunctionSupport() {
    }

    static void requireFields(Dataset<Row> input, String... fields) {
        List<String> available = Arrays.asList(input.columns());
        for (String field : fields) {
            if (field != null && !field.isBlank() && !available.contains(field)) {
                throw new IllegalArgumentException("DataAI function references missing field: " + field);
            }
        }
    }

    static Column[] columns(List<String> fields) {
        return fields.stream().map(org.apache.spark.sql.functions::col).toArray(Column[]::new);
    }

    static Column dimension(List<String> fields) {
        if (fields == null || fields.isEmpty()) {
            return lit("All Records");
        }
        Column[] values = fields.stream()
                .map(field -> coalesce(col(field).cast("string"), lit("<null>")))
                .toArray(Column[]::new);
        return concat_ws(" | ", values);
    }

    static Column period(String dateField, TimePeriod period) {
        String unit = switch (period) {
            case DAY -> "day";
            case WEEK -> "week";
            case MONTH -> "month";
            case QUARTER -> "quarter";
            case YEAR -> "year";
        };
        return date_trunc(unit, col(dateField).cast("timestamp"));
    }

    static Column safeDivide(Column numerator, Column denominator) {
        return when(denominator.isNotNull().and(denominator.notEqual(0)), numerator.divide(denominator))
                .otherwise(lit(null).cast("double"));
    }

    static double percentRate(double percent) {
        return percent / 100.0;
    }
}
