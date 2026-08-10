# Third-Party Notices

## Apache Spark

The adapter compiles against Apache Spark 3.5.0 under the Apache License 2.0.
Spark is a `provided` dependency and is not bundled in the DataAI IRIS JAR.

## InterSystems JDBC Driver

The adapter refers to the driver class
`com.intersystems.jdbc.IRISDriver` but does not bundle the driver. Customers
must obtain and use an InterSystems-approved driver compatible with their IRIS
and Java versions. The driver remains governed by InterSystems' terms.

Documentation: https://docs.intersystems.com/irislatest/

Maven coordinate when approved by the customer:
`com.intersystems:intersystems-jdbc:<version>`.

## Pillow

Pillow is used only to generate local PNG listing assets. It is not bundled in
the Java adapter.

InterSystems, IRIS, IRIS for Health, HealthShare, Apache Spark, and other marks
are the property of their respective owners. Their mention does not imply
endorsement or marketplace approval.
