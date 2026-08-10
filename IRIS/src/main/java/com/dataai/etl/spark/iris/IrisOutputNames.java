package com.dataai.etl.spark.iris;

/** Stable suggested IRIS SQL table names for DataAI results. */
public final class IrisOutputNames {
    public static final String CLEAN_ROWS = "DataAI.CleanRows";
    public static final String REJECTED_ROWS = "DataAI.RejectedRows";
    public static final String QUALITY_FINDINGS = "DataAI.QualityFindings";
    public static final String FIELD_PROFILES = "DataAI.FieldProfiles";
    public static final String PIPELINE_RUNS = "DataAI.PipelineRuns";
    public static final String MATRIX_BALANCE = "DataAI.MatrixBalance";

    private IrisOutputNames() {
    }
}
