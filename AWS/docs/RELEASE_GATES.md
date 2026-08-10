# Release Gates for AWS Marketplace

The generated package is complete for internal review and evaluation packaging, but it is not authorized for external marketplace publication.

1. Replace the SNAPSHOT build with an immutable production release.
2. Build and scan AMD64 and any claimed ARM64 images in AWS Marketplace-managed ECR.
3. Validate the selected EMR release, Java, Spark, Scala, IAM, and job behavior.
4. Select BYOL, contract, or supported pricing and complete seller review.
5. Provide fully self-service usage instructions without external paid dependencies.

The `submissionReady` field in `manifest.json` must remain `false` until all gates are evidenced, the package is regenerated from immutable artifacts, and Yanbor LLC authorizes publication.
