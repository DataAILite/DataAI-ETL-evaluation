-- Example Spark SQL/Databricks views. Replace catalog and schema names with
-- customer-governed values. These views do not move data outside the platform.

CREATE OR REPLACE VIEW analytics.tableau_dataai_run_overview AS
SELECT
    run_id,
    completed_at,
    status,
    rows_read,
    rows_accepted,
    rows_rejected,
    quality_score,
    critical_findings,
    error_findings,
    warning_findings,
    info_findings,
    fields_profiled,
    total_null_values
FROM analytics.dataai_dashboard_metrics;

CREATE OR REPLACE VIEW analytics.tableau_dataai_finding_detail AS
SELECT
    run_id,
    record_key,
    rule_id,
    field_name,
    severity,
    finding_code,
    message,
    original_value,
    normalized_value
FROM analytics.dataai_quality_findings;

CREATE OR REPLACE VIEW analytics.tableau_dataai_field_profile AS
SELECT
    run_id,
    field_name,
    source_type,
    record_count,
    null_count,
    distinct_count,
    minimum_value,
    maximum_value,
    mean_value,
    standard_deviation
FROM analytics.dataai_field_profiles;
