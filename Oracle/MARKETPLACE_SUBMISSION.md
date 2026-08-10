# Oracle Cloud Marketplace Submission Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

**Recommended offer type:** OCI application container image or lead-generation listing

## Product boundary

Start with an Oracle lead-generation listing for private JAR fulfillment, or use an OCI container image only after Oracle approves the library-delivery model and an immutable release.

The raw DataAI JAR bundle is not assumed to be an accepted marketplace product type. The current SNAPSHOT build is for evaluation and reviewer preparation only. Do not submit it as a production release.

## Submission steps

1. Enroll Yanbor LLC in Oracle PartnerNetwork and complete Marketplace Publisher onboarding.
2. Select a lead-generation listing for controlled private delivery or an OCI Application container listing.
3. Replace all placeholders and provide Oracle-required support, related documents, terms, and system requirements.
4. For a container listing, build and scan the Linux image from `container/Dockerfile` with immutable DataAI JARs.
5. Push the image to OCI Container Registry, create a Publisher artifact, and attach it to a listing revision.
6. Validate extraction or placement of JARs in customer-controlled Object Storage for OCI Data Flow jobs.
7. Upload the listing icon, banner, screenshots, release notes, documentation, and pricing plan.
8. Test launch and Spark execution in a separate OCI tenancy without Yanbor credentials or services.
9. Submit the listing revision for Oracle review and publish only after approval.

## Files supplied by this kit

- Listing copy: `listing/ORACLE_LISTING.md`
- Provider gates: `PROVIDER_CHECKLIST.md`
- Customer installation: `docs/INSTALLATION_AND_USAGE.md`
- Release blockers: `docs/RELEASE_GATES.md`
- Function inventory: `docs/FUNCTION_CATALOG.md`
- Evaluation download: `distribution/DataAI_ETL_Oracle_Evaluation.zip`
- Integrity checks: `CHECKSUMS.sha256`

## External references

Marketplace requirements change. Recheck these official sources on the submission date:

- `https://docs.oracle.com/en-us/iaas/Content/Marketplace/Tasks/creating-oci-application-listing.htm`
- `https://docs.oracle.com/en-us/iaas/Content/Marketplace/publishing_guidelines.htm`
- `https://docs.oracle.com/en-us/iaas/Content/Marketplace/become-oci-partner.htm`
