# Databricks Marketplace Submission

**Publisher:** Yanbor LLC, provider of the DataAI product.

## Recommended listing

Create a personalized Databricks Marketplace listing named **DataAI ETL Spark
Libraries**. Require provider approval before fulfillment. This allows Yanbor
LLC and the customer to complete evaluation terms, runtime qualification, and
commercial discussions before production artifacts are delivered.

The shared evaluation assets are:

- Importable notebooks demonstrating quality, analytics, market, matrix, and
  governed-output workflows.
- Fictional CSV data with deliberate quality conditions.
- Evaluation JARs for Java 17, Spark 3.5.x, and Scala 2.12.
- Installation, compatibility, security, licensing, and function documentation.

Do not include license keys, repository credentials, customer agreements,
production customer data, or private Maven tokens in a Marketplace share.

## Submission file map

| Provider need | Included asset |
| --- | --- |
| Listing fields and copy | `listing/DATABRICKS_MARKETPLACE_LISTING.md` |
| Provider checklist | `PROVIDER_CHECKLIST.md` |
| Square DataAI icon | `assets/dataai-databricks-icon.png` |
| Editable artwork | `assets/dataai-databricks-icon.svg` |
| Listing previews | `screenshots/databricks-quality.png`, `screenshots/databricks-matrix.png` |
| Customer evaluation package | `distribution/DataAI_ETL_Databricks_Evaluation.zip` |
| Shared-volume payload | `lib/`, `data/`, `docs/` |
| Sample notebooks | `notebooks/` |
| Provider SQL template | `sql/CREATE_PROVIDER_ASSETS.sql` |
| Consumer SQL template | `sql/CREATE_CONSUMER_OUTPUTS.sql` |
| Cluster/Job templates | `configs/` |
| Evaluation terms | `LICENSE.md` |
| Commercial terms sample | `COMMERCIAL_LICENSE_TEMPLATE.md` |
| Third-party disclosure | `THIRD_PARTY_NOTICES.md` |
| Integrity checks | `CHECKSUMS.sha256`, repository-root sidecar |

## Provider workflow

1. Apply to the Databricks Data Partner Program for public listings, or use the
   provider-console self-service workflow for private-exchange-only delivery.
2. Use a Premium-or-higher workspace enabled for Unity Catalog and assign the
   Marketplace admin role.
3. Create and approve the Yanbor LLC provider profile. Supply public support,
   privacy, terms, documentation, and company URLs.
4. Replace every bracketed placeholder in
   `listing/DATABRICKS_MARKETPLACE_LISTING.md`.
5. Run the complete DataAI Maven reactor and the Databricks package generator
   and validator. Archive the clean validation output.
6. In the provider workspace, adapt and execute
   `sql/CREATE_PROVIDER_ASSETS.sql` using provider-controlled catalog, schema,
   and volume names.
7. Upload `lib/`, `data/`, `docs/`, and the evaluation ZIP to the provider
   volume. Import the source notebooks into the provider workspace.
8. Create an OpenSharing share containing the approved evaluation volume and
   sample notebooks. A personalized listing may omit its share until customer
   approval and business terms are complete.
9. In Marketplace > Provider console > Listings, select **Create listing**.
   Choose Public Marketplace or a private exchange and enter the copy from the
   listing file.
10. Select **Files** and **Notebooks** as the data asset types, then select the
    approved share. Do not select models or MCP server unless the product is
    intentionally expanded and separately reviewed.
11. Set fulfillment to require provider approval. Add the evaluation license,
    privacy, terms, support, and documentation URLs.
12. Upload the DataAI icon and final screenshots. The included PNGs are design
    previews, not Databricks screenshots; replace them with captures from an
    actually validated workspace before submission.
13. Test the consumer experience from a separate Unity Catalog-enabled
    workspace: request, approval, asset access, JAR installation, notebook
    import, all examples, output persistence, revocation, and documentation.
14. Complete Yanbor legal, security, brand, compatibility, and support review,
    then publish or submit the listing for Databricks review.

## Required external validation

Before submission, execute every notebook on the selected supported
Databricks Runtime and access mode. Validate:

- JAR installation from the shared Unity Catalog volume.
- Standard-access-mode allowlist behavior.
- Java 17, Spark 3.5.x, and Scala 2.12 compatibility.
- Quality routing and output schemas.
- Matrix convergence metadata and control totals.
- Explicit Delta writes and Unity Catalog permissions.
- Job restart behavior and cluster-library installation.
- No Spark or Hadoop classes bundled in DataAI JARs.

## Commercial boundary

The Marketplace evaluation assets do not grant production rights. After a
commercial agreement, deliver a non-SNAPSHOT, immutable DataAI release through
an authenticated private Maven repository or an approved customer artifact
channel. Keep entitlement records outside the JARs and do not add remote
license checks or customer-data transmission without separate approval.

Official process references must be rechecked at submission time:

- `https://docs.databricks.com/aws/en/marketplace/get-started-provider`
- `https://docs.databricks.com/aws/en/marketplace/create-listing`
- `https://docs.databricks.com/aws/en/marketplace/private-exchange`
- `https://docs.databricks.com/aws/en/libraries/`
- `https://docs.databricks.com/aws/en/files/files-recommendations`
