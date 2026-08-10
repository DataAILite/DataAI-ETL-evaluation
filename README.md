# DataAI ETL

Embedded DataAI libraries for customer-controlled data pipelines. The first
runtime implementation is the Spark 3.5 / Java 17 SDK in `spark/`.

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

## Repository layout

- `specification/` holds runtime-neutral contracts and golden fixtures.
- `spark/` contains the Spark/JVM implementation.
- `spark/dataai-spark-functions/` contains the portable analytics, market,
  geographic, matrix, quality, recommendation, and narrative functions.
- `SparkETL/` contains the Spark library marketplace-review package, Maven
  artifacts, evaluation distribution, listing assets, and offline validator.
- `Databricks/` contains the Databricks Marketplace provider kit, Unity Catalog
  delivery templates, importable evaluation notebooks, fictional sample data,
  DataAI JAR payload, listing assets, and offline validator.
- `AWS/`, `Microsoft/`, `Oracle/`, and `Google/` contain cloud-marketplace
  review kits with channel-specific listing guidance, customer-run container
  candidates, evaluation artifacts, release gates, and offline validation.
- `Maven/` contains a Maven Central pre-publication kit with binary, source,
  Javadoc, POM, repository-layout, namespace/signing guidance, and an explicit
  publication block while the artifacts remain SNAPSHOT builds.
- `NuGet/` contains two .NET 8 evaluation packages: a typed integration helper
  and a transitive runtime package that copies the DataAI library and shaded
  CLI JARs into customer application output without adding a hosted service.
- `Tableau/` contains the optional Spark-to-Tableau output adapter, packaged
  evaluation Accelerator, fictional sample data, Hyper extract, native Spark
  SQL/Databricks connection examples, and Exchange submission assets.
- `IRIS/` contains the optional InterSystems IRIS JDBC adapter, complete
  function-output contracts, fictional evaluation data, Open Exchange listing
  assets, and a free IRIS-native IPM bootstrap module.
- `examples/` contains platform-specific examples.

The initial Spark vertical slice normalizes data, profiles fields, evaluates
quality rules, routes clean and rejected rows, and publishes standard metadata
tables. Spark and Hadoop remain `provided` dependencies so customer clusters
supply their own compatible runtime.

See the [step-by-step installation and usage guide](docs/INSTALLATION_AND_USAGE.md)
for customer deployment, Oracle AIDP setup, configuration, Java API usage, and
troubleshooting. See [spark/README.md](spark/README.md) for the concise SDK
reference and the [Spark function catalog](docs/FUNCTION_CATALOG.md) for the
complete embeddable API.

For Tableau, start with [Tableau/README.md](Tableau/README.md). The adapter
keeps DataAI computation in the customer's Spark runtime and exposes stable
DataFrames for Tableau through native Spark SQL or Databricks connections; it
does not add a DataAI service or make the core modules depend on Tableau.

For InterSystems IRIS, start with [IRIS/README.md](IRIS/README.md). The adapter
uses Spark's standard JDBC integration, keeps credentials and persistence under
customer control, and includes every DataAI function through the functions
artifact, including matrix balancing.

For Databricks Marketplace, start with
[Databricks/README.md](Databricks/README.md). The package uses Unity Catalog
files and notebooks for controlled evaluation while DataAI continues to run as
embedded Spark libraries inside customer-selected compute.

For .NET and private NuGet-feed distribution, start with
[NuGet/README.md](NuGet/README.md). The helper builds customer-controlled
`spark-submit` commands and JSON quality-job configuration; the runtime package
supplies the verified Spark JARs and includes matrix balancing in its function
catalog.

Marketplace submission kits are packaged as root-level `SparkETL.zip` for the
Spark libraries, `DataAIETLDatabricks.zip` for Databricks Marketplace,
`DataAIETLAWS.zip`, `DataAIETLMicrosoft.zip`, `DataAIETLOracle.zip`,
`DataAIETLGoogle.zip`, and `DataAIETLMaven.zip` for their named channels,
`DataAIETLIRIS.zip` for InterSystems Open Exchange, and
`DataAIETLTableau.zip` for Tableau Exchange. Each archive contains a
`MARKETPLACE_SUBMISSION.md` upload map, listing copy, product assets,
documentation, evaluation materials, licenses, integrity checks, source, tests,
and the locally verified adapter JAR.

## License

DataAI ETL is source-available for evaluation under the PolyForm Free Trial
License 1.0.0 for less than 32 consecutive calendar days. Production,
continued use, and redistribution require a separate written commercial
license. See [LICENSE.md](LICENSE.md) for the complete distribution terms.
A counsel-reviewable, non-binding commercial agreement and order-form sample is
available in
[COMMERCIAL_LICENSE_TEMPLATE.md](COMMERCIAL_LICENSE_TEMPLATE.md).
