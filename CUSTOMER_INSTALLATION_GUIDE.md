# DataAI ETL Customer Installation Guide

**Provider:** Yanbor LLC, provider of the DataAI product  
**Guide date:** August 9, 2026  
**Purpose:** Installation and first-use instructions for each DataAI ETL
distribution format.

## Read this first

The packages audited with this guide contain `0.1.0-SNAPSHOT` or
`0.1.0-evaluation.1` development artifacts. They are for controlled evaluation,
not production deployment. Production customers must receive an immutable
licensed version through the channel stated in their signed agreement or order
form.

DataAI ETL is an embedded customer-side library. It does not require a Yanbor
hosted service, transmit customer data to Yanbor, or choose where results are
stored. The customer controls Spark compute, identity, catalogs, table names,
formats, save modes, partitions, schedules, and permissions.

Unless a platform section states otherwise, the runtime baseline is:

- Java 17;
- Apache Spark 3.5.x;
- Scala binary version 2.12;
- customer-controlled compute, identity, catalog, and storage;
- Delta Lake/catalog support when using the supplied configuration-driven CLI.

## Common download and verification steps

1. Obtain the package only from Yanbor LLC, the approved marketplace listing,
   or the customer artifact repository named in the agreement.
2. Obtain its `.sha256` file through the approved channel.
3. In PowerShell, calculate the downloaded ZIP hash:

   ```powershell
   Get-FileHash .\<downloaded-file>.zip -Algorithm SHA256
   ```

4. Compare the hexadecimal value exactly with the sidecar. Stop if it differs.
5. Extract the ZIP into a new evaluation directory. Do not extract it over a
   prior version.
6. Read `LICENSE.md`, `THIRD_PARTY_NOTICES.md`, the package `README.md`, and the
   executed commercial agreement if one exists.
7. Confirm that every DataAI module has the same version. Never mix modules
   from different DataAI releases.
8. Use non-production data, schemas, identities, and compute for the evaluation.
9. Do not place credentials in a DataAI JSON file, notebook, JAR, workflow, ZIP,
   or command line. Use the platform's secret manager and workload identity.

## Which file should a customer use?

| Channel | Customer acquisition or installation artifact |
| --- | --- |
| Generic Spark | Maven modules from an authenticated repository or `SparkETL.zip` controlled evaluation payload |
| Databricks | Provider-approved Marketplace files/notebooks or controlled `DataAI_ETL_Databricks_Evaluation.zip` |
| AWS | Approved Marketplace image; controlled evaluation may use JARs from `DataAIETLAWS.zip` |
| Microsoft | Approved Marketplace plan if published; controlled evaluation may use JARs from `DataAIETLMicrosoft.zip` |
| Oracle | Approved OCI listing/fulfillment; controlled evaluation may use JARs from `DataAIETLOracle.zip` |
| Google | Approved Marketplace image; controlled evaluation may use JARs from `DataAIETLGoogle.zip` |
| Maven | Private Maven coordinates; Maven Central coordinates only after public release |
| NuGet | `Yanbor.DataAI.Etl.Spark` plus its `Yanbor.DataAI.Etl.Spark.Runtime` dependency |
| Tableau | `DataAI_ETL_Accelerator.twbx` plus licensed DataAI Spark outputs |
| InterSystems IRIS | `dataai-spark-iris` adapter, core DataAI modules, and customer-approved InterSystems JDBC driver |
| Alteryx | `DataAI_ETL_Alteryx_2026_1_Evaluation.yxi` |

The root `DataAIETL*.zip` files are generally provider/reviewer kits. Customers
should receive the internal evaluation artifact or marketplace fulfillment
identified above, not provider secrets, test evidence, or partner credentials.

## 1. Generic Spark ETL

### Option A: Install as Maven libraries

1. Obtain the authenticated repository URL, read-only credentials, group ID,
   and immutable version from Yanbor or the customer artifact administrator.
2. Add the repository to the customer's Maven `settings.xml` or approved build
   repository configuration. Put the password/token in the build secret store.
3. Add the functions dependency to the Spark application's `pom.xml`; it brings
   API, quality, and core transitively:

   ```xml
   <dependency>
     <groupId>com.dataai</groupId>
     <artifactId>dataai-spark-functions</artifactId>
     <version>0.1.0-SNAPSHOT</version>
   </dependency>
   ```

4. Compile against the customer Spark runtime and keep Spark provided:

   ```xml
   <dependency>
     <groupId>org.apache.spark</groupId>
     <artifactId>spark-sql_2.12</artifactId>
     <version>3.5.0</version>
     <scope>provided</scope>
   </dependency>
   ```

5. Build in a clean environment and confirm that one version of each DataAI
   module resolves.
6. Add the application JAR and DataAI dependencies through the cluster's normal
   library mechanism.
7. Run a non-production pipeline and verify clean rows, rejected rows,
   findings, profiles, run summary, and any selected analytical outputs.

For production, replace the displayed evaluation version with the exact
immutable version supplied to the customer. Do not guess coordinates.

### Option B: Run the configuration-driven CLI

1. Obtain the shaded `dataai-spark-cli-<version>.jar`. Do not use a file whose
   name begins with `original-`.
2. Create source and separate evaluation output schemas/tables in a Spark
   catalog with Delta support.
3. Copy an example JSON configuration and set `sourceTable`, optional output
   tables, normalization, record keys, rules, and optional minimum score.
4. Run locally or in client mode:

   ```powershell
   spark-submit `
     --class com.dataai.etl.spark.cli.DataAiJob `
     .\dataai-spark-cli-0.1.0-SNAPSHOT.jar `
     --config .\customer-orders.json
   ```

5. In cluster deploy mode, distribute the configuration to the driver:

   ```shell
   spark-submit \
     --class com.dataai.etl.spark.cli.DataAiJob \
     --files customer-orders.json \
     dataai-spark-cli-0.1.0-SNAPSHOT.jar \
     --config customer-orders.json
   ```

6. Query every configured output table and verify `_dataai_record_key`, quality
   findings, profiles, routing, row counts, and the minimum-score behavior.
7. Note that the current CLI writes named output tables in overwrite mode. Use
   dedicated evaluation tables.

The full API and CLI guide is `docs\INSTALLATION_AND_USAGE.md`; the complete
function list, including matrix balancing, is `docs\FUNCTION_CATALOG.md`.

## 2. Databricks

1. Use a Unity Catalog-enabled workspace and an approved Java 17/Spark
   3.5.x/Scala 2.12 compute image. Databricks Runtime 16.4 LTS with Scala 2.12 is
   the initial validation target in the current kit, not a general support
   guarantee.
2. Create a customer-controlled catalog, schema, and volume. Grant the job
   identity `USE CATALOG`, `USE SCHEMA`, `READ VOLUME`, and only the output
   privileges the customer approves.
3. Accept/request the Marketplace listing, or extract the controlled evaluation
   package supplied by Yanbor.
4. Upload `lib`, `data`, and `docs` to a governed volume. Example:

   ```powershell
   databricks fs mkdir dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl
   databricks fs cp .\lib dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl/lib -r --overwrite
   databricks fs cp .\data dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl/data -r --overwrite
   databricks fs cp .\docs dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl/docs -r --overwrite
   ```

5. On the compute resource, open **Libraries > Install new**, choose the Unity
   Catalog volume source, and install the same-version API, quality, core, and
   functions JARs. Add the path to the standard-access-mode allowlist if the
   administrator requires it.
6. Restart compute after installing the libraries.
7. Import the `notebooks` directory into a customer-controlled workspace
   folder and set `dataai_base_path` to the uploaded volume path.
8. Run notebooks in this order:

   1. `00_INSTALL_AND_VERIFY.py`
   2. `01_QUALITY_PIPELINE.py`
   3. `02_ANALYTICS_AND_MARKET.py`
   4. `03_MATRIX_BALANCING.py`
   5. `04_PUBLISH_FOR_BI.py`

9. Leave `persist_results` and `publish_views` false until the output catalog,
   schema, table names, grants, and retention have been approved.
10. Verify runtime versions, class loading, quality routing, matrix convergence,
    and the optional governed views.
11. Pin the exact immutable library version in Jobs and cluster policies for
    any licensed production deployment.

## 3. AWS / Amazon EMR

### Marketplace image after publication

1. Sign in to the approved buyer account, open the DataAI ETL AWS Marketplace
   listing, review the EULA and pricing, and subscribe.
2. Select the supported region and immutable product version.
3. Follow the listing's IAM instructions so the EMR Serverless service and job
   roles can use the Marketplace-managed image and customer S3 locations.
4. Create or update an EMR Serverless Spark application using the subscribed
   custom image and the documented compatible runtime.
5. Store the customer's application JAR, optional CLI configuration, and input
   data in customer-controlled S3 locations.
6. Start the Spark job with the application entry point. The image places
   DataAI libraries in its documented Spark library paths; do not download a
   second, mismatched DataAI version.
7. Inspect CloudWatch/EMR logs and customer-controlled output tables or paths.
8. Validate an intentionally failing quality rule and matrix control totals
   before enabling a production schedule.

### Controlled evaluation before Marketplace publication

1. Extract the approved evaluation payload from `DataAIETLAWS.zip`.
2. Upload the matching API, quality, core, and functions JARs from `lib` to a
   private S3 artifact prefix.
3. Add those URIs using the EMR release's supported `--jars` or application
   dependency configuration. Use the optional shaded CLI only for JSON-driven
   jobs.
4. Run on isolated EMR compute and validate the same outputs as generic Spark.

Do not treat `DataAIETLAWS.zip` or its `SNAPSHOT` image inputs as a production
Marketplace product.

## 4. Microsoft Azure

The current Microsoft kit is not a finished deployable Marketplace plan. Use
one of these procedures only after Yanbor identifies the approved fulfillment
model.

### Approved Marketplace plan

1. In Azure Marketplace, review and acquire the DataAI ETL offer and its plan.
2. Select the documented subscription, resource group, region, immutable
   version, and customer-managed identity.
3. If the plan is an AKS application, deploy it with the Marketplace wizard and
   verify that all created resources remain in the customer tenant.
4. Follow the plan's technical instructions to make the DataAI JARs available
   to the customer's compatible Spark compute.
5. Run the supplied verification job and inspect only customer-controlled
   logs, storage, and catalogs.
6. Test upgrade and uninstall in non-production before approval.

### Controlled JAR evaluation

1. Extract the evaluation payload from `DataAIETLMicrosoft.zip`.
2. Copy the matching JARs from `lib` to an approved private Azure Storage/ADLS
   or artifact repository.
3. Attach all four JARs to the customer's Java 17/Spark 3.5.x/Scala 2.12 job
   using that Spark platform's supported library or `--jars` mechanism.
4. Run the generic quality or embedded-API example and verify outputs.

The included component Dockerfile is for provider architecture review. A
customer should not deploy it as though it were a completed Marketplace
application.

## 5. Oracle Cloud / OCI Data Flow

1. Acquire the approved OCI Marketplace listing or receive the controlled
   evaluation package from Yanbor.
2. Create a private Object Storage bucket/prefix for licensed artifacts and a
   separate location for the customer's application and configuration.
3. Upload the same-version API, quality, core, and functions JARs. Upload the
   shaded CLI only if using the JSON-driven job.
4. Grant the OCI Data Flow run identity read access to those objects and only
   the catalog/storage permissions required for the chosen inputs and outputs.
5. Create a Java 17/Spark 3.5-compatible Data Flow application and list the
   DataAI JAR Object Storage URIs as application dependencies.
6. For the CLI, set main class
   `com.dataai.etl.spark.cli.DataAiJob`, distribute the JSON file, and pass
   `--config <localized-file>`.
7. For an embedded application, call `DataAiPipeline` or functions from the
   customer's application JAR.
8. Run with isolated schemas, inspect Data Flow logs, query every output, and
   verify that no unselected table was written.
9. Test the exact OCI Data Flow image and dependencies again before licensed
   production scheduling.

The container in the provider kit is an artifact carrier candidate; OCI Data
Flow normally consumes the licensed JARs from customer-controlled Object
Storage as documented by the approved offer.

## 6. Google Cloud / Dataproc

1. Acquire the approved Google Cloud Marketplace image or receive the
   controlled evaluation package from Yanbor.
2. Create a private Cloud Storage prefix for DataAI artifacts and upload the
   same-version API, quality, core, and functions JARs.
3. Grant the Dataproc service account read access to the artifact prefix and
   only approved input/output permissions.
4. Create a Java 17/Spark 3.5-compatible Dataproc cluster or Serverless batch.
5. Submit the customer Spark job and provide all DataAI JAR URIs using the
   Dataproc `--jars` option. For the CLI, use
   `com.dataai.etl.spark.cli.DataAiJob` and distribute the JSON configuration.
6. Inspect Cloud Logging and customer-controlled BigQuery, catalog, or Cloud
   Storage outputs selected by the application.
7. Verify quality routing, analytical outputs, matrix convergence, and failure
   behavior before creating a production workflow.

If the Marketplace image is used as the licensed artifact carrier, follow its
documented extraction/copy step and do not mix those JARs with the evaluation
ZIP.

## 7. Maven repository installation

### Private repository (recommended for commercial customers)

1. Ask the customer administrator to add the Yanbor repository URL and server
   ID to the organization's Maven configuration.
2. Store the issued read-only token in the build secret manager, not in source
   control.
3. Add `com.dataai:dataai-spark-functions:<licensed-version>` to the customer
   application; add the Tableau or IRIS adapter only when needed.
4. Confirm Spark SQL 2.12 is supplied by the customer runtime in `provided`
   scope.
5. Run `mvn dependency:tree` and confirm all DataAI modules resolve at one exact
   version.
6. Build and run the application on a qualified non-production cluster.

### Maven Central after an authorized public release

1. Remove any private repository entry that masks Central.
2. Add the exact published coordinate and immutable version to the POM.
3. Resolve it from an empty Maven cache and inspect the PGP/signature and
   checksum evidence supplied in the release notes.
4. Run the same compatibility and output checks as the private-repository path.

The present `DataAIETLMaven.zip` is a prepublication review layout, not a
customer Central installation bundle.

## 8. NuGet for .NET orchestration

1. Install .NET 8, Java 17, and a Spark 3.5/Scala 2.12 runtime.
2. Add the approved private feed:

   ```powershell
   dotnet nuget add source "<PRIVATE-FEED-URL>" --name DataAI
   ```

3. Add the helper package:

   ```powershell
   dotnet add package Yanbor.DataAI.Etl.Spark `
     --version 0.1.0-evaluation.1 `
     --source DataAI
   ```

4. The helper restores `Yanbor.DataAI.Etl.Spark.Runtime` and copies four
   unshaded library JARs to `dataai/jars` plus the shaded CLI to `dataai/cli`.
5. Create a `DataAiQualityJobConfiguration`, write its JSON, and call
   `DataAiSparkSubmitBuilder.BuildQualityJob(...)` to obtain the executable and
   argument list.
6. Review the generated command, then let customer application code launch it
   under the approved identity. The helper itself does not launch Spark,
   transmit telemetry, or write data.
7. Verify output tables and logs. Blank output names disable the corresponding
   CLI write.

The package exposes runtime layout, configuration, command building, and the
function catalog. It does **not** claim direct Microsoft.Spark DataFrame
extension methods in this evaluation release; non-quality functions are called
through the packaged Java APIs.

For production, use the exact immutable NuGet version and feed specified by
Yanbor. The current prerelease packages are evaluation-only.

## 9. Tableau

The Tableau Accelerator visualizes results produced by DataAI ETL; Tableau
does not execute the Spark transformations inside the workbook.

### Fast no-credential test drive

1. Obtain `Tableau\accelerator\DataAI_ETL_Accelerator.twbx` from the controlled
   package or approved Tableau Exchange listing.
2. Open it in Tableau Desktop. It contains fictional embedded data, so no
   database credentials are required.
3. Review run trends, accepted/rejected totals, quality score, findings by
   severity, field profiles, and analytics views.

### Connect to customer DataAI outputs

1. Install the licensed DataAI Spark modules and optional
   `dataai-spark-tableau` adapter in the customer's Spark application.
2. Run DataAI and convert the returned DataFrames with `TableauOutputs` or
   `TableauFunctionOutputs`. Matrix balancing uses the dedicated conversion so
   convergence, iteration, and maximum-error metadata are retained.
3. Explicitly persist the selected output DataFrames as governed Spark/Delta
   tables. The adapter performs no automatic write.
4. Expose them through either Spark Thrift Server or a Databricks SQL warehouse.
5. In Tableau Desktop, connect with **Spark SQL** or **Databricks** using the
   customer-approved authentication method.
6. Use **Data > Replace Data Source** to replace the Accelerator's sample
   `dataai_dashboard_metrics` source.
7. Add `dataai_quality_findings` and `dataai_field_profiles` and relate them by
   `run_id`.
8. Validate mappings, date filters, refreshes, row-level security, permissions,
   and performance in a non-production Tableau project.
9. Publish the workbook to Tableau Cloud/Server only after the customer Tableau
   administrator approves credentials, permissions, refresh schedules, and
   supported connector behavior.

See `Tableau\mapping\FUNCTION_OUTPUTS_FOR_TABLEAU.md` for all DataAI function
families and `Tableau\mapping\TABLEAU_OUTPUT_SCHEMA.md` for exact tables.

## 10. InterSystems IRIS

1. Provision an isolated IRIS namespace and a least-privilege evaluation
   identity.
2. Obtain an InterSystems JDBC driver version approved for the exact IRIS
   server and Java 17. The DataAI package does not include this driver.
3. Install the matching DataAI API, quality, core, functions, and
   `dataai-spark-iris` adapter JARs in the customer's Spark job.
4. Add the JDBC driver as a runtime dependency or cluster library. Confirm its
   license separately.
5. Create `IrisJdbcOptions` with server, Superserver port, namespace, fetch and
   batch sizes. Load user/password from the customer's secret manager.
6. Read a bounded table with `IrisDataFrames.readTable(...)`. For a large table,
   use `readTablePartitioned(...)` only after the IRIS administrator approves a
   numeric partition field, bounds, and connection concurrency.
7. Run `DataAiPipeline` or any function from `dataai-spark-functions`.
8. Convert results with `IrisPipelineOutputs` or `IrisFunctionOutputs`.
   Matrix-balancing conversion retains convergence metadata.
9. Choose the output table and save mode explicitly, then invoke the Spark JDBC
   writer. Prefer staging tables and an IRIS-controlled merge procedure for
   production.
10. Validate reads, output row counts, permissions, retries, partial failures,
    fetch/batch sizes, and maximum connection count.

The optional `IRIS\ipm` package installs only free IRIS-native bootstrap
metadata. It does not install or download the commercial Spark library. Do not
expect the Open Exchange listing alone to install the licensed JAR.

## 11. Alteryx

### Prerequisites for the current evaluation build

- Windows 64-bit;
- Alteryx Designer 2026.1;
- AMP Engine enabled;
- Java 17;
- customer-managed Spark 3.5/Scala 2.12 runtime;
- working `spark-submit` executable on the Designer machine;
- a reachable Spark catalog and customer-approved identity.

### Install and run

1. Verify the YXI hash against `Alteryx\CHECKSUMS.sha256`.
2. Read `Alteryx\LICENSE.md` and accept the evaluation checkbox only if the
   customer agrees to the terms.
3. Close workflows that use an older DataAI tool.
4. Double-click
   `DataAI_ETL_Alteryx_2026_1_Evaluation.yxi` or drag it into Designer.
5. Choose user or administrator installation according to company policy.
6. Restart Designer if **DataAI ETL** does not appear, then confirm **DataAI ETL
   Quality** is available.
7. Load approved sample data into a Spark catalog table. The tool consumes a
   Spark table; it does not consume an in-memory Alteryx record stream.
8. Add **DataAI ETL Quality** to a workflow and set:

   - Spark Submit path;
   - master and deploy mode;
   - source table;
   - optional clean, rejected, profile, and findings tables;
   - normalization, record keys, JSON rules, minimum score, extra Spark
     arguments, and timeout.

9. Remember that every specified output table is overwritten by the current
   CLI. Use dedicated evaluation tables and verify grants first.
10. Enable AMP, attach a Browse tool to the optional Status output, run the
    workflow, and confirm `Succeeded` with exit code `0`.
11. Inspect customer-controlled Spark logs and every configured output. Test at
    least one intentionally failing rule and the minimum-score gate.

The first Alteryx tool exposes the quality CLI. Matrix balancing and other
advanced functions are available in the bundled Java libraries and require a
customer Spark wrapper/job; they are not separate Alteryx buttons in this
version.

For Alteryx Server, an administrator must install the same approved YXI on
every worker and separately validate the service account, Java, Spark,
catalogs, connector libraries, and filesystem access.

## Acceptance test for every installation

Before authorizing production use, record evidence that:

1. the downloaded artifact hash matches the provider value;
2. all DataAI modules use one immutable version;
3. Java, Spark, Scala, and platform versions match the supported matrix;
4. the application reads only the approved source;
5. clean/rejected routing and field profiles are correct;
6. findings contain the expected rule, field, severity, code, message, and
   record key;
7. the minimum quality score passes and fails as designed;
8. representative analytical functions and matrix convergence are correct;
9. no output occurs until customer code or configuration explicitly selects it;
10. the selected output format, save mode, catalog, schema, and table names are
    correct;
11. logs contain no source records, secrets, or credentials;
12. restart, retry, failure, rollback/cleanup, upgrade, and removal procedures
    are understood;
13. the customer has accepted the applicable license and security review.

## Common troubleshooting

- **`UnsupportedClassVersionError`:** use a Java 17-compatible runtime.
- **DataAI class not found:** install API, quality, core, and functions at the
  same version, then restart/recreate compute if the platform requires it.
- **Scala linkage error:** select a Scala 2.12 runtime.
- **Spark linkage error:** validate against the Spark 3.5.x baseline and remove
  accidental bundled Spark/Hadoop libraries.
- **Delta data source not found:** add the customer platform's compatible Delta
  runtime or use an approved persistence format through the embedded API.
- **Configuration missing in cluster mode:** distribute it with `--files` and
  pass the localized driver path.
- **Permission failure:** correct the customer identity and catalog/storage
  grants; DataAI does not bypass platform controls.
- **Matrix does not converge:** confirm equal row/column target totals, complete
  controls, valid keys, and appropriate tolerance/iteration settings.
- **Output was overwritten:** restore through the customer's data recovery
  process and use dedicated tables or the embedded API with an approved save
  mode. The current CLI and Alteryx quality tool overwrite configured outputs.
