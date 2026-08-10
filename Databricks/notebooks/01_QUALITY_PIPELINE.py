# Databricks notebook source
# MAGIC %md
# MAGIC # DataAI ETL: quality pipeline
# MAGIC
# MAGIC This example reads fictional orders from the customer-specified Unity
# MAGIC Catalog volume and calls the DataAI Java API through PySpark. Writes are
# MAGIC disabled unless `persist_results` is explicitly set to `true`.

# COMMAND ----------

import re

from pyspark.sql import DataFrame

dbutils.widgets.text(
    "dataai_base_path",
    "/Volumes/<catalog>/<schema>/<volume>/dataai-etl",
    "DataAI evaluation base path",
)
dbutils.widgets.dropdown("persist_results", "false", ["false", "true"], "Persist Delta outputs")
dbutils.widgets.text("output_catalog", "<customer_catalog>", "Output catalog")
dbutils.widgets.text("output_schema", "<customer_schema>", "Output schema")
dbutils.widgets.dropdown(
    "save_mode",
    "errorifexists",
    ["errorifexists", "append", "overwrite", "ignore"],
    "Delta save mode",
)

base_path = dbutils.widgets.get("dataai_base_path").rstrip("/")
persist_results = dbutils.widgets.get("persist_results").lower() == "true"
output_catalog = dbutils.widgets.get("output_catalog")
output_schema = dbutils.widgets.get("output_schema")
save_mode = dbutils.widgets.get("save_mode")


def require_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"{label} must be a simple Unity Catalog identifier: {value!r}")
    return value


def from_java(java_dataset) -> DataFrame:
    return DataFrame(java_dataset, spark)


orders = (
    spark.read.option("header", True)
    .option("inferSchema", True)
    .csv(f"{base_path}/data/customer_orders.csv")
)

display(orders)

# COMMAND ----------

jvm = spark.sparkContext._jvm
gateway = spark.sparkContext._gateway

accepted_statuses = jvm.java.util.ArrayList()
accepted_statuses.add("Open")
accepted_statuses.add("Closed")

rules = jvm.java.util.ArrayList()
rules.add(jvm.com.dataai.etl.spark.api.RuleSpec.required("customer-required", "customer_id"))
rules.add(jvm.com.dataai.etl.spark.api.RuleSpec.unique("order-unique", "order_id"))
rules.add(jvm.com.dataai.etl.spark.api.RuleSpec.between("amount-range", "amount", 0.0, 100000.0))
rules.add(jvm.com.dataai.etl.spark.api.RuleSpec.dateFormat("order-date", "order_date", "yyyy-MM-dd"))
rules.add(jvm.com.dataai.etl.spark.api.RuleSpec.inSet("status-values", "status", accepted_statuses))

key_fields = gateway.new_array(jvm.java.lang.String, 1)
key_fields[0] = "order_id"

result = (
    jvm.com.dataai.etl.spark.core.DataAiPipeline.fromDataset(orders._jdf)
    .normalize()
    .recordKey(key_fields)
    .profile()
    .validate(rules)
    .execute()
)

clean_rows = from_java(result.cleanRows())
rejected_rows = from_java(result.rejectedRows())
findings = from_java(result.findings())
field_profiles = from_java(result.fieldProfiles())
summary = result.summary()

print(
    {
        "run_id": summary.runId(),
        "status": summary.status(),
        "rows_read": summary.rowsRead(),
        "rows_accepted": summary.rowsAccepted(),
        "rows_rejected": summary.rowsRejected(),
        "quality_score": summary.qualityScore(),
        "library_version": summary.libraryVersion(),
    }
)

# COMMAND ----------

display(clean_rows)
display(rejected_rows)
display(findings)
display(field_profiles)

# COMMAND ----------

if persist_results:
    catalog = require_identifier(output_catalog, "output_catalog")
    schema = require_identifier(output_schema, "output_schema")
    prefix = f"{catalog}.{schema}"

    clean_rows.write.format("delta").mode(save_mode).saveAsTable(f"{prefix}.dataai_clean_rows")
    rejected_rows.write.format("delta").mode(save_mode).saveAsTable(f"{prefix}.dataai_rejected_rows")
    findings.write.format("delta").mode(save_mode).saveAsTable(f"{prefix}.dataai_quality_findings")
    field_profiles.write.format("delta").mode(save_mode).saveAsTable(f"{prefix}.dataai_field_profiles")
    print(f"Persisted customer-controlled outputs in {prefix} using mode {save_mode}.")
else:
    print("No outputs persisted. Set persist_results=true to enable explicit customer-controlled writes.")
