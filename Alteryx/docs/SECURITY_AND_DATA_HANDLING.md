# Security and Data Handling

## Trust boundary

The Designer tool, the DataAI JAR, `spark-submit`, Spark compute, catalogs,
credentials, logs, and generated tables all remain in customer-controlled
systems. The adapter has no Yanbor-hosted execution path.

## Process execution

The adapter accepts only an executable named `spark-submit`,
`spark-submit.cmd`, `spark-submit.bat`, or `spark-submit.exe`. It supplies a
Python argument list with `shell=False`; it does not concatenate or evaluate a
shell command. The DataAI main class cannot be overridden through the advanced
arguments field.

## Temporary files

A temporary UTF-8 JSON job configuration is written under the operating
system's temporary directory immediately before execution. It contains table
names, rule definitions, and quality settings, but should not contain
credentials. Python removes its private temporary directory after completion,
failure, or timeout.

## Output behavior

Every nonblank Clean, Rejected, Profile, or Findings table is written in Delta
format with `Overwrite` and `overwriteSchema=true`. This behavior is visible in
the UI, license acceptance text, usage guide, and listing. Blank output values
skip that write.

## Logs and network

The tool captures the child process output only while the process is running
and does not write or return raw Spark logs. The status record contains only a
generic result. Spark or connector networking is controlled by customer Spark
configuration. The adapter implements no telemetry, analytics beacon, update
check, remote license check, or required network call to Yanbor LLC.

## Credentials

Do not put credentials in tool configuration, rules JSON, table names, or
extra arguments. Use the customer's service identity, Spark configuration,
credential provider, secret store, and Alteryx deployment policy.

## Customer validation

Before production licensing, test with representative non-sensitive data,
review the YXI and JAR hashes, scan dependencies, confirm least privilege,
verify table targets, exercise failure and timeout paths, and validate the same
version in Designer and Server environments that will execute it.
