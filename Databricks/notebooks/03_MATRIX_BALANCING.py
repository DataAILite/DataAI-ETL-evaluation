# Databricks notebook source
# MAGIC %md
# MAGIC # DataAI ETL: matrix balancing
# MAGIC
# MAGIC Balance fictional region/channel cells against explicit row and column
# MAGIC targets. The customer controls iteration count, tolerance, and writes.

# COMMAND ----------

import re

from pyspark.sql import DataFrame

dbutils.widgets.text(
    "dataai_base_path",
    "/Volumes/<catalog>/<schema>/<volume>/dataai-etl",
    "DataAI evaluation base path",
)
dbutils.widgets.text("maximum_iterations", "50", "Maximum iterations")
dbutils.widgets.text("tolerance", "0.0001", "Convergence tolerance")
dbutils.widgets.dropdown("persist_results", "false", ["false", "true"], "Persist balanced cells")
dbutils.widgets.text("output_catalog", "<customer_catalog>", "Output catalog")
dbutils.widgets.text("output_schema", "<customer_schema>", "Output schema")

base_path = dbutils.widgets.get("dataai_base_path").rstrip("/")
maximum_iterations = int(dbutils.widgets.get("maximum_iterations"))
tolerance = float(dbutils.widgets.get("tolerance"))
persist_results = dbutils.widgets.get("persist_results").lower() == "true"


def require_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"{label} must be a simple Unity Catalog identifier: {value!r}")
    return value


cells = spark.read.option("header", True).option("inferSchema", True).csv(
    f"{base_path}/data/matrix_cells.csv"
)
row_targets = spark.read.option("header", True).option("inferSchema", True).csv(
    f"{base_path}/data/matrix_row_targets.csv"
)
column_targets = spark.read.option("header", True).option("inferSchema", True).csv(
    f"{base_path}/data/matrix_column_targets.csv"
)

# COMMAND ----------

jvm = spark.sparkContext._jvm
balance_result = jvm.com.dataai.etl.spark.functions.MatrixFunctions.balance(
    cells._jdf,
    "region",
    "channel",
    "current_value",
    row_targets._jdf,
    column_targets._jdf,
    "target",
    maximum_iterations,
    tolerance,
)

balanced_cells = DataFrame(balance_result.balancedCells(), spark)

print(
    {
        "iterations": balance_result.iterations(),
        "maximum_error": balance_result.maximumError(),
        "converged": balance_result.converged(),
    }
)
display(balanced_cells.orderBy("region", "channel"))

# COMMAND ----------

if persist_results:
    catalog = require_identifier(dbutils.widgets.get("output_catalog"), "output_catalog")
    schema = require_identifier(dbutils.widgets.get("output_schema"), "output_schema")
    balanced_cells.write.format("delta").mode("errorifexists").saveAsTable(
        f"{catalog}.{schema}.dataai_balanced_matrix"
    )
    print(f"Persisted balanced cells in {catalog}.{schema}.dataai_balanced_matrix.")
else:
    print("No output persisted. Set persist_results=true to enable an explicit write.")
