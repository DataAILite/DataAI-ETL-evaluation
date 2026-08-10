package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

public record MatrixBalanceResult(
        Dataset<Row> balancedCells,
        int iterations,
        double maximumError,
        boolean converged) {
}
