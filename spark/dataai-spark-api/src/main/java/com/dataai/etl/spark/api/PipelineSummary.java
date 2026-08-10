package com.dataai.etl.spark.api;

import java.time.Instant;

public record PipelineSummary(
        String runId,
        Instant startedAt,
        Instant completedAt,
        String status,
        long rowsRead,
        long rowsAccepted,
        long rowsRejected,
        double qualityScore,
        String libraryVersion) {
}

