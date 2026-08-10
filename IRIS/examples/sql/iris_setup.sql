-- Fictional evaluation schema. Review types, privileges, and retention with
-- the customer's IRIS administrator before use.

CREATE SCHEMA DataAI;

CREATE TABLE DataAI.PipelineRuns (
    run_id VARCHAR(80) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    status VARCHAR(40) NOT NULL,
    rows_read BIGINT NOT NULL,
    rows_accepted BIGINT NOT NULL,
    rows_rejected BIGINT NOT NULL,
    quality_score DOUBLE NOT NULL,
    library_version VARCHAR(40) NOT NULL,
    platform VARCHAR(40) NOT NULL,
    PRIMARY KEY (run_id)
);

CREATE TABLE DataAI.QualityFindings (
    record_key VARCHAR(128),
    rule_id VARCHAR(120),
    field_name VARCHAR(240),
    severity VARCHAR(20),
    finding_code VARCHAR(120),
    message VARCHAR(2000),
    original_value VARCHAR(4000),
    normalized_value VARCHAR(4000),
    _dataai_result_name VARCHAR(80) NOT NULL,
    _dataai_run_id VARCHAR(80) NOT NULL,
    _dataai_completed_at TIMESTAMP NOT NULL,
    _dataai_library_version VARCHAR(40) NOT NULL,
    _dataai_platform VARCHAR(40) NOT NULL
);

CREATE TABLE DataAI.FieldProfiles (
    field_name VARCHAR(240) NOT NULL,
    source_type VARCHAR(80),
    record_count BIGINT,
    null_count BIGINT,
    distinct_count BIGINT,
    minimum_value VARCHAR(4000),
    maximum_value VARCHAR(4000),
    mean_value DOUBLE,
    standard_deviation DOUBLE,
    _dataai_result_name VARCHAR(80) NOT NULL,
    _dataai_run_id VARCHAR(80) NOT NULL,
    _dataai_completed_at TIMESTAMP NOT NULL,
    _dataai_library_version VARCHAR(40) NOT NULL,
    _dataai_platform VARCHAR(40) NOT NULL
);

CREATE INDEX QualityFindingsRun ON DataAI.QualityFindings (_dataai_run_id);
CREATE INDEX QualityFindingsSeverity ON DataAI.QualityFindings (severity);
CREATE INDEX FieldProfilesRun ON DataAI.FieldProfiles (_dataai_run_id);
