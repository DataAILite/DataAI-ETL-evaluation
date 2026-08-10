# Databricks notebook source
# MAGIC %md
# MAGIC # DataAI ETL: analytics, market, and automatic quality
# MAGIC
# MAGIC This notebook demonstrates multiple DataAI function families without
# MAGIC persisting output.

# COMMAND ----------

from pyspark.sql import DataFrame

dbutils.widgets.text(
    "dataai_base_path",
    "/Volumes/<catalog>/<schema>/<volume>/dataai-etl",
    "DataAI evaluation base path",
)

base_path = dbutils.widgets.get("dataai_base_path").rstrip("/")
orders = (
    spark.read.option("header", True)
    .option("inferSchema", True)
    .csv(f"{base_path}/data/customer_orders.csv")
)


def from_java(java_dataset) -> DataFrame:
    return DataFrame(java_dataset, spark)


def java_strings(*values: str):
    result = spark.sparkContext._jvm.java.util.ArrayList()
    for value in values:
        result.add(value)
    return result


jvm = spark.sparkContext._jvm
aggregation = jvm.com.dataai.etl.spark.functions.Aggregation.SUM

# COMMAND ----------

regional_totals = from_java(
    jvm.com.dataai.etl.spark.functions.AnalyticsFunctions.groupedSummary(
        orders._jdf,
        java_strings("region"),
        "amount",
        aggregation,
    )
)

market_segments = from_java(
    jvm.com.dataai.etl.spark.functions.MarketFunctions.segments(
        orders._jdf,
        java_strings("region", "channel"),
        "amount",
    )
)

market_scenarios = from_java(
    jvm.com.dataai.etl.spark.functions.MarketFunctions.scenario(
        orders._jdf,
        java_strings("region"),
        "amount",
        10.0,
    )
)

automatic_quality = from_java(
    jvm.com.dataai.etl.spark.functions.DataQualityFunctions.automaticChecks(
        orders._jdf,
        3.0,
    )
)

# COMMAND ----------

display(regional_totals)
display(market_segments)
display(market_scenarios)
display(automatic_quality)

print("No outputs persisted. Each DataAI function returned a customer-controlled DataFrame.")
