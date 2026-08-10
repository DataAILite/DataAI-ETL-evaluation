# Databricks notebook source
# MAGIC %md
# MAGIC # DataAI ETL: publish governed views for BI
# MAGIC
# MAGIC This optional notebook creates customer-governed Unity Catalog views
# MAGIC over tables written by `01_QUALITY_PIPELINE`. Nothing is created unless
# MAGIC `publish_views` is explicitly set to `true`.

# COMMAND ----------

import re

dbutils.widgets.dropdown("publish_views", "false", ["false", "true"], "Publish BI views")
dbutils.widgets.text("output_catalog", "<customer_catalog>", "Output catalog")
dbutils.widgets.text("output_schema", "<customer_schema>", "Output schema")


def require_identifier(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"{label} must be a simple Unity Catalog identifier: {value!r}")
    return value


publish_views = dbutils.widgets.get("publish_views").lower() == "true"

# COMMAND ----------

if publish_views:
    catalog = require_identifier(dbutils.widgets.get("output_catalog"), "output_catalog")
    schema = require_identifier(dbutils.widgets.get("output_schema"), "output_schema")
    prefix = f"{catalog}.{schema}"

    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {prefix}.dataai_quality_overview AS
        SELECT
          current_timestamp() AS generated_at,
          (SELECT count(*) FROM {prefix}.dataai_clean_rows) AS accepted_rows,
          (SELECT count(*) FROM {prefix}.dataai_rejected_rows) AS rejected_rows,
          (SELECT count(*) FROM {prefix}.dataai_quality_findings) AS findings,
          (SELECT count(*) FROM {prefix}.dataai_field_profiles) AS profiled_fields
        """
    )
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {prefix}.dataai_findings_by_rule AS
        SELECT rule_id, severity, finding_code, count(*) AS findings
        FROM {prefix}.dataai_quality_findings
        GROUP BY rule_id, severity, finding_code
        """
    )
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {prefix}.dataai_field_health AS
        SELECT * FROM {prefix}.dataai_field_profiles
        """
    )

    display(spark.table(f"{prefix}.dataai_quality_overview"))
    display(spark.table(f"{prefix}.dataai_findings_by_rule"))
    print(f"Published governed BI views in {prefix}.")
else:
    print("No views created. Set publish_views=true after reviewing catalog and schema permissions.")
