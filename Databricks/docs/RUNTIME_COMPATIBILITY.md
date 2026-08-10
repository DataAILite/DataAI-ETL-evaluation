# Databricks Runtime Compatibility

## Current artifact baseline

| Component | Baseline |
| --- | --- |
| Java bytecode | Java 17 |
| Apache Spark API | 3.5.0 |
| Scala binary line | 2.12 |
| Jackson in shaded CLI | 2.15.3 |
| DataAI evaluation version | 0.1.0-SNAPSHOT |

## Initial Databricks validation target

Databricks Runtime 16.4 LTS using its Scala 2.12 image is the closest current
target because it uses Java 17 and Spark 3.5.2. Spark 3.5.2 is a patch-level
advance over the 3.5.0 compile baseline, but compatibility must be demonstrated
by executing the complete notebook and Maven-derived test scenarios.

Runtime 17 and later use Spark 4 and move the platform toward Scala 2.13 or
newer JVM baselines. The current DataAI artifacts must not be advertised as
compatible with those runtimes without a separately built and tested release.

## Required qualification matrix

| Runtime | Scala image | Access mode | JDK | Install source | Result |
| --- | --- | --- | --- | --- | --- |
| 16.4 LTS | 2.12 | Standard | 17 | Unity Catalog volume | Not yet externally tested |
| 16.4 LTS | 2.12 | Dedicated | 17 | Unity Catalog volume | Not yet externally tested |
| 16.4 LTS | 2.12 | Standard | 17 | Private Maven | Not yet externally tested |

Test normalization, every rule type, automatic quality checks, representative
function families, matrix convergence, optional Delta persistence, restart,
Jobs execution, and dependency isolation before changing a row to supported.

## Library installation rules

- Install `api`, `quality`, `core`, and `functions` together at the same version.
- Keep Spark and Hadoop supplied by Databricks; they are not bundled by DataAI.
- Use Unity Catalog volumes or an authenticated Maven repository.
- Apply a standard-access-mode allowlist when required.
- Restart compute after changing cluster-scoped JARs.
- Pin immutable production versions; never overwrite release artifacts.
