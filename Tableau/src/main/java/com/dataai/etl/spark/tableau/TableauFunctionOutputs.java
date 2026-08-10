package com.dataai.etl.spark.tableau;

import com.dataai.etl.spark.api.PipelineSummary;
import com.dataai.etl.spark.functions.MatrixBalanceResult;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;

import static org.apache.spark.sql.functions.lit;

/** Adds consistent run metadata to any DataAI analytical result DataFrame. */
public final class TableauFunctionOutputs {
    public static final String RESULT_NAME = "_dataai_result_name";
    public static final String RUN_ID = "_dataai_run_id";
    public static final String COMPLETED_AT = "_dataai_completed_at";
    public static final String LIBRARY_VERSION = "_dataai_library_version";

    private static final List<String> METADATA_COLUMNS = List.of(
            RESULT_NAME,
            RUN_ID,
            COMPLETED_AT,
            LIBRARY_VERSION);

    private TableauFunctionOutputs() {
    }

    /** Adds pipeline summary metadata without executing or persisting the result. */
    public static Dataset<Row> withRunMetadata(
            Dataset<Row> output,
            String resultName,
            PipelineSummary summary) {
        Objects.requireNonNull(summary, "summary");
        return withRunMetadata(
                output,
                resultName,
                summary.runId(),
                summary.completedAt(),
                summary.libraryVersion());
    }

    /** Adds caller-supplied metadata to any DataAI function result DataFrame. */
    public static Dataset<Row> withRunMetadata(
            Dataset<Row> output,
            String resultName,
            String runId,
            Instant completedAt,
            String libraryVersion) {
        Objects.requireNonNull(output, "output");
        requireText(resultName, "resultName");
        requireText(runId, "runId");
        Objects.requireNonNull(completedAt, "completedAt");
        requireText(libraryVersion, "libraryVersion");
        ensureNoMetadataCollision(output);

        return output
                .withColumn(RESULT_NAME, lit(resultName))
                .withColumn(RUN_ID, lit(runId))
                .withColumn(COMPLETED_AT, lit(Timestamp.from(completedAt)))
                .withColumn(LIBRARY_VERSION, lit(libraryVersion));
    }

    /**
     * Converts matrix-balancing cells to a Tableau result and preserves
     * convergence metadata on every cell for filtering and audit display.
     */
    public static Dataset<Row> matrixBalance(
            MatrixBalanceResult balance,
            String runId,
            Instant completedAt,
            String libraryVersion) {
        Objects.requireNonNull(balance, "balance");
        return withRunMetadata(
                balance.balancedCells(),
                "matrix_balance",
                runId,
                completedAt,
                libraryVersion)
                .withColumn("balance_iterations", lit(balance.iterations()))
                .withColumn("balance_maximum_error", lit(balance.maximumError()))
                .withColumn("balance_converged", lit(balance.converged()));
    }

    private static void ensureNoMetadataCollision(Dataset<Row> output) {
        List<String> columns = Arrays.asList(output.columns());
        for (String metadataColumn : METADATA_COLUMNS) {
            if (columns.contains(metadataColumn)) {
                throw new IllegalArgumentException(
                        "Output already contains reserved Tableau metadata column: " + metadataColumn);
            }
        }
    }

    private static void requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " cannot be blank.");
        }
    }
}
