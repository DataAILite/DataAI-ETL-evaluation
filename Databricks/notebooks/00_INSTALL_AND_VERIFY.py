# Databricks notebook source
# MAGIC %md
# MAGIC # DataAI ETL: install and verify
# MAGIC
# MAGIC Attach compute after installing the four DataAI JARs from a Unity
# MAGIC Catalog volume. This notebook performs read-only runtime checks.

# COMMAND ----------

dbutils.widgets.text(
    "dataai_base_path",
    "/Volumes/<catalog>/<schema>/<volume>/dataai-etl",
    "DataAI evaluation base path",
)

dataai_base_path = dbutils.widgets.get("dataai_base_path").rstrip("/")
print(f"Evaluation base path: {dataai_base_path}")

# COMMAND ----------

jvm = spark.sparkContext._jvm
loader = jvm.java.lang.Thread.currentThread().getContextClassLoader()

required_classes = [
    "com.dataai.etl.spark.api.DataAiResult",
    "com.dataai.etl.spark.quality.QualityEvaluator",
    "com.dataai.etl.spark.core.DataAiPipeline",
    "com.dataai.etl.spark.functions.MatrixFunctions",
]

for class_name in required_classes:
    loader.loadClass(class_name)
    print(f"OK: {class_name}")

# COMMAND ----------

dataai_version = jvm.com.dataai.etl.spark.core.DataAiPipeline.LIBRARY_VERSION
spark_version = spark.version
scala_version = jvm.scala.util.Properties.versionNumberString()
java_version = jvm.java.lang.System.getProperty("java.version")

print(f"DataAI version: {dataai_version}")
print(f"Spark version: {spark_version}")
print(f"Scala version: {scala_version}")
print(f"Java version: {java_version}")

assert str(dataai_version).startswith("0.1.0")
assert str(scala_version).startswith("2.12"), "Current DataAI artifacts require Scala 2.12."
assert int(str(java_version).split(".")[0]) >= 17, "Current DataAI artifacts require Java 17 or later."

# COMMAND ----------

# MAGIC %md
# MAGIC Verification succeeded when every class is marked `OK` and the
# MAGIC runtime values match the qualified compatibility matrix. No data was
# MAGIC persisted and no network call was made by DataAI.
