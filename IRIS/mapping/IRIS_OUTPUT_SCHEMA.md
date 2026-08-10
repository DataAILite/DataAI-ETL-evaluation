# IRIS Output Contract

## Pipeline tables

| Bundle method | Suggested IRIS table | Grain |
| --- | --- | --- |
| `cleanRows()` | `DataAI.CleanRows` | Accepted source record |
| `rejectedRows()` | `DataAI.RejectedRows` | Rejected source record |
| `qualityFindings()` | `DataAI.QualityFindings` | Rule finding |
| `fieldProfiles()` | `DataAI.FieldProfiles` | Profiled field per run |
| `pipelineRuns()` | `DataAI.PipelineRuns` | Pipeline execution |

Clean and rejected tables retain customer source fields, so customers must
define them from the approved source schema rather than use one universal DDL.

## Audit columns added to result DataFrames

| Column | Spark type | Meaning |
| --- | --- | --- |
| `_dataai_result_name` | string | Stable function-result name |
| `_dataai_run_id` | string | Run identifier |
| `_dataai_completed_at` | timestamp | Completion instant |
| `_dataai_library_version` | string | DataAI version |
| `_dataai_platform` | string | `INTERSYSTEMS_IRIS` |

The adapter rejects an input that already contains a reserved audit name
instead of overwriting customer data.

## Pipeline run columns

`run_id`, `started_at`, `completed_at`, `status`, `rows_read`,
`rows_accepted`, `rows_rejected`, `quality_score`, `library_version`, and
`platform`.

## Matrix balancing

`IrisFunctionOutputs.matrixBalance(...)` retains the balanced-cell schema and
adds `balance_iterations`, `balance_maximum_error`, and `balance_converged`.

## Type and identifier notes

- Test Spark `decimal`, timestamp, date, binary, and long-string mappings with
  the selected IRIS JDBC driver.
- IRIS namespaces are part of the JDBC URL; SQL schemas are part of table
  names. Do not treat them as interchangeable.
- Use explicit schemas and restricted identities.
- Review identifier quoting and case with existing IRIS persistent classes.
- Use staging and merge procedures when retries could duplicate appended rows.
