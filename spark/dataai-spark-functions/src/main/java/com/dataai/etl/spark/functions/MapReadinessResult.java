package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import java.util.List;

public record MapReadinessResult(
        Dataset<Row> classifiedRows,
        Dataset<Row> summary,
        Dataset<Row> validRows,
        Dataset<Row> invalidRows,
        List<String> suggestedLatitudeFields,
        List<String> suggestedLongitudeFields) {
}
