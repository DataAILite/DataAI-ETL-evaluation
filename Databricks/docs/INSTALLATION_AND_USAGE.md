# DataAI ETL Databricks Installation and Usage

## 1. Confirm prerequisites

Use a Unity Catalog-enabled workspace and compute compatible with Java 17,
Spark 3.5.x, and Scala 2.12. Databricks Runtime 16.4 LTS with the Scala 2.12
image is the initial validation target. Do not claim support until the selected
runtime and access mode pass the provider checklist.

The evaluation package contains `0.1.0-SNAPSHOT` development artifacts. They
are for evaluation only and must not be represented as an immutable production
release.

## 2. Create customer-controlled storage

Adapt `../sql/CREATE_CONSUMER_OUTPUTS.sql` and create a catalog, schema, and
volume under the customer's governance. Example names are intentionally
generic and may be replaced.

The customer controls grants. The identity running the notebooks needs:

- `USE CATALOG` on the selected catalog.
- `USE SCHEMA` on the selected schema.
- `READ VOLUME` for evaluation files.
- `CREATE TABLE` only if optional output persistence is enabled.

## 3. Upload the evaluation payload

Upload the package contents to a Unity Catalog volume. With the Databricks CLI:

```powershell
databricks fs mkdir dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl
databricks fs cp .\lib dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl/lib -r --overwrite
databricks fs cp .\data dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl/data -r --overwrite
databricks fs cp .\docs dbfs:/Volumes/<catalog>/<schema>/<volume>/dataai-etl/docs -r --overwrite
```

Do not upload Maven credentials, Databricks tokens, license certificates,
customer agreements, or customer data with the evaluation payload.

## 4. Install the DataAI JARs

Install these four libraries on the cluster or Job compute:

```text
/Volumes/<catalog>/<schema>/<volume>/dataai-etl/lib/dataai-spark-api-0.1.0-SNAPSHOT.jar
/Volumes/<catalog>/<schema>/<volume>/dataai-etl/lib/dataai-spark-quality-0.1.0-SNAPSHOT.jar
/Volumes/<catalog>/<schema>/<volume>/dataai-etl/lib/dataai-spark-core-0.1.0-SNAPSHOT.jar
/Volumes/<catalog>/<schema>/<volume>/dataai-etl/lib/dataai-spark-functions-0.1.0-SNAPSHOT.jar
```

In the Databricks UI, edit the compute resource, open **Libraries**, select
**Install new**, choose the Unity Catalog volume source, and add each JAR.
Restart compute after installation.

For standard access mode, an administrator may need to add the volume path to
the library allowlist. The DataAI classes use named Java packages.

The CLI JAR is optional and is intended for configuration-driven Spark jobs,
not for the notebook examples.

## 5. Import the notebooks

Import the `notebooks/` directory into a customer-controlled workspace folder.
Run them in this order:

1. `00_INSTALL_AND_VERIFY.py`
2. `01_QUALITY_PIPELINE.py`
3. `02_ANALYTICS_AND_MARKET.py`
4. `03_MATRIX_BALANCING.py`
5. `04_PUBLISH_FOR_BI.py`

Set the `dataai_base_path` widget to:

```text
/Volumes/<catalog>/<schema>/<volume>/dataai-etl
```

## 6. Verify the runtime

The first notebook checks that the four required DataAI classes are visible,
prints the DataAI development version, and reports the Spark, Scala, and Java
runtime versions. A missing class normally means the JAR was not installed on
the attached compute or the compute was not restarted.

## 7. Run the quality example

The quality notebook reads fictional orders, normalizes values, creates a
record key, profiles fields, applies validation rules, and returns clean rows,
rejected rows, findings, profiles, and a run summary.

The notebook does not persist output by default. Set `persist_results` to
`true` only after specifying a customer-controlled catalog and schema.

## 8. Run analytics and matrix examples

The analytics notebook calls the same Java APIs available to Java/Scala Spark
jobs and displays DataFrames through PySpark. It demonstrates grouped totals,
market segments, scenarios, and automatic quality diagnostics.

The matrix notebook balances fictional region/channel cells against row and
column controls. It exposes iteration count, maximum error, convergence status,
balanced values, coefficients, and differences.

## 9. Publish optional governed outputs

The BI notebook creates views only when `publish_views` is explicitly set to
`true`. It never chooses a catalog, schema, table name, or grant automatically.
The resulting views can be queried from Databricks SQL or connected to Power BI
and Tableau using their native Databricks connectors.

## 10. Production fulfillment

For licensed production use, replace every `SNAPSHOT` artifact with an
immutable, signed release delivered from Yanbor LLC's authenticated Maven
repository or an approved customer artifact repository. Pin exact versions in
Jobs and cluster policies. Do not overwrite an existing production version.

## Troubleshooting

### `JavaPackage` is not callable or class is missing

Install all four required JARs on the attached compute and restart it. Confirm
the volume path and allowlist settings.

### `UnsupportedClassVersionError`

The compute JVM is older than Java 17. Select a Java 17-compatible runtime.

### Scala linkage errors

Use the Scala 2.12 runtime image. Do not use a Scala 2.13-only or Spark 4-only
runtime with the current artifacts.

### Writes fail

Keep `persist_results=false`, or grant the notebook identity the customer-
approved Unity Catalog privileges. DataAI does not bypass Unity Catalog.

### Matrix does not converge

Check that row and column targets have equal totals, controls cover the input
keys, and the iteration and tolerance settings are suitable.
