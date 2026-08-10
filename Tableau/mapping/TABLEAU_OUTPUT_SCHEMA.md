# Tableau Output Contract

`TableauOutputs.from(DataAiResult)` returns a `TableauOutputBundle`. The
adapter does not write these DataFrames. Persist only the outputs needed by the
customer and use governed table/view names if they differ from the defaults.

## Standard outputs

| Bundle method | Default table constant | Grain | Tableau use |
| --- | --- | --- | --- |
| `cleanRows()` | `dataai_clean_rows` | One accepted source record | Governed analysis and record drill-through |
| `rejectedRows()` | `dataai_rejected_rows` | One rejected source record | Remediation workflow |
| `qualityFindings()` | `dataai_quality_findings` | One rule finding | Severity/rule/field analysis |
| `fieldProfiles()` | `dataai_field_profiles` | One field profile for the current run | Completeness and distribution analysis |
| `pipelineRuns()` | `dataai_pipeline_runs` | One pipeline execution | Audit and run history |
| `dashboardMetrics()` | `dataai_dashboard_metrics` | One pipeline execution | Fast Tableau overview |

The default names are constants in `TableauOutputNames`. They do not force a
catalog, schema, storage format, or write mode.

## `dataai_dashboard_metrics`

| Field | Spark type | Nullable | Meaning |
| --- | --- | --- | --- |
| `run_id` | string | No | DataAI pipeline run identifier |
| `completed_at` | timestamp | No | Pipeline completion time |
| `status` | string | No | Pipeline status |
| `rows_read` | long | No | Input records evaluated |
| `rows_accepted` | long | No | Records without findings |
| `rows_rejected` | long | No | Records with at least one finding |
| `quality_score` | double | No | Accepted records / read records * 100 |
| `critical_findings` | long | No | CRITICAL finding count |
| `error_findings` | long | No | ERROR finding count |
| `warning_findings` | long | No | WARNING finding count |
| `info_findings` | long | No | INFO finding count |
| `fields_profiled` | long | No | Profile rows produced |
| `total_null_values` | long | No | Sum of profile `null_count` values |

## `dataai_pipeline_runs`

| Field | Spark type | Nullable |
| --- | --- | --- |
| `run_id` | string | No |
| `started_at` | timestamp | No |
| `completed_at` | timestamp | No |
| `status` | string | No |
| `rows_read` | long | No |
| `rows_accepted` | long | No |
| `rows_rejected` | long | No |
| `quality_score` | double | No |
| `library_version` | string | No |

## `dataai_quality_findings`

The base DataAI findings schema is:

`record_key`, `rule_id`, `field_name`, `severity`, `finding_code`, `message`,
`original_value`, `normalized_value`.

For multi-run Tableau history, add the current `run_id` before appending:

```java
Dataset<Row> findingsForHistory = tableau.qualityFindings()
        .withColumn("run_id", lit(result.summary().runId()));
```

## `dataai_field_profiles`

The base profile schema is:

`field_name`, `source_type`, `record_count`, `null_count`, `distinct_count`,
`minimum_value`, `maximum_value`, `mean_value`, `standard_deviation`.

For multi-run Tableau history, add `run_id` in the same way before append.

## Recommended Tableau model

- Use `dataai_dashboard_metrics` alone for the overview Accelerator.
- Relate `dataai_pipeline_runs` (one) to `dataai_quality_findings` (many) by
  `run_id` for finding details.
- Relate `dataai_pipeline_runs` (one) to `dataai_field_profiles` (many) by
  `run_id` for completeness details.
- Relate findings to clean/rejected source rows by `record_key` only when the
  customer authorizes record-level BI access.
- Keep row-level security and data-source credentials in Tableau or the
  underlying platform; DataAI does not manage Tableau identities.
