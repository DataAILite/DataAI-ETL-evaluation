# Third-Party Notices

## Apache Spark

The Java adapter compiles against Apache Spark 3.5.0. Spark is licensed under
the Apache License 2.0 and is a `provided` dependency; it is not bundled in the
DataAI Tableau adapter JAR.

Project: https://spark.apache.org/

## Tableau Hyper API

The Tableau Hyper API is used only by `scripts/generate_tableau_assets.py` to
create the fictional `.hyper` evaluation artifact. It is not a runtime
dependency of the Java adapter and is not bundled in its JAR.

Project and license information:
https://tableau.github.io/hyper-db/docs/

The generator explicitly selects
`Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU`.

## Pillow

Pillow is used only by the asset generator to create local PNG listing assets
and design previews. It is not bundled in the Java adapter.

Project: https://python-pillow.org/

Tableau, Tableau Exchange, Tableau Hyper, Databricks, Apache Spark, and other
marks are the property of their respective owners. Their mention does not
imply endorsement or marketplace approval.
