# Google Cloud Marketplace Submission Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

**Recommended offer type:** Container image product for customer-controlled Dataproc delivery

## Product boundary

Use a Google Cloud Marketplace container image as the licensed artifact carrier after partner approval, then place JARs in customer-controlled Cloud Storage for Dataproc jobs.

The raw DataAI JAR bundle is not assumed to be an accepted marketplace product type. The current SNAPSHOT build is for evaluation and reviewer preparation only. Do not submit it as a production release.

## Submission steps

1. Enroll Yanbor LLC as a Google Cloud Marketplace partner and complete the Project Info process.
2. Create the container image product in Producer Portal and obtain its service name.
3. Replace `<SERVICE_NAME>` in the Dockerfile label and use immutable DataAI artifacts.
4. Build and scan the image, then push approved tags to the staging `gcr.io` repository.
5. Configure Google to copy the selected tags into `marketplace.gcr.io`.
6. Enter listing copy, pricing, regions, support/privacy/terms URLs, icon, and screenshots.
7. Test subscription and image access from a buyer project, then copy JARs into customer-controlled Cloud Storage.
8. Execute representative Dataproc Spark jobs including matrix balancing and explicit output writes.
9. Submit for partner-engineering review and publish only after approval.

## Files supplied by this kit

- Listing copy: `listing/GOOGLE_LISTING.md`
- Provider gates: `PROVIDER_CHECKLIST.md`
- Customer installation: `docs/INSTALLATION_AND_USAGE.md`
- Release blockers: `docs/RELEASE_GATES.md`
- Function inventory: `docs/FUNCTION_CATALOG.md`
- Evaluation download: `distribution/DataAI_ETL_Google_Evaluation.zip`
- Integrity checks: `CHECKSUMS.sha256`

## External references

Marketplace requirements change. Recheck these official sources on the submission date:

- `https://docs.cloud.google.com/marketplace/docs/partners/container`
- `https://docs.cloud.google.com/marketplace/docs/partners`
