package com.dataai.etl.spark.iris;

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

/** Adds stable audit metadata to any DataAI function result for IRIS storage. */
public final class IrisFunctionOutputs {
    public static final String RESULT_NAME = "_dataai_result_name";
    public static final String RUN_ID = "_dataai_run_id";
    public static final String COMPLETED_AT = "_dataai_completed_at";
    public static final String LIBRARY_VERSION = "_dataai_library_version";
    public static final String PLATFORM = "_dataai_platform";

    private static final List<String> RESERVED_COLUMNS = List.of(
            RESULT_NAME, RUN_ID, COMPLETED_AT, LIBRARY_VERSION, PLATFORM);

    private IrisFunctionOutputs() {
    }

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
        ensureNoCollision(output);
        return output
                .withColumn(RESULT_NAME, lit(resultName))
                .withColumn(RUN_ID, lit(runId))
                .withColumn(COMPLETED_AT, lit(Timestamp.from(completedAt)))
                .withColumn(LIBRARY_VERSION, lit(libraryVersion))
                .withColumn(PLATFORM, lit("INTERSYSTEMS_IRIS"));
    }

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

    private static void ensureNoCollision(Dataset<Row> output) {
        List<String> columns = Arrays.asList(output.columns());
        for (String reserved : RESERVED_COLUMNS) {
            if (columns.contains(reserved)) {
                throw new IllegalArgumentException(
                        "Output already contains reserved IRIS metadata column: " + reserved);
            }
        }
    }

    private static void requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " cannot be blank.");
        }
    }
}
