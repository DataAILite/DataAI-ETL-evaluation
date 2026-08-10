# DataAI ETL Production Release Guide

**Owner:** Yanbor LLC, provider of the DataAI product  
**Guide date:** August 9, 2026  
**Scope:** How to turn each current DataAI ETL evaluation package into a
controlled production release.

This guide describes the release process; it does not authorize a publication,
upload, push, tag, or customer delivery. Each production release still requires
explicit Yanbor approval and completion of the applicable marketplace review.

## Current state

The present packages are structurally valid evaluation/reviewer kits, but they
are not production releases. They contain `0.1.0-SNAPSHOT` Java artifacts or
`0.1.0-evaluation.1` NuGet packages, include design-preview media in several
channels, and have not completed all external runtime and marketplace gates.

A production release is not made by renaming a ZIP. It requires rebuilding all
binary and platform artifacts from one approved source revision under one
immutable version, then validating the exact delivered files.

## Release inputs to decide first

Before changing a version, create a release record with:

1. Product version, for example `1.0.0`.
2. Source revision and release owner.
3. Maven group ID/namespace controlled by Yanbor LLC.
4. Supported Java, Spark, Scala, and platform versions.
5. Included modules and adapters.
6. Evaluation and commercial fulfillment policy.
7. Marketplace/listing versions and pricing model.
8. Public-versus-private distribution decision for Maven and NuGet.
9. Support, security-response, deprecation, and end-of-life policy.
10. Required legal, security, engineering, product, and marketplace approvers.

Do not begin a Maven Central release until the final namespace is verified.
Changing the group ID later would change all customer coordinates and may also
require Java package and documentation changes.

## Shared production release pipeline

Every product below begins with this pipeline.

### Phase 1: Freeze the source

1. Stop unrelated changes to the release source revision.
2. Record the revision and create the release candidate under Yanbor's source
   control procedure.
3. Confirm that no generated binaries, credentials, customer data, tokens, or
   signed agreements are in source control.
4. Confirm that the public API and output schemas are approved for the release.
5. Update release notes with new functions, fixes, compatibility changes,
   migration steps, and known limitations.

### Phase 2: Replace development versions

1. Change the Maven reactor and every child/adapter POM from
   `0.1.0-SNAPSHOT` to the chosen immutable version.
2. Update runtime version constants and every platform manifest.
3. Update copied POMs, example dependencies, notebook paths, Docker labels,
   filenames, checksums, listing release notes, and compatibility documents.
4. For NuGet, use a stable package version that corresponds to the immutable
   JVM release. Update its project metadata, dependency version, MSBuild paths,
   validation expectations, and embedded JAR filenames.
5. For Alteryx, replace `Evaluation` and `SNAPSHOT` filenames/metadata only in
   the commercial production edition; keep a separately versioned evaluation
   edition if Yanbor will continue offering one.
6. Search the release payload for stale version references:

   ```powershell
   rg -n "0\.1\.0-SNAPSHOT|0\.1\.0-evaluation\.1" C:\Projects\DataAI.Etl
   ```

7. Review every match. Warnings that explain why old snapshots are unsupported
   may remain in historical documentation; executable configuration, manifests,
   filenames, checksums, examples, and customer instructions must use the new
   version.

The current generators and NuGet/Alteryx build scripts contain hard-coded
evaluation filenames. Update or parameterize those scripts before attempting a
production build. Do not simply rename their generated files afterward.

### Phase 3: Build and test the canonical Spark release

1. Use the approved Java 17 and Maven 3.9 toolchain.
2. From `C:\Projects\DataAI.Etl\spark`, run:

   ```powershell
   mvn clean verify
   ```

3. Require `BUILD SUCCESS` and zero failed/error/skipped tests unless an
   exception is explicitly approved and documented.
4. Run a clean consumer build from an empty Maven repository.
5. Run real Spark execution tests for quality rules, normalization, record
   keys, profiling, all changed functions, empty/null/error cases, and matrix
   convergence.
6. Inspect every JAR. Confirm that Spark/Hadoop classes are not bundled and
   that dependency versions match the supported baseline.
7. Generate sources and Javadocs for public modules.
   Before the first production release, bind approved versions of the Maven
   Source and Javadoc plugins to a release profile so a clean build recreates
   every companion JAR. The current ordinary `clean verify` lifecycle does not
   generate them; a production pipeline must never depend on companion JARs
   left by an earlier build.
8. Scan dependencies and binaries, create an SBOM, and resolve or formally
   accept findings according to Yanbor policy.
9. Generate SHA-256 values and approved digital signatures for the canonical
   artifacts.

### Phase 4: Stage, never publish first

1. Copy the immutable artifacts into a clean release-staging directory.
2. Regenerate each selected platform package from that directory/source
   revision.
3. Run each package's validator after the final binary copy.
4. Test the exact staged artifact on the exact advertised platform.
5. Test acquisition and installation through a private feed, preview audience,
   Limited listing, private exchange, or separate buyer account.
6. Freeze artifact hashes after validation. Any binary change invalidates the
   old scan, test evidence, signature, checksum, and platform package.
7. Obtain the product-specific sign-offs below.
8. Publish only after a separate explicit release authorization.

## 1. DataAI ETL Spark core release

### Production deliverables

- `dataai-spark-api-<version>.jar`
- `dataai-spark-quality-<version>.jar`
- `dataai-spark-core-<version>.jar`
- `dataai-spark-functions-<version>.jar`
- optional shaded `dataai-spark-cli-<version>.jar`
- matching POMs, sources/Javadocs where distributed, checksums, signatures,
  SBOM, licenses, notices, compatibility matrix, function catalog, and release
  notes

### Release steps

1. Complete the shared pipeline.
2. Run the Spark package generator:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\SparkETL\scripts\generate_spark_marketplace_assets.py
   ```

3. Run its validator:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\SparkETL\scripts\validate_spark_marketplace_package.py
   ```

4. Confirm the generator copied the new immutable JARs/POMs and that no
   `SNAPSHOT` artifact exists in `SparkETL.zip` or its customer payload.
5. Publish the modules first to a staging/private Maven repository.
6. Resolve them from an empty cache and run both embedded API and shaded CLI
   tests on a qualified customer-like cluster.
7. Promote the exact repository coordinates only after engineering, security,
   legal, product, and release approval.

### Sign-off

The Spark release becomes the canonical binary input for every product below.
Do not allow a platform package to carry a different unrecorded Spark build.

## 2. Databricks production release

### Production deliverables

- immutable API, quality, core, and functions JARs;
- versioned notebooks and fictional sample data;
- governed volume/share payload;
- installation, compatibility, security, licensing, and function documents;
- final Databricks screenshots and release notes.

### Release steps

1. Complete the Spark release and update the Databricks manifest, notebooks,
   configuration templates, documentation, and generator version references.
2. Generate and validate the package:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Databricks\scripts\generate_databricks_assets.py
   & <approved-python> C:\Projects\DataAI.Etl\Databricks\scripts\validate_databricks_package.py
   ```

3. Create a provider-controlled Unity Catalog release volume and upload the
   immutable staged payload.
4. Install the exact four JARs on the selected Databricks Runtime and access
   mode; restart compute and run every notebook.
5. Validate allowlists, class loading, quality routing, all advertised
   analytics, matrix convergence, explicit Delta writes, permissions, job
   restarts, and removal.
6. Replace design previews with captures from the validated workspace.
7. Test the personalized/private-exchange request, approval, share access,
   installation, and revocation from a separate consumer workspace.
8. Freeze share assets and hashes, complete
   `Databricks\PROVIDER_CHECKLIST.md`, and obtain Databricks/provider approval.
9. Publish the listing revision only after explicit Yanbor authorization.

## 3. AWS production release

### Production deliverable

An immutable, scanned Linux container image based on an approved EMR Serverless
Spark image, copied to AWS Marketplace-managed ECR with customer launch and IAM
instructions. The root ZIP is supporting review material, not the deployable
product.

### Release steps

1. Complete the Spark release and AWS seller/container-product onboarding.
2. Update `AWS\container\Dockerfile`, manifest, listing, documentation, release
   gates, and generator to the immutable version.
3. Generate and validate the AWS provider kit:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\AWS\scripts\generate_marketplace_package.py
   & <approved-python> C:\Projects\DataAI.Etl\AWS\scripts\validate_marketplace_package.py
   ```

4. Build from the exact approved EMR Serverless base digest; preserve its
   entrypoint and required non-root/runtime user.
5. Scan the operating-system and application layers, generate an image SBOM,
   sign/attest the image under Yanbor policy, and record its digest.
6. Push that digest to the product's Marketplace-managed ECR repository and add
   an immutable product version/delivery option.
7. In a separate allow-listed buyer account, subscribe, pull the image, create
   the EMR Serverless application, and run quality, analytics, matrix, write,
   upgrade, and cancellation tests.
8. Validate the selected contract/entitlement/metering model without adding
   customer-data collection.
9. Complete `AWS\PROVIDER_CHECKLIST.md`, resolve AWS scans/review findings, and
   move from Limited to Public only after approval.

## 4. Microsoft production release

### Production deliverable

The deliverable depends on the offer type approved in Partner Center. For an
Azure Container offer it must be a functional customer-run Kubernetes
application packaged in the required CNAB format; the current component image
alone is not a production offer.

### Release steps

1. Obtain written offer-type agreement from Microsoft and Yanbor product/legal
   owners. Decide whether Yanbor will support an AKS application or use a
   lead-generation/private-fulfillment route.
2. Complete the Spark release and update all Microsoft version references.
3. If using Azure Container, implement the actual AKS application, deployment
   templates, identity/RBAC, resource lifecycle, upgrades, and removal.
4. Generate and validate the provider kit:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Microsoft\scripts\generate_marketplace_package.py
   & <approved-python> C:\Projects\DataAI.Etl\Microsoft\scripts\validate_marketplace_package.py
   ```

5. Build and scan the component image, generate SBOM/signing evidence, then
   build and validate the CNAB bundle with the required numeric version.
6. Push only the approved artifacts to the primary-tenant ACR configured for
   the offer.
7. Configure offer, plan, technical assets, pricing, markets, legal/support
   URLs, final media, and reviewer instructions.
8. Deploy from Partner Center preview into a separate tenant. Test creation,
   library availability, Spark execution, identity, data boundaries, upgrades,
   and uninstall.
9. Complete `Microsoft\PROVIDER_CHECKLIST.md`, resolve certification findings,
   and choose **Review and publish** only after explicit approval.

## 5. Oracle production release

### Production deliverable

Either an approved OCI Application artifact/container image or a
lead-generation listing with private immutable Maven/JAR fulfillment. Choose
one and document it; do not imply that the provider ZIP installs in OCI.

### Release steps

1. Complete Oracle PartnerNetwork, Marketplace Publisher, commercial, tax, and
   listing-type eligibility steps.
2. Complete the Spark release and update all Oracle version references.
3. Generate and validate the provider kit:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Oracle\scripts\generate_marketplace_package.py
   & <approved-python> C:\Projects\DataAI.Etl\Oracle\scripts\validate_marketplace_package.py
   ```

4. For an OCI Application container, build, scan, SBOM, sign, and push the
   immutable image to OCI Container Registry; create the Publisher artifact.
5. For private fulfillment, stage immutable Maven modules/JARs in the approved
   authenticated channel and keep the Open Marketplace listing credential-free.
6. From a separate OCI tenancy, acquire the listing, place JARs into
   customer-controlled Object Storage, and run them as OCI Data Flow
   dependencies.
7. Validate Spark compatibility, IAM, output control, matrix balancing,
   upgrade, rollback/removal, and absence of a Yanbor-hosted runtime.
8. Complete `Oracle\PROVIDER_CHECKLIST.md`, attach final artifacts to the
   listing revision, resolve Oracle review findings, and publish after approval.

## 6. Google production release

### Production deliverable

An immutable, scanned Marketplace container image bearing the exact Google
Marketplace service-name annotation, used as the approved artifact carrier for
customer-controlled Dataproc delivery.

### Release steps

1. Complete Google Cloud Marketplace partner and Producer Portal onboarding.
2. Create the product and obtain its actual service name.
3. Complete the Spark release and update the Google generator, manifest,
   Dockerfile, listing, and documentation.
4. Set the required Docker label to the exact
   `services/<service-name>` value.
5. Generate and validate the provider kit:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Google\scripts\generate_marketplace_package.py
   & <approved-python> C:\Projects\DataAI.Etl\Google\scripts\validate_marketplace_package.py
   ```

6. Build the immutable image, scan it, create an SBOM/signing attestation, and
   push the selected tag to the designated staging registry.
7. In Producer Portal, select the staged image, run **Save and Validate**, and
   allow Google to copy the approved tag into its Marketplace registry.
8. From a separate buyer project, subscribe, access the image, copy JARs to
   customer-controlled Cloud Storage, and run Dataproc quality, analytics,
   matrix, write, upgrade, and removal tests.
9. Complete `Google\PROVIDER_CHECKLIST.md`, resolve partner-engineering
   findings, freeze the image digest, and publish only after approval.

## 7. Maven Central production release

### Production deliverables

For each public non-POM module: binary JAR, sources JAR, Javadoc JAR, POM, PGP
signature for each POM/JAR, and Central-required checksums.

### Release steps

1. Verify a namespace controlled by Yanbor LLC in Central Publisher Portal.
2. Obtain legal/product approval for permanent public distribution. Maven
   Central is not a billing or entitlement service.
3. Complete the Spark release using the verified namespace and full required
   POM name, description, URL, license, developer, and SCM metadata.
4. Update the Maven package generator and all repository-layout paths.
5. Generate and validate the prepublication kit:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Maven\scripts\generate_marketplace_package.py
   & <approved-python> C:\Projects\DataAI.Etl\Maven\scripts\validate_marketplace_package.py
   ```

6. Sign every release POM/JAR with the approved Yanbor PGP key; publish the
   public key through the approved mechanism.
7. Ensure all runtime dependencies are Central-resolvable and Spark/Hadoop are
   `provided`.
8. Resolve the complete release from an empty repository and run a consumer
   Spark test.
9. Create a Central deployment bundle or use the Central Publishing Maven
   Plugin with automatic publishing disabled.
10. Upload to staging, inspect Central validation, and correct failures by
    rebuilding the candidate.
11. Publish only after final authorization. Central components are immutable;
    a defect requires a new version.

## 8. NuGet production release

### Production deliverables

- `Yanbor.DataAI.Etl.Spark.Runtime.<version>.nupkg`, containing the exact
  immutable DataAI JARs;
- `Yanbor.DataAI.Etl.Spark.<version>.nupkg`, depending on the same Runtime
  version;
- checksums, optional signatures, SBOM, package metadata, readme, license,
  notices, and release notes.

### Release steps

1. Complete the Spark release first.
2. Update the Runtime project JAR includes, `.props`, `.targets`, package
   metadata, helper dependency, source validation, consumer validation, and
   `NuGet\scripts\build-packages.ps1`; it currently expects hard-coded
   `0.1.0-SNAPSHOT` filenames.
3. Choose a stable NuGet version that maps unambiguously to the JVM version.
4. Run the package build with that version:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass `
     -File C:\Projects\DataAI.Etl\NuGet\scripts\build-packages.ps1 `
     -Version <production-version> `
     -Configuration Release
   ```

5. Run `NuGet\scripts\validate-packages.ps1` and inspect both package archives.
6. Restore from a new local/private feed and run the clean PackageConsumer test
   on .NET 8 with the supported Java/Spark runtime.
7. Confirm the helper makes no unsupported direct C# DataFrame claim and that
   all catalog writes remain customer-selected.
8. Sign packages if required by the selected feed/Yanbor policy.
9. Push Runtime first and helper second to a private staging feed; verify
   read-only customer restore and execution.
10. Promote to the commercial private feed after approval. Publish to nuget.org
    only after separate authorization for permanent public access.

## 9. Tableau production release

### Production deliverables

- free validated `DataAI_ETL_Accelerator.twbx` for Tableau Exchange;
- immutable `dataai-spark-tableau-<version>.jar` plus canonical DataAI Spark
  modules through commercial fulfillment;
- output-schema/function mapping, installation guide, final screenshots,
  checksums, license/terms/support URLs, and release notes.

### Release steps

1. Complete the Spark release and build the Tableau adapter in the Maven
   reactor under the same immutable version.
2. Update Tableau POM, manifest, examples, mappings, workbook metadata,
   documentation, and asset generator to the new version.
3. Generate and validate offline assets:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Tableau\scripts\generate_tableau_assets.py
   & <approved-python> C:\Projects\DataAI.Etl\Tableau\scripts\validate_tableau_package.py
   ```

4. Open the generated TWBX in every advertised Tableau Desktop version. Repair
   metadata if necessary, resave, and rerun checksums.
5. Connect a test copy to actual DataAI outputs through Spark SQL and
   Databricks. Validate source replacement, relationships, refresh, filters,
   accessibility, row-level security, permissions, and performance.
6. Run the adapter tests for pipeline outputs, universal function outputs, and
   matrix convergence metadata.
7. Capture final Tableau screenshots from the tested workbook.
8. Rebuild the partner review ZIP from the final Tableau files and generate its
   root SHA-256 sidecar.
9. Complete managed Salesforce Partner/partner-manager review. Publish the
   Accelerator only after Tableau and Yanbor approval; fulfill production JARs
   separately under commercial terms.

## 10. InterSystems IRIS production release

### Production deliverables

- immutable `dataai-spark-iris-<version>.jar` plus canonical DataAI modules;
- customer-approved InterSystems JDBC dependency instructions, but no bundled
  driver;
- optional free IPM bootstrap with its own tested version;
- controlled evaluation/commercial fulfillment, checksums, mappings, examples,
  support/legal URLs, and release notes.

### Release steps

1. Complete the Spark release and build the IRIS adapter under the same
   immutable version.
2. Update IRIS POM, manifest, source/runtime metadata, examples, IPM module,
   distribution names, documentation, and generator version references.
3. Generate and validate offline assets:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\IRIS\scripts\generate_iris_assets.py
   & <approved-python> C:\Projects\DataAI.Etl\IRIS\scripts\validate_iris_package.py
   ```

4. Run against each advertised IRIS server version and its exact supported
   JDBC driver. Test namespace/authentication, bounded and partitioned reads,
   fetch size, batch size, connection limits, writes, staging/merge, retries,
   transaction/partial-failure handling, and secret redaction.
5. Verify quality outputs, analytical function outputs, and matrix convergence
   metadata in IRIS tables.
6. If publishing the IPM bootstrap, host its source publicly, test
   `module.xml` with each advertised IRIS/IPM version, and confirm that it
   contains and downloads no commercial JAR.
7. Rebuild the root review ZIP and SHA-256 sidecar from the final adapter JAR.
8. Submit the controlled listing/release to Open Exchange review; publish the
   commercial JAR only through the approved private fulfillment channel.

## 11. Alteryx production release

### Production deliverable

An immutable, validated YXI built for a specific Alteryx Designer embedded
Python generation, plus its checksum, dependency/security evidence, customer
instructions, compatibility matrix, and release notes. Server support requires
separate evidence.

### Release steps

1. Complete the Spark release and copy the immutable shaded CLI JAR into the
   Alteryx runtime source.
2. Update Alteryx manifests, tool/UI version, runtime JAR path, YXI name,
   provider/customer ZIP names, documentation, source checks, and build scripts.
   The current script is explicitly hard-coded for an evaluation YXI and the
   `0.1.0-SNAPSHOT` CLI.
3. Rebuild the UI from the locked dependency set:

   ```powershell
   Set-Location C:\Projects\DataAI.Etl\Alteryx\yxi-source\ui\DataAiEtlQuality
   npm ci
   npm run build
   ```

4. Acquire the official AYX Python SDK wheels for the exact Designer embedded
   Python version through the approved build process; scan and record them.
5. Generate assets, build the YXI/provider ZIP, and validate:

   ```powershell
   & <approved-python> C:\Projects\DataAI.Etl\Alteryx\scripts\generate_alteryx_assets.py
   & <approved-python> C:\Projects\DataAI.Etl\Alteryx\scripts\build_alteryx_package.py --wheel-dir <approved-wheel-directory>
   & <approved-python> C:\Projects\DataAI.Etl\Alteryx\scripts\validate_alteryx_package.py
   ```

6. Install the exact YXI on a clean Designer 2026.1 machine, enable AMP, and
   run the sample plus failure, timeout, license, overwrite, credential, and
   command-injection tests.
7. If claiming Alteryx Server support, install on every worker type and test the
   service identity, Java, Spark, catalogs, connectors, concurrency, scheduling,
   upgrade, and removal.
8. Replace design previews with tested-release screenshots; generate the final
   checksum and do not change the YXI afterward.
9. Complete `Alteryx\PROVIDER_CHECKLIST.md`, upload the immutable YXI to the
   Creator Portal edition/version, resolve verification/security findings with
   a new version, and publish only after Alteryx and Yanbor approval.

## Production release sign-off table

Every product release record should contain completed evidence for:

| Gate | Required evidence |
| --- | --- |
| Version | One immutable version across binaries, manifests, docs, examples, and listings |
| Source | Approved revision and reproducible build inputs |
| Build | Full Maven reactor and product package build logs |
| Tests | Spark execution plus target-platform test report |
| Compatibility | Exact Java/Spark/Scala/platform versions tested |
| Integrity | SHA-256 values, signatures/attestations, container digests |
| Security | Dependency/container scans, SBOM, secrets review, disposition of findings |
| Legal | Approved license, notices, privacy, terms, export/commercial review |
| Support | Monitored contact, severity targets, upgrade and end-of-life policy |
| Customer | Clean acquisition, installation, upgrade, rollback/removal acceptance test |
| Marketplace | Provider/listing approval and final artifact identifier |
| Authorization | Named Yanbor approver and publication timestamp |

If one required gate is incomplete, label the product **release candidate** or
**evaluation**, not production.

## Recommended release order

1. Canonical Spark modules and optional CLI.
2. Private Maven staging and clean-consumer verification.
3. Tableau and IRIS adapters in the Maven reactor.
4. Databricks and cloud/provider packages.
5. NuGet and Alteryx packages, because they embed the completed Spark binaries.
6. Platform preview/private-exchange/buyer tests.
7. Maven Central or nuget.org only if permanent public distribution is
   separately approved.
8. Final marketplace publication after all product-specific approvals.

This order prevents a platform package from shipping a JAR that differs from
the canonical licensed Spark release.
