package com.dataai.etl.spark.tableau;

/** Stable default names for DataAI outputs exposed to Tableau. */
public final class TableauOutputNames {
    public static final String CLEAN_ROWS = "dataai_clean_rows";
    public static final String REJECTED_ROWS = "dataai_rejected_rows";
    public static final String QUALITY_FINDINGS = "dataai_quality_findings";
    public static final String FIELD_PROFILES = "dataai_field_profiles";
    public static final String PIPELINE_RUNS = "dataai_pipeline_runs";
    public static final String DASHBOARD_METRICS = "dataai_dashboard_metrics";

    private TableauOutputNames() {
    }
}
