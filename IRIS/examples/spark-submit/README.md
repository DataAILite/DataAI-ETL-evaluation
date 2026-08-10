# Spark Submit with InterSystems IRIS

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

Set secrets through the customer-approved secret mechanism. The environment
variables below are illustrative and should not be printed or stored in shell
history on shared systems.

Required runtime artifacts:

- customer Spark application JAR;
- `dataai-spark-iris` and its DataAI dependencies, normally resolved during
  the customer application build;
- the customer-approved `intersystems-jdbc-<version>.jar`.

```powershell
$env:IRIS_JDBC_URL = 'jdbc:IRIS://iris.internal:1972/DATAAI'
$env:IRIS_USER = 'dataai_etl'
$env:IRIS_PASSWORD = '<retrieve-from-secret-manager>'

spark-submit `
  --jars C:\ApprovedDrivers\intersystems-jdbc.jar `
  --class com.dataai.customer.examples.IrisDataAiPipelineExample `
  customer-dataai-iris-job.jar
```

In cluster deploy mode, configure secrets through the platform rather than
driver-local environment variables. Confirm that executors can reach the IRIS
Superserver port and that connection concurrency is approved.
