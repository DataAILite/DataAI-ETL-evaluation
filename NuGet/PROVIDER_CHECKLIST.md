# DataAI ETL NuGet Provider Checklist

- [ ] Immutable DataAI release replaces every SNAPSHOT artifact.
- [ ] Package, assembly, JAR, documentation, and runtime versions agree.
- [ ] Java 17 / Spark 3.5-compatible / Scala 2.12 runtime is tested.
- [ ] .NET 8 build, publish, and package-consumer validation pass.
- [ ] Runtime JAR checksums match the approved Maven build.
- [ ] No Spark or Hadoop classes are bundled in library JARs.
- [ ] License, third-party notices, README, and icon render correctly.
- [ ] Public URLs and Yanbor LLC ownership metadata are final.
- [ ] Public NuGet.org distribution is explicitly authorized.
- [ ] Commercial billing and entitlement are handled outside NuGet.org.
- [ ] No credentials, telemetry, customer data, or hidden writes are present.
- [ ] Direct Microsoft.Spark API claims are withheld until JVM-bridge testing.
