# Release Gates for Google Cloud Marketplace

The generated package is complete for internal review and evaluation packaging, but it is not authorized for external marketplace publication.

1. Complete Google Cloud Marketplace partner onboarding and Producer Portal access.
2. Replace SNAPSHOT artifacts with an immutable production release.
3. Obtain the product service name and add the required OCI image annotation.
4. Build, scan, stage, and validate the image in Google's required registry workflow.
5. Test Dataproc compatibility, pricing, support, and private-offer behavior.

The `submissionReady` field in `manifest.json` must remain `false` until all gates are evidenced, the package is regenerated from immutable artifacts, and Yanbor LLC authorizes publication.
