# Release Gates for Microsoft Marketplace

The generated package is complete for internal review and evaluation packaging, but it is not authorized for external marketplace publication.

1. Select an accepted Azure offer type that does not misrepresent DataAI as SaaS.
2. Replace SNAPSHOT artifacts with an immutable production release.
3. Build a functional AKS application and CNAB if the Azure Container route is approved.
4. Approve public-registry exposure of proprietary container layers before using that route.
5. Complete Partner Center certification, pricing, privacy, and support requirements.

The `submissionReady` field in `manifest.json` must remain `false` until all gates are evidenced, the package is regenerated from immutable artifacts, and Yanbor LLC authorizes publication.
