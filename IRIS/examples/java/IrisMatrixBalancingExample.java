package com.dataai.customer.examples;

import com.dataai.etl.spark.functions.MatrixBalanceResult;
import com.dataai.etl.spark.functions.MatrixFunctions;
import com.dataai.etl.spark.iris.IrisDataFrames;
import com.dataai.etl.spark.iris.IrisFunctionOutputs;
import com.dataai.etl.spark.iris.IrisJdbcOptions;
import com.dataai.etl.spark.iris.IrisOutputNames;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;

import java.time.Instant;
import java.util.UUID;

public final class IrisMatrixBalancingExample {
    private IrisMatrixBalancingExample() {
    }

    public static void publish(
            Dataset<Row> cells,
            Dataset<Row> rowTargets,
            Dataset<Row> columnTargets,
            IrisJdbcOptions iris) {
        MatrixBalanceResult balance = MatrixFunctions.balance(
                cells,
                "region",
                "category",
                "value",
                rowTargets,
                columnTargets,
                "target_total",
                50,
                0.001);
        if (!balance.converged()) {
            throw new IllegalStateException(
                    "Matrix did not converge; maximum error=" + balance.maximumError());
        }
        Dataset<Row> output = IrisFunctionOutputs.matrixBalance(
                balance,
                UUID.randomUUID().toString(),
                Instant.now(),
                "0.1.0-SNAPSHOT");
        IrisDataFrames.writer(output, iris)
                .option("dbtable", IrisOutputNames.MATRIX_BALANCE)
                .mode(SaveMode.Append)
                .save();
    }
}
