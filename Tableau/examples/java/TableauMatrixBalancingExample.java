package com.dataai.customer.examples;

import com.dataai.etl.spark.functions.MatrixBalanceResult;
import com.dataai.etl.spark.functions.MatrixFunctions;
import com.dataai.etl.spark.tableau.TableauFunctionOutputs;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SaveMode;

import java.time.Instant;
import java.util.UUID;

/** Publishes a DataAI balanced matrix as a customer-controlled Tableau table. */
public final class TableauMatrixBalancingExample {
    private TableauMatrixBalancingExample() {
    }

    public static void publish(
            Dataset<Row> cells,
            Dataset<Row> rowTargets,
            Dataset<Row> columnTargets) {
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

        TableauFunctionOutputs.matrixBalance(
                        balance,
                        UUID.randomUUID().toString(),
                        Instant.now(),
                        "0.1.0-SNAPSHOT")
                .write()
                .format("delta")
                .mode(SaveMode.Overwrite)
                .saveAsTable("analytics.dataai_matrix_balance");
    }
}
