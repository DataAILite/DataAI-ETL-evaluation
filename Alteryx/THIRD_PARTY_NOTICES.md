# Third-Party Notices

## Alteryx SDK components

The YXI evaluation candidate includes Alteryx Python SDK 2.5.3 and its runtime
dependencies for Alteryx Designer 2026.1 / Python 3.13. These components are
provided under the Alteryx SDK and API License Agreement. The configuration UI
is based on the official AYX UI SDK template and packages.

- SDK agreement: https://www.alteryx.com/alteryx-sdk-and-api-license-agreement
- AYX Python SDK: https://pypi.org/project/ayx-python-sdk/
- AYX Plugin CLI: https://pypi.org/project/ayx-plugin-cli/

Alteryx and Designer are trademarks of Alteryx, Inc. Inclusion or mention does
not imply Marketplace approval, certification, or endorsement.

## Apache Spark and Hadoop

DataAI ETL compiles against Apache Spark 3.5.0 and its transitive Hadoop APIs.
Spark and Hadoop are Apache License 2.0 projects and are `provided`
dependencies; they are not bundled in the DataAI JARs or this YXI.

- Spark: https://spark.apache.org/
- Hadoop: https://hadoop.apache.org/

## Jackson

The shaded DataAI CLI includes Jackson 2.15.3 components used to read the local
job configuration. Jackson is licensed under the Apache License 2.0.

Project: https://github.com/FasterXML/jackson

## Python runtime dependencies

The Alteryx SDK wheel declares runtime packages including Click, deprecation,
grpcio-fips, NumPy, pandas, protobuf, psutil, Pydantic, PyArrow, PyPAC,
python-dateutil, pytz, requests, six, Typer, urllib3, wincertstore, and
xmltodict. Their license metadata is retained inside the packaged Python
distribution. Review all applicable third-party terms before commercial
release.

Maven, JUnit, Pillow, Node.js, and the AYX Plugin CLI are used for build,
testing, validation, or local asset generation. They are not Yanbor-hosted
runtime services.
