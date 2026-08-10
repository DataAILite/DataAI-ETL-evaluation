# DataAI ETL NuGet Packages

This folder contains two evaluation NuGet packages from Yanbor LLC, provider
of the DataAI product:

- `Yanbor.DataAI.Etl.Spark` provides .NET configuration, function discovery,
  runtime discovery, and safe `spark-submit` command construction.
- `Yanbor.DataAI.Etl.Spark.Runtime` carries the API, quality, core, functions,
  and shaded CLI JARs and copies them to the consumer output.

DataAI ETL is proprietary, source-available evaluation software from Yanbor
LLC, built with open-source technologies including Apache Spark.

## Build and validate

```powershell
Set-Location C:\Projects\DataAI.Etl\NuGet
.\scripts\build-packages.ps1
```

Successful validation produces:

```text
packages\Yanbor.DataAI.Etl.Spark.0.1.0-evaluation.1.nupkg
packages\Yanbor.DataAI.Etl.Spark.Runtime.0.1.0-evaluation.1.nupkg
CHECKSUMS.sha256
```

The current packages are evaluation prereleases containing DataAI
`0.1.0-SNAPSHOT` JARs. They are not approved for NuGet.org publication or
production use. NuGet.org is public and does not provide marketplace billing or
evaluation expiration. Use a controlled private feed for customer evaluation
and commercial fulfillment.

The packages do not require a DataAI service, telemetry, remote license check,
or customer-data callback. They do not start `spark-submit`; the customer owns
process launch, compute, identity, storage, table names, save modes, scheduling,
orchestration, and security.

See `docs/INSTALLATION_AND_USAGE.md` for customer instructions.
