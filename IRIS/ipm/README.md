# Optional IRIS IPM Bootstrap

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

This module is a free IRIS-native bootstrap and discovery companion. It does
not contain, install, download, or grant rights to the commercial DataAI Spark
libraries.

Before public IPM publication:

1. Test the module with each supported IRIS/IPM version.
2. Update the semantic version in `module.xml`.
3. From an isolated evaluation namespace, run `zpm "load ."`.
4. Verify `DataAI.ETL.Status` compiles and returns the expected description.
5. Test against the InterSystems IPM test registry.
6. Publish the public repository through the Open Exchange workflow with
   **Publish in Package Manager** selected.

The production Spark adapter remains in DataAI's authenticated Maven
repository and requires the applicable DataAI license.
