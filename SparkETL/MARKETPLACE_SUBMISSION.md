# Spark Library Marketplace Submission

**Publisher:** Yanbor LLC, provider of the DataAI product.

The repository-root `SparkETL.zip` is a review and fulfillment kit for the DataAI ETL Spark
libraries. Apache Spark does not operate a single commercial marketplace for
third-party JARs, so use the channel matching the intended transaction.

## Recommended channel strategy

| Purpose | Recommended channel | Boundary |
| --- | --- | --- |
| Paid production delivery | Authenticated private Maven repository | Best match for licensed customer-side libraries |
| Public evaluation/discovery | Yanbor product page and controlled Maven repository | Preserve evaluation terms and customer qualification |
| Public Java artifact publication | Maven Central only after all release gates pass | Public, immutable repository; not a billing marketplace |
| Databricks discovery | Databricks partner/provider review with documentation or notebook assets | Do not claim a raw-JAR listing until Databricks approves that delivery model |
| AWS/Azure commercial procurement | Private offer or approved software product only after selecting a supported marketplace delivery type | Current library is not SaaS, AMI, VM, or container fulfillment |

## Submission file map

| Submission need | Included file or directory |
| --- | --- |
| Listing name, descriptions, tags, requirements, CTA, and URLs | `listing/SPARK_MARKETPLACE_LISTING.md` |
| Primary square logo | `assets/dataai-spark-icon.png` |
| Editable vector logo | `assets/dataai-spark-icon.svg` |
| Product previews | `screenshots/spark-pipeline.png`, `screenshots/spark-functions.png` |
| Evaluation download | `distribution/DataAI_ETL_Spark_Evaluation.zip` |
| Binary artifacts | `lib/` |
| Maven descriptors | `poms/` |
| Documentation | `README.md`, `docs/` |
| Examples | `examples/` |
| Reviewer/evaluation source | `source/` |
| Evaluation terms | `LICENSE.md` |
| Sample commercial terms | `COMMERCIAL_LICENSE_TEMPLATE.md` |
| Third-party disclosure | `THIRD_PARTY_NOTICES.md` |
| Integrity verification | `CHECKSUMS.sha256` |

## Maven Central publication gates

The included `0.1.0-SNAPSHOT` artifacts must not be uploaded as a release.
Before a public Central publication:

1. Choose and verify a namespace controlled by Yanbor LLC. The current
   `com.dataai` coordinate should be used only if Yanbor can verify that
   namespace; otherwise select a controlled domain-derived group ID and update
   Java packages consistently.
2. Replace `SNAPSHOT` with an immutable release version.
3. Complete POM project URL, description, license, developer, and SCM metadata.
4. Produce binary, source, and Javadoc JARs for every public module.
5. Create PGP signatures and Central-required checksums.
6. Ensure every non-provided dependency is already publicly resolvable.
7. Validate license presentation for public, anonymous downloads.
8. Test the release bundle in a clean repository before publication.

Official references:

- `https://maven.apache.org/repository/guide-central-repository-upload`
- `https://central.sonatype.org/publish/publish-portal-maven/`
- `https://spark.apache.org/docs/3.5.6/submitting-applications.html`

## Commercial boundary

Do not publish customer credentials, license certificates, private repository
tokens, production data, or signed customer agreements. Public marketplace
discovery must direct commercial customers to Yanbor LLC for licensed,
immutable artifact fulfillment.
