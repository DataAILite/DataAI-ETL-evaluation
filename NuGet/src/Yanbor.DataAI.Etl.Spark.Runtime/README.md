# Yanbor.DataAI.Etl.Spark.Runtime

This evaluation package carries the DataAI Spark library JARs and the shaded
configuration-driven CLI JAR. Its transitive MSBuild targets copy them into the
consumer output under `dataai/jars` and `dataai/cli`.

DataAI ETL is proprietary, source-available evaluation software from Yanbor
LLC, built with open-source technologies including Apache Spark.

The package is an embedded runtime dependency. It does not start a DataAI
service, send telemetry, perform remote license checks, or write customer data.

Current evaluation baseline: Java 17, Spark 3.5.0, Scala 2.12, and DataAI
0.1.0-SNAPSHOT. Do not publish this prerelease to NuGet.org as a production
release.
