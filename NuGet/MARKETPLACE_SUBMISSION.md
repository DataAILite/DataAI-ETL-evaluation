# NuGet Distribution Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

NuGet.org is a public package repository, not a billing marketplace. The
recommended commercial route is a private NuGet feed. Publish the public helper
package to NuGet.org only after Yanbor LLC approves permanent public access.

## Release gates

1. Replace all `0.1.0-SNAPSHOT` JARs with an immutable release.
2. Validate Java 17, Spark 3.5-compatible, Scala 2.12, and .NET 8 behavior.
3. Implement and test a JVM bridge before claiming direct C# DataFrame APIs.
4. Replace evaluation package versions with matching immutable versions.
5. Sign packages with a registered code-signing certificate when required.
6. Publish first to a private test feed and validate from a clean consumer.
7. Obtain legal and distribution approval before any public push.

Do not upload the current evaluation packages to NuGet.org as production
releases.
