# Databricks Provider Checklist

## Organization and legal

- [ ] Yanbor LLC provider enrollment is approved.
- [ ] Marketplace admin is assigned in a Unity Catalog-enabled workspace.
- [ ] Provider name is exactly `Yanbor LLC`.
- [ ] Support, privacy, terms, documentation, and company URLs are public.
- [ ] Evaluation and commercial terms have completed legal review.
- [ ] All bracketed placeholders have been replaced.

## Artifact and runtime

- [ ] Artifact version is immutable and does not end in `-SNAPSHOT` for production.
- [ ] Java, Spark, Scala, and Databricks Runtime compatibility is documented.
- [ ] Full Maven `clean verify` passes from `spark/`.
- [ ] SHA-256 checksums match all delivered artifacts.
- [ ] JARs contain no bundled Spark or Hadoop classes.
- [ ] Runtime dependencies and third-party notices are reviewed.
- [ ] Standard and dedicated access modes are tested where claimed.

## Marketplace assets

- [ ] Provider Unity Catalog catalog, schema, volume, and share are approved.
- [ ] Only fictional evaluation data is included.
- [ ] Notebooks import and run in a separate consumer workspace.
- [ ] Listing descriptions and tags match the validated product.
- [ ] Final screenshots come from the validated Databricks workspace.
- [ ] Files and notebooks are the only selected asset types.
- [ ] Personalized fulfillment and approval behavior are tested.

## Security and privacy

- [ ] No credentials, tokens, secrets, customer data, or signed agreements exist in the share.
- [ ] No required DataAI telemetry, hosted service, or network callback exists.
- [ ] Volume permissions provide read-only consumer access where practical.
- [ ] Customers control compute, input data, outputs, catalogs, writes, and scheduling.
- [ ] Revocation and artifact-update procedures are tested.
- [ ] Vulnerability and dependency review is current.

## Publication

- [ ] Public or private-exchange audience is approved.
- [ ] Consumer request, approval, download, installation, and support flows pass.
- [ ] Databricks provider policies are reviewed on the submission date.
- [ ] Yanbor LLC authorizes the final Marketplace submission.
