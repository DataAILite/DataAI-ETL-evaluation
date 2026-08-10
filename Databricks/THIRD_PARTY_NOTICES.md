# Third-Party Notices

## Apache Spark and Hadoop

DataAI ETL compiles against Apache Spark 3.5.0 and its transitive Hadoop APIs.
These projects are licensed under the Apache License 2.0. Spark and Hadoop are
`provided` dependencies and are not bundled in the DataAI library JARs.

- Spark: https://spark.apache.org/
- Hadoop: https://hadoop.apache.org/

## Jackson

The optional shaded DataAI CLI includes Jackson 2.15.3 components used to read
local job configuration. Jackson is licensed under the Apache License 2.0.

Project: https://github.com/FasterXML/jackson

## Databricks

Databricks is a customer-selected execution and marketplace platform. DataAI
ETL does not bundle or redistribute Databricks software. Use of Databricks is
subject to the customer's separate Databricks and cloud-provider terms.

## Build and validation tools

Maven, JUnit, and Pillow are used to build, test, validate, or generate local
marketplace assets. They are not required DataAI runtime services. JUnit and
Pillow are not bundled in production DataAI library JARs.

Apache Spark, Apache Hadoop, Jackson, Maven, JUnit, Java, Databricks, and other
marks are the property of their respective owners. Their mention does not
imply endorsement, certification, or marketplace approval.
