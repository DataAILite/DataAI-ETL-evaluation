# Third-Party Notices

## Apache Spark and Hadoop

DataAI ETL compiles against Apache Spark 3.5.0 and its transitive Hadoop APIs.
These projects are licensed under the Apache License 2.0. Spark and Hadoop are
`provided` dependencies and are not bundled in the DataAI library JARs.

- Spark: https://spark.apache.org/
- Hadoop: https://hadoop.apache.org/

## Jackson

The shaded DataAI CLI includes Jackson 2.15.3 components used to read local job
configuration. Jackson is licensed under the Apache License 2.0.

Project: https://github.com/FasterXML/jackson

## Build and test tools

Maven, JUnit, and Pillow are used to build, test, validate, or generate local
marketplace assets. They are not DataAI runtime services. JUnit and Pillow are
not bundled in the production DataAI JARs.

Apache Spark, Apache Hadoop, Jackson, Maven, JUnit, Java, Databricks, and other
marks are the property of their respective owners. Their mention does not
imply endorsement, certification, or marketplace approval.
