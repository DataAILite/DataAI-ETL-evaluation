# AWS Marketplace Submission Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

**Recommended offer type:** Linux container product for Amazon EMR Serverless

## Product boundary

Use a Linux container delivery option built from an approved Amazon EMR Serverless Spark base image. DataAI JARs are added to the image while EMR remains the runtime.

The raw DataAI JAR bundle is not assumed to be an accepted marketplace product type. The current SNAPSHOT build is for evaluation and reviewer preparation only. Do not submit it as a production release.

## Submission steps

1. Register Yanbor LLC as an AWS Marketplace seller and complete tax and banking onboarding.
2. Create a new container product and its AWS Marketplace-managed ECR repositories.
3. Choose a supported EMR Serverless Spark base image matching the qualified DataAI runtime.
4. Build the container with `--build-arg BASE_IMAGE=<approved-image>` and an immutable DataAI release.
5. Scan the image, verify non-root/runtime behavior, and push it to the assigned Marketplace ECR repository.
6. Create a container-image delivery option and supply complete EMR Serverless launch instructions.
7. Enter the listing copy, support/privacy/terms URLs, pricing, regions, logo, and screenshots.
8. Test subscription, image pull, EMR application creation, Spark job execution, upgrades, and cancellation in a buyer account.
9. Submit for AWS review and address security or metadata findings before publishing.

## Files supplied by this kit

- Listing copy: `listing/AWS_LISTING.md`
- Provider gates: `PROVIDER_CHECKLIST.md`
- Customer installation: `docs/INSTALLATION_AND_USAGE.md`
- Release blockers: `docs/RELEASE_GATES.md`
- Function inventory: `docs/FUNCTION_CATALOG.md`
- Evaluation download: `distribution/DataAI_ETL_AWS_Evaluation.zip`
- Integrity checks: `CHECKSUMS.sha256`

## External references

Marketplace requirements change. Recheck these official sources on the submission date:

- `https://docs.aws.amazon.com/marketplace/latest/userguide/container-based-products.html`
- `https://docs.aws.amazon.com/marketplace/latest/userguide/container-product-policies.html`
- `https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/application-custom-image.html`
