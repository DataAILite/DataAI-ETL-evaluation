# DataAI ETL Work Rules

This file is a permanent local reminder for future work in
`C:\Projects\DataAI.Etl`.

## Working Rules

- Work only in `C:\Projects\DataAI.Etl` unless explicit permission is given
  for another folder.
- Explain the plan before changing files and wait for approval.
- Change only the files approved in the plan.
- Preserve unrelated or pre-existing customer changes.
- Normalize touched text and source files to CRLF to avoid Windows and IDE
  inconsistent line-ending warnings.
- Use the Maven module structure, Java style, naming conventions, and public
  API patterns already established in this repository.
- Tell the user when work is done so it can be checked.
- Keep a separate `DataAIetl_WORK_HISTORY.md` file and update it every day that
  DataAI ETL work is performed.

## Product Boundary Rules

- DataAI ETL is an embeddable library that runs inside the customer's pipeline.
  Do not turn it into a required hosted service.
- Do not add required network calls, external telemetry, remote license checks,
  or transmission of customer data without explicit approval.
- Keep customer control over input DataFrames, output formats, table names,
  save modes, partitioning, catalogs, scheduling, orchestration, and security.
- Keep UI rendering, dashboards, report delivery, identity, and scheduling out
  of the computational library unless an explicitly approved adapter requires
  them.
- Prefer reusable Spark transformations over behavior tied to Oracle AIDP,
  Power BI, Tableau, or another single platform.
- Platform-specific behavior belongs in examples or adapters and must not make
  the core library dependent on that platform.
- Do not add or change the commercial, evaluation, or open-source license
  without explicit approval.

## Runtime Compatibility Rules

- The current baseline is Java 17, Apache Spark 3.5.0, and Scala binary version
  2.12.
- Keep Jackson on a Spark-compatible 2.15.x line unless a tested Spark runtime
  upgrade requires another version.
- Keep Spark and Hadoop dependencies in `provided` scope. Customer clusters
  supply those runtimes; do not bundle them into customer artifacts.
- Preserve compatibility with the existing shaded CLI JAR and the unshaded
  Maven library artifacts.
- Treat a Spark, Java, Scala, Jackson, Delta, or Maven baseline change as a
  compatibility change that requires explicit documentation and full tests.
- Do not install Java, Maven, Spark, or other build tools globally. If portable
  verification tools are needed, keep them under `.tools/` and local Maven
  artifacts under `.m2/`; both must remain ignored.

## Module Boundary Rules

- `dataai-spark-api` contains stable public contracts and must not depend on
  implementation modules.
- `dataai-spark-quality` contains declarative quality evaluation and depends on
  the public API.
- `dataai-spark-core` contains normalization, profiling, record keys, pipeline
  execution, and result routing.
- `dataai-spark-functions` contains reusable analytics, time-series, business,
  market, geographic, matrix, quality-diagnostic, recommendation, alert, and
  narrative functions.
- `dataai-spark-testkit` contains shared Spark testing support and must not
  become a production runtime dependency.
- `dataai-spark-cli` is the configuration-driven entry point and shaded
  distribution artifact. It may compose library modules but must not own core
  analytical algorithms.
- `Tableau/` contains the optional Tableau output adapter, fictional evaluation
  data, Accelerator/Hyper artifacts, and marketplace preparation assets. The
  Spark API, quality, core, functions, and CLI modules must not depend on it.
- `IRIS/` contains the optional InterSystems IRIS JDBC adapter, fictional
  evaluation data, Open Exchange assets, and optional IRIS-native IPM bootstrap.
  It may depend on the public functions artifact; Spark API, quality, core,
  functions, CLI, and Tableau modules must not depend on it. It must not bundle
  the InterSystems JDBC driver or make automatic customer-data writes.
- `SparkETL/` contains generated Spark marketplace-review and evaluation
  artifacts. It may copy verified Spark source, documentation, POMs, and JARs
  for distribution but must not become a Maven reactor dependency or own the
  canonical implementation.
- `Databricks/` contains the optional Databricks Marketplace provider package,
  Unity Catalog delivery templates, notebooks, fictional evaluation data,
  documentation, and generated distribution artifacts. It may copy verified
  Spark JARs but must not become a Maven reactor dependency, own canonical
  functions, require a hosted DataAI service, or write customer data unless an
  example explicitly enables a customer-selected destination.
- `AWS/`, `Microsoft/`, `Oracle/`, and `Google/` contain optional cloud-
  marketplace review and packaging artifacts. They may include customer-run
  container or deployment candidates, but must not turn DataAI into a hosted
  service, become Maven reactor dependencies, own canonical functions, bundle
  Spark/Hadoop classes, or claim submission readiness before immutable release,
  partner, security, runtime, and marketplace-specific gates pass.
- `Maven/` contains Maven Central pre-publication and repository-layout
  artifacts. It must remain blocked from publication while versions end in
  `SNAPSHOT`, namespace ownership is unverified, required POM metadata or PGP
  signatures are incomplete, or public permanent distribution is unauthorized.
- Runtime-neutral contracts, schemas, and golden fixtures belong in
  `specification/`.
- Platform-specific samples belong in `examples/`.

## Spark Function Rules

- Public computational functions should accept `Dataset<Row>` inputs and
  return DataFrames or small result records containing DataFrames.
- Preserve lazy Spark execution unless an action is necessary for a documented
  reason, such as correlation calculation or matrix-convergence testing.
- Do not collect unbounded customer records to the driver.
- Driver-side collections must be bounded to schemas, field lists, small model
  metadata, or explicitly documented result summaries.
- Validate referenced field names and required parameters early with clear
  error messages.
- Handle nulls, empty inputs, zero denominators, invalid casts, and duplicate
  normalized field names deliberately.
- Use deterministic calculations, stable output column names, and explicit
  record keys where results must be related to source rows.
- Avoid hidden writes. The embedded API should return results and let the
  customer choose how to persist them.
- When an API performs iterative Spark actions, expose iteration limits,
  tolerance, convergence status, and error metrics.
- New public functions must be added to `docs/FUNCTION_CATALOG.md` with their
  inputs, outputs, execution behavior, and limitations.

## Quality and Data-Safety Rules

- Quality findings must remain traceable to rule ID, field, severity, finding
  code, message, and source record key where applicable.
- Adding a new `RuleType` requires a public `RuleSpec` factory where practical,
  evaluator support, JSON compatibility consideration, documentation, and an
  execution test.
- Do not silently change whether a finding rejects a record or how quality
  scores are calculated.
- Document any change to severity semantics, score formulas, record routing,
  normalization, or record-key generation as a behavioral compatibility
  change.
- Do not log source records, credentials, secrets, connection strings, or
  customer configuration values.
- Never include production customer data in tests, examples, documentation, or
  generated artifacts.

## Build and Test Rules

- Run Maven commands from `C:\Projects\DataAI.Etl\spark`.
- Before handing off code changes, run the complete reactor:

  ```powershell
  mvn clean verify
  ```

- If Maven is not installed globally, use the ignored portable Maven and JDK
  under `.tools/` with the ignored local repository under `.m2/`.
- A successful compile is not sufficient for Spark transformations. Run real
  Spark execution tests for new or changed functions.
- Add focused tests for normal behavior and material edge cases, especially
  nulls, empty inputs, invalid field names, zero denominators, thresholds,
  convergence, and output schemas.
- Keep tests deterministic, self-contained, and independent of customer
  databases, network services, Oracle AIDP, Delta catalogs, or credentials.
- The local Windows `winutils.exe` warning is acceptable only when the full
  Maven build and tests finish successfully.
- Rebuild the shaded CLI artifact after changes to any packaged module and
  verify that Spark and Hadoop classes are not bundled.

## Documentation Rules

- Update `README.md` when repository structure, supported runtimes, or major
  product behavior changes.
- Update `spark/README.md` when build commands, Maven coordinates, module use,
  or CLI behavior changes.
- Update `docs/INSTALLATION_AND_USAGE.md` when installation, configuration,
  deployment, output, or troubleshooting behavior changes.
- Update `docs/FUNCTION_CATALOG.md` for every public function or rule addition,
  removal, rename, or semantic change.
- Keep examples executable against the documented runtime and use fictional,
  non-sensitive data.
- State whether an example is generic Spark, Oracle AIDP-specific, or intended
  for another platform.
- Do not claim an integration was tested on an external platform unless that
  integration was actually executed there.

## Distribution and Versioning Rules

- Use immutable release versions for customer distribution. Do not present a
  `SNAPSHOT` artifact as a production release.
- Keep group ID, artifact ID, version, Java baseline, Spark baseline, Scala
  binary version, and dependency scopes visible in release documentation.
- Publish library modules to an approved authenticated Maven repository and
  provide the shaded CLI JAR only when the configuration-driven entry point is
  needed.
- Produce and verify SHA-256 checksums for customer-delivered binaries.
- Do not publish, upload, push, tag, or release artifacts without explicit
  approval.
- Preserve backward compatibility for public APIs and output schemas within a
  released version line, or document and version breaking changes explicitly.

## Commit Rules

- Commit only when requested.
- Do not initialize a Git repository, create a branch, push, tag, publish a
  release, or open a pull request unless explicitly requested.
- Do not commit `.tools/`, `.m2/`, `target/`, IDE metadata, logs, temporary
  files, Spark warehouse data, or generated test output.
- Do not commit credentials, tokens, connection strings, private repository
  passwords, customer table names, or customer data.
- Do not commit generated JARs unless explicitly approved for that commit.
- Do not commit license or entitlement files unless explicitly approved.
- Do not commit `DataAIetl_WORK_RULES.md` unless explicitly requested.
- Do not commit `DataAIetl_WORK_HISTORY.md` unless explicitly requested.
- Exclude temporary/generated folders and helper scripts unless explicitly
  approved.
