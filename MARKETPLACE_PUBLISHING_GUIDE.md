# DataAI ETL Marketplace Publishing Guide

**Publisher:** Yanbor LLC, provider of the DataAI product  
**Audit date:** August 9, 2026  
**Scope:** Provider publication instructions for every distribution kit currently
prepared under `C:\Projects\DataAI.Etl`.

## Important readiness result

All current kits pass their available offline structural, manifest, checksum,
and package validators. They are suitable for internal review and controlled
evaluation preparation. **None of the current artifacts is ready for a public
production marketplace submission.** Every Spark-based kit still contains
`0.1.0-SNAPSHOT` evaluation/development artifacts, and the platform-specific
external validation and provider-onboarding gates have not all been completed.

Do not interpret "offline validation passed" as marketplace certification.
Public submission requires an immutable release, legal and security approval,
the target marketplace's provider account, and successful execution on the
advertised platform.

## Package readiness summary

| Provider kit | Intended channel | Offline kit status | Submit current build? | Principal remaining gates |
| --- | --- | --- | --- | --- |
| `SparkETL.zip` | Private Maven repository; Maven Central only if public distribution is approved | Passed | No | Immutable version, namespace, POM metadata, source/Javadoc JARs, signatures, SBOM, release approval |
| `DataAIETLDatabricks.zip` | Databricks Marketplace or private exchange | Passed | No | Databricks provider approval, public policy URLs, immutable release, actual Databricks Runtime execution |
| `DataAIETLAWS.zip` | AWS Marketplace container product for EMR Serverless | Passed | No | Seller onboarding, immutable image, security scan, EMR test, pricing/entitlement, AWS review |
| `DataAIETLMicrosoft.zip` | Microsoft Marketplace offer-type review; likely Azure Container/Kubernetes application | Passed | No | Offer-type approval, functional CNAB/AKS design if used, immutable release, preview deployment, certification |
| `DataAIETLOracle.zip` | Oracle Cloud Marketplace OCI Application or lead-generation listing | Passed | No | Oracle Partner onboarding, listing-type choice, immutable image/release, OCI Data Flow validation, Oracle review |
| `DataAIETLGoogle.zip` | Google Cloud Marketplace container product for Dataproc delivery | Passed | No | Partner onboarding, service-name annotation, immutable image, security scan, buyer-project and Dataproc test |
| `DataAIETLMaven.zip` | Maven Central Publisher Portal | Passed | No | Verified Yanbor namespace, immutable version, complete metadata, sources/Javadocs, PGP signatures, authorization for permanent public distribution |
| `DataAIETLTableau.zip` | Tableau Exchange Accelerator | Passed | No | Managed Salesforce Partner eligibility, Tableau Desktop render/interaction test, final screenshots, partner approval |
| `DataAIETLIRIS.zip` | InterSystems Open Exchange | Passed | No | Exact IRIS/JDBC/runtime test, public URLs, controlled demo fulfillment, optional IPM test, approval |
| `DataAIETLAlteryx.zip` | Alteryx Marketplace Custom Tool | Passed | No | Immutable YXI, clean Designer 2026.1 and Server tests, security/verification evidence, Partner review |
| NuGet `.nupkg` files | Private NuGet feed; nuget.org only if public distribution is approved | Passed | No | Immutable JVM runtime, matching package versions, clean-consumer test, signing policy, public-distribution approval |

The Tableau and IRIS adapter checksums were refreshed after the final Maven
build, their root ZIPs were rebuilt, and root `.sha256` sidecars were added.

## Common release procedure

Complete these steps before following any channel-specific submission steps:

1. Choose one immutable release version, for example `1.0.0`; remove every
   `SNAPSHOT` reference from binaries, POMs, manifests, documentation, examples,
   package names, runtime reporting, and container labels.
2. Run the full Maven reactor from `C:\Projects\DataAI.Etl\spark` with
   `mvn clean verify`.
3. Run the target package generator and validator, then archive their complete
   output. Do not reuse a validator report from an earlier binary.
4. Verify Java 17, Spark 3.5.x, Scala 2.12, and every advertised platform
   version using the exact artifact that will be submitted.
5. Scan dependencies and containers, create an SBOM, inspect JAR contents, and
   confirm that Spark and Hadoop remain customer-provided rather than bundled.
6. Generate and independently verify SHA-256 checksums. Sign artifacts where
   the repository or Yanbor release policy requires signing.
7. Replace every bracketed URL or placeholder with stable public documentation,
   support, privacy, evaluation-license, commercial-terms, and security URLs.
8. Confirm that samples and screenshots contain only fictional data and no
   credentials, tokens, customer names, license certificates, or agreements.
9. Have Yanbor LLC approve the release, license presentation, pricing,
   fulfillment method, support commitment, and permanent-publication scope.
10. Test acquisition and installation using a separate buyer/customer account.
11. Publish only after the channel-specific reviewer accepts the product.

`LICENSE.md` is an evaluation license and
`COMMERCIAL_LICENSE_TEMPLATE.md` is a non-binding sample. Marketplace terms,
an executed customer agreement, and an order form must be reviewed together by
Yanbor's qualified legal adviser before commercial launch.

## 1. Generic Spark library distribution

### Where to distribute

The recommended production channel is a Yanbor-controlled authenticated Maven
repository or a customer-controlled artifact repository. Apache Spark does not
operate a commercial marketplace for third-party JAR libraries. Use Maven
Central only if Yanbor approves permanent public access; use the cloud-specific
kits below for procurement through cloud marketplaces.

### What the ZIP is

`SparkETL.zip` is a provider review and controlled-evaluation kit. Its internal
`distribution/DataAI_ETL_Spark_Evaluation.zip` is the customer evaluation
download. The production deliverable should be immutable Maven modules and,
only when needed, the shaded CLI JAR.

### Publication steps

1. Complete the common release procedure.
2. Select an authenticated Maven repository and create a read-only customer
   repository or virtual repository.
3. Publish the API, quality, core, and functions modules under one immutable
   version. Publish the CLI separately when customers need the JSON-driven job.
4. Keep Spark and Hadoop dependencies in `provided` scope.
5. Upload the associated POMs, checksums, SBOM, license, third-party notices,
   compatibility matrix, installation guide, and function catalog.
6. Create customer-scoped, read-only credentials and a revocation procedure;
   never embed credentials in a ZIP, POM, or JAR.
7. Resolve the dependency from a clean Maven cache and run a sample Spark job
   on a separate machine.
8. Provide the customer with repository configuration, exact coordinates,
   checksums, supported-runtime statement, and signed commercial entitlement.
9. Retain immutable versions; publish a new version for every correction.

Use `SparkETL\MARKETPLACE_SUBMISSION.md` and
`SparkETL\listing\SPARK_MARKETPLACE_LISTING.md` as the release checklist and
listing copy.

## 2. Databricks Marketplace

### Where and what to submit

Use Databricks Marketplace **Provider console**. The recommended first release
is a private-exchange or personalized listing that requires provider approval.
The Marketplace share should expose approved notebooks, fictional data,
documentation, and an evaluation-volume payload. The root ZIP is the provider
kit; it is not uploaded as a raw Marketplace product.

### Submission steps

1. Apply to become a public or private Databricks Marketplace provider.
2. Use a Premium-or-higher Unity Catalog workspace, create the Yanbor provider
   profile, and assign the Marketplace admin role. Personalized listings also
   require the relevant recipient privileges.
3. Complete the common release procedure and every item in
   `Databricks\PROVIDER_CHECKLIST.md`.
4. Execute every notebook on the advertised Databricks Runtime and access mode.
   Replace the included design previews with screenshots from that execution.
5. Adapt and run `Databricks\sql\CREATE_PROVIDER_ASSETS.sql` in a
   provider-controlled catalog, schema, and volume.
6. Upload the approved `lib`, `data`, and `docs` payloads to the provider volume
   and import the notebooks into a provider workspace folder.
7. Create an OpenSharing share containing the approved volume and notebooks. A
   request-access listing may defer the share until the customer is approved.
8. Open **Marketplace > Provider console > Listings > Create listing**.
9. Under **General**, enter **DataAI ETL Spark Libraries**, select the Yanbor
   provider profile, choose **Consumers must request access**, and select either
   **Private exchange** or **Public Marketplace** after approval.
10. Under **Data assets**, select **Files** and **Notebooks**, then select the
    approved share. Do not select Models or MCP server for this library product.
11. Complete attributes and details from
    `Databricks\listing\DATABRICKS_MARKETPLACE_LISTING.md`. Add public,
    no-login documentation, privacy, license, and terms URLs.
12. Add final screenshots and sample notebooks, save a draft, and preview it.
13. From a separate consumer workspace, request access, approve the request,
    install the JARs, import and run every notebook, test governed outputs, and
    test revocation.
14. Complete Yanbor legal/security review, then publish or submit for
    Databricks review.

Official process:
https://docs.databricks.com/aws/en/marketplace/create-listing

## 3. AWS Marketplace

### Where and what to submit

Use **AWS Marketplace Management Portal > Products > Server > Create server
product > Container**. Submit a Marketplace-managed ECR image and delivery
instructions, not `DataAIETLAWS.zip`. The ZIP is the review/build kit.

### Submission steps

1. Register Yanbor LLC as an AWS Marketplace seller and complete tax and
   banking onboarding.
2. Confirm with AWS that the proposed EMR Serverless custom-image delivery is
   accepted for the selected offer and pricing model.
3. Complete the common release procedure and
   `AWS\PROVIDER_CHECKLIST.md`.
4. Choose an AWS-provided EMR Serverless Spark base image that matches the
   validated runtime. Build `AWS\container\Dockerfile` with immutable DataAI
   JARs while preserving the required entrypoint and runtime user.
5. Scan the image and confirm that it contains no Spark/Hadoop duplication,
   credentials, telemetry, or customer data.
6. In the Management Portal, create the container product ID and product code.
7. Complete product information, pricing, refund policy, EULA, availability,
   and repository information. The first accepted product has Limited
   visibility for testing.
8. Push the approved image to the AWS Marketplace-managed ECR repository and
   add an immutable product version and delivery option.
9. Supply EMR Serverless launch/configuration instructions, IAM prerequisites,
   listing copy, final media, support, privacy, terms, and release notes.
10. If the offer is paid, implement and validate the approved contract,
    entitlement, or metering model without adding customer-data telemetry.
11. In a separate allow-listed buyer account, subscribe, pull the image, create
    an EMR Serverless application, run representative quality and matrix jobs,
    upgrade, and cancel.
12. Resolve all AWS security findings, then request visibility change from
    Limited to Public.

Official process:
https://docs.aws.amazon.com/marketplace/latest/userguide/container-product-getting-started.html

## 4. Microsoft Marketplace

### Where and what to submit

Use Microsoft **Partner Center > Marketplace offers**. The current kit is an
offer-type and architecture review candidate. A raw JAR bundle or single
container is not a finished Azure Container offer; the documented Azure
Container path requires a functional Kubernetes application/CNAB package.

### Submission steps

1. Enroll Yanbor LLC in Microsoft Marketplace and establish the Partner Center
   marketplace account.
2. Review the non-service, embedded-library architecture with Microsoft and
   select an accepted offer type. Prefer a lead-generation/private-fulfillment
   route unless Yanbor chooses to build and support a real AKS application.
3. If Azure Container is approved, design, implement, and test a functional
   customer-run AKS application; do not submit the component image alone.
4. Complete the common release procedure and
   `Microsoft\PROVIDER_CHECKLIST.md`.
5. Build the Linux AMD64 component image from
   `Microsoft\container\Dockerfile` with immutable DataAI artifacts.
6. Create and validate the required CNAB bundle, push it to the primary-tenant
   Azure Container Registry, and use the version format required by the offer.
7. In Partner Center, choose **New offer**, select the approved offer type, and
   create a stable offer ID.
8. Complete offer setup, properties, availability, plans, pricing, listing
   copy, technical configuration, support, privacy, terms, final media, and
   reviewer instructions.
9. Select a preview audience and submit the draft for preview.
10. From the preview tenant, acquire and deploy the offer, verify library
    availability and customer control, run Spark workloads, upgrade, and remove
    the deployment.
11. Correct certification findings, select **Review and publish**, and publish
    only after Yanbor and Microsoft approval.

Official setup and publication:
https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-offer-setup
and
https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-app-test-publish

## 5. Oracle Cloud Marketplace

### Where and what to submit

Use Oracle Cloud Marketplace Publisher. Choose either an **OCI Application**
container listing after Oracle accepts the delivery model, or a lead-generation
listing that directs qualified customers to private JAR fulfillment. Do not
upload `DataAIETLOracle.zip` as the deployable product.

### Submission steps

1. Create the Oracle account, enroll Yanbor LLC in Oracle PartnerNetwork,
   complete the Oracle Cloud Marketplace Agreement, and register the publisher.
2. Confirm paid-listing eligibility and choose lead generation or OCI
   Application as the listing type.
3. Complete the common release procedure and
   `Oracle\PROVIDER_CHECKLIST.md`.
4. For a container listing, build and scan
   `Oracle\container\Dockerfile` with immutable release JARs.
5. Push the approved image to OCI Container Registry and create the associated
   Marketplace Publisher artifact.
6. Open the Publisher portal, select **Create Listing > OCI Application
   Listing**, and choose the approved package type and pricing model.
7. Complete listing details, system requirements, support, related documents,
   terms, release notes, final media, markets, and pricing.
8. Attach the approved artifact to a new listing revision.
9. Validate that a customer can place the licensed JARs in customer-controlled
   Object Storage and use them as OCI Data Flow Spark job dependencies.
10. Test acquisition, Spark execution, output control, upgrade, and removal in
    a separate OCI tenancy with no Yanbor credentials or hosted service.
11. Preview the listing, submit the revision for Oracle review, resolve
    findings, and publish only after approval.

Official process:
https://docs.oracle.com/en-us/iaas/Content/Marketplace/Tasks/creating-oci-application-listing.htm

## 6. Google Cloud Marketplace

### Where and what to submit

Use Google Cloud Marketplace **Producer Portal** and create a container image
product. The deployable artifact is the approved image copied into the
Marketplace registry; `DataAIETLGoogle.zip` is the provider review/build kit.

### Submission steps

1. Enroll Yanbor LLC as a Google Cloud Marketplace partner and complete
   business, legal, technical, and Project Info onboarding.
2. In Producer Portal, select **Add product > Container image** and obtain the
   product service name.
3. Complete the common release procedure and
   `Google\PROVIDER_CHECKLIST.md`.
4. Replace `<SERVICE_NAME>` in the Dockerfile annotation with
   `services/<actual-service-name>` as required by Google.
5. Build an immutable image from `Google\container\Dockerfile`, scan it, and
   push the approved tag to the designated staging Artifact Registry or `gcr.io`
   repository.
6. In Producer Portal, complete **Product details** and **Container images**;
   select the staged tag and configure Google to copy it into the Marketplace
   registry.
7. Complete pricing, regions, support, privacy, terms, documentation, listing
   copy, release notes, icon, and final screenshots.
8. Select **Save and Validate** and resolve every automated validation result.
9. Preview the product, then test subscription and image access from a separate
   buyer project.
10. Copy the delivered JARs to customer-controlled Cloud Storage and execute
    representative Dataproc quality, analytics, matrix, and explicit-write jobs.
11. Submit the technical components and product details for partner-engineering
    review, resolve findings, and publish only after approval.

Official process:
https://docs.cloud.google.com/marketplace/docs/partners/container-setup

## 7. Maven Central

### Where and what to submit

Use the Sonatype **Central Publisher Portal**. Maven Central is a public,
permanent component repository, not a billing marketplace. Do not upload the
current `DataAIETLMaven.zip`; create a compliant release deployment bundle from
immutable artifacts after Yanbor authorizes public distribution.

### Submission steps

1. Create the Yanbor Central Publisher Portal account and verify a namespace
   controlled by Yanbor LLC. Do not assume that `com.dataai` is verifiable.
2. Confirm that permanent public binary, source, Javadoc, POM, and license
   availability is compatible with the commercial model.
3. Complete the common release procedure and
   `Maven\PROVIDER_CHECKLIST.md`.
4. Add required POM name, description, project URL, license, developer, and SCM
   metadata to every public module.
5. Produce a binary, sources, and Javadoc JAR for every non-POM artifact.
6. Sign each POM and JAR with the approved Yanbor PGP key and create the
   Central-required checksums.
7. Verify that all non-provided dependencies are already resolvable from
   Central and that Spark/Hadoop remain provided.
8. Resolve the release from a clean empty local Maven repository and execute a
   consumer Spark test.
9. Create the Central deployment bundle or use the Central Publishing Maven
   Plugin with automatic publication disabled.
10. Upload to the Publisher Portal, wait for validation, inspect every result,
    and correct failures with a new release candidate.
11. After explicit Yanbor approval, publish. A released coordinate cannot be
    replaced; corrections require a new version.

Official requirements and portal:
https://central.sonatype.org/publish/requirements/ and
https://central.sonatype.org/publish/publish-portal-guide/

## 8. NuGet

### Where and what to submit

The recommended commercial route is an authenticated private NuGet feed. The
two packages are:

- `NuGet\packages\Yanbor.DataAI.Etl.Spark.<version>.nupkg`
- `NuGet\packages\Yanbor.DataAI.Etl.Spark.Runtime.<version>.nupkg`

Nuget.org is a public component repository, not a billing marketplace. Do not
publish the current evaluation packages there as production releases.

### Private-feed publication steps

1. Replace the embedded `SNAPSHOT` JARs and both NuGet prerelease versions with
   one approved immutable release.
2. Validate Java/Spark/Scala compatibility and the .NET 8 helper from a clean
   consumer. Do not claim direct C# DataFrame extensions unless a separately
   tested JVM bridge is implemented.
3. Complete metadata, repository/license/readme links, package checksums, SBOM,
   signing policy, and commercial approval.
4. Create a private feed and a least-privilege publishing identity.
5. Push the Runtime package first, then the helper package, because the helper
   depends on Runtime.
6. Restore both packages from a clean machine using a read-only customer
   identity and execute a representative Spark job.
7. Provide customers the feed URL, source name, exact version, checksum, and
   credential-rotation instructions.

### Optional nuget.org steps

1. Complete the private-feed procedure and approve permanent anonymous access.
2. Create the Yanbor organization/account on nuget.org and configure package
   ownership and multifactor authentication.
3. Reserve/verify package IDs as applicable and create a scoped API key or use
   trusted publishing where supported.
4. Upload the Runtime package and wait for validation/indexing, then upload the
   helper package.
5. Install from nuget.org in a clean project and verify package contents and
   dependency resolution.

Official process:
https://learn.microsoft.com/en-us/nuget/nuget-org/publish-a-package

## 9. Tableau Exchange

### Where and what to submit

Submit the free Accelerator
`Tableau\accelerator\DataAI_ETL_Accelerator.twbx` through the managed
Salesforce Partner/Tableau Exchange process. `DataAIETLTableau.zip` is the
partner review kit, not the public Accelerator download. The commercial Spark
library is fulfilled separately; Tableau Exchange Accelerators are offered at
no additional charge.

### Submission steps

1. Confirm that Yanbor LLC is a managed Salesforce Partner. Only managed
   partners can contribute Accelerators to Tableau Exchange.
2. Work with the assigned partner account manager to obtain the current intake,
   content, brand, and review requirements.
3. Complete the common release procedure and the checklist in
   `Tableau\listing\TABLEAU_EXCHANGE_LISTING.md`.
4. Open `DataAI_ETL_Accelerator.twbx` in every advertised Tableau Desktop
   version. Validate rendering, interactions, filters, accessibility, embedded
   fictional data, and data-source replacement.
5. Connect a copy to actual governed DataAI Spark SQL and Databricks output
   tables and validate refreshes, relationships, permissions, and row-level
   security.
6. Resave the workbook with the final supported Tableau version and regenerate
   checksums.
7. Replace preview images with screenshots from the validated workbook.
8. Give the partner account manager the TWBX, listing copy, icon, screenshots,
   installation/data-replacement guide, public support/privacy/terms/license
   URLs, and function/output mapping.
9. Clearly state that the Accelerator is free, contains fictional data, and
   does not itself grant a production DataAI Spark license.
10. Address Tableau review findings, retest the final TWBX, and authorize the
    listing only after Yanbor approval.

If Yanbor is not a managed partner, Tableau Public can host a workbook, but it
is not a substitute for an eligible Tableau Exchange submission.

Official process:
https://help.tableau.com/current/pro/desktop/en-us/accelerators_build.htm

## 10. InterSystems Open Exchange

### Where and what to submit

Use the InterSystems Open Exchange **Developer portal > All applications > New
Application** flow. The listing's call-to-action should point to a controlled
evaluation page or `IRIS\distribution\DataAI_ETL_IRIS_Evaluation.zip` hosted
under Yanbor's terms. Do not publish a licensed production JAR or JDBC driver.

### Submission steps

1. Create an InterSystems Developer Community/Open Exchange account and finish
   the public developer/company profile.
2. Complete the common release procedure and the checklist in
   `IRIS\listing\INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md`.
3. Test the exact advertised IRIS server, namespace, JDBC driver, Java, Spark,
   read, partitioning, batch write, retry, and failure behavior.
4. Publish stable public documentation, evaluation license, support, privacy,
   terms, and controlled demonstration URLs.
5. In the Developer portal, select **All applications > New Application**.
6. Enter the application name and logo; select the category, InterSystems
   technology, industries, AI/ML flags, and tags.
7. Enter the call-to-action, about, and license URLs. Commercial licensing is
   allowed, so do not label DataAI ETL as open source.
8. Enter short and full descriptions from
   `IRIS\listing\INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md`, then add demo,
   documentation, support, article, and video URLs as available.
9. Leave **Publish in Package Manager** off unless the free bootstrap
   `IRIS\ipm\module.xml` has been tested from a public GitHub/GitLab repository
   and contains no commercial JAR.
10. Save the draft, preview it, enter the first release version and release
    notes, and select **Send for Approval**.
11. Resolve reviewer findings and verify the published call-to-action and
    download checksum.

Official process:
https://docs.openexchange.intersystems.com/apps/submit/

## 11. Alteryx Marketplace

### Where and what to submit

Use the Alteryx Marketplace Creator Portal and create a **Custom Tool** Add-On.
The upload artifact is an immutable, validated `.yxi`, not
`DataAIETLAlteryx.zip`. The root ZIP is the provider submission kit.

### Submission steps

1. Confirm Yanbor LLC is an Alteryx Partner and that the company has approved
   Creator Portal access through Alteryx SSO.
2. Assign business, technical, security, legal, and monitored support owners;
   accept the current Marketplace Creator Terms.
3. Complete the common release procedure and every item in
   `Alteryx\PROVIDER_CHECKLIST.md`.
4. Build the final UI and YXI, replace all `SNAPSHOT` JARs, and run
   `Alteryx\scripts\validate_alteryx_package.py`.
5. Install and execute the exact YXI on clean Alteryx Designer 2026.1 with AMP.
   If Server support is claimed, test every execution worker separately.
6. Replace design previews with screenshots from the validated release and
   archive the test workflow, output evidence, scans, SBOM, and checksum.
7. Sign in to the Creator Portal, create a new Add-On draft, and select
   **Custom Tool**.
8. Fill **Basic Information**, **Overview**, **Benefits**, **Features**, **Help
   & Support**, and **Resources** using
   `Alteryx\listing\ALTERYX_MARKETPLACE_LISTING.md`.
9. Add an edition named **Designer 2026.1 Evaluation**, declare Windows 64-bit,
   AMP, Java 17, Spark 3.5, Scala 2.12, embedded Python compatibility, and any
   Server limitation.
10. Upload the immutable YXI as the edition version; add release notes and its
    SHA-256 value.
11. In reviewer notes, provide the sample workflow, expected results,
    architecture, no-service/no-telemetry statement, subprocess controls,
    overwrite disclosure, dependency scans, test evidence, and support contact.
12. Preview the listing and submit it for Marketplace verification and security
    scans.
13. Address findings with a new immutable version and new checksum; never
    silently replace an uploaded file.
14. After publication, download the public artifact, verify its hash, and
    maintain a Designer/embedded-Python compatibility matrix.

Official process:
https://help.alteryx.com/marketplace/en/marketplace-creator-portal.html

## Final provider sign-off record

Before any listing is made public, record the following for the exact release:

- immutable version and Git/source revision;
- artifact and container digests;
- full Maven and package-validator results;
- supported-platform test evidence;
- dependency scan and SBOM;
- license, privacy, terms, support, and pricing approvals;
- marketplace/provider approval identifier;
- clean buyer installation result;
- release owner and publication date.

No file in the present August 9, 2026 audit has completed that production
sign-off.
