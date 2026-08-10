# Microsoft Marketplace Submission Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

**Recommended offer type:** Azure Container / Kubernetes application review candidate

## Product boundary

Use this kit for Partner Center review and offer-type selection. Azure Container offers require a Kubernetes application packaged as CNAB; a raw JAR or single container is not accepted.

The raw DataAI JAR bundle is not assumed to be an accepted marketplace product type. The current SNAPSHOT build is for evaluation and reviewer preparation only. Do not submit it as a production release.

## Submission steps

1. Enroll Yanbor LLC in Microsoft Marketplace through Partner Center.
2. Review the library-only architecture with Microsoft and select Azure Container, Azure Application, VM, or a lead-generation path.
3. If Azure Container is approved, design a functional customer-run AKS application; single containers are unsupported.
4. Build the Linux AMD64 component image from `container/Dockerfile` using immutable DataAI artifacts.
5. Create and validate a CNAB bundle, publish it to the primary-tenant ACR, and use a numeric `#.#.#` tag.
6. Configure the offer, plan, technical assets, markets, pricing, listing copy, URLs, logos, and screenshots.
7. Test the preview audience deployment, library availability, customer control, upgrades, and removal.
8. Confirm that public Microsoft ACR distribution is compatible with DataAI licensing and IP policy.
9. Submit for certification only after legal, security, and runtime approval.

## Files supplied by this kit

- Listing copy: `listing/MICROSOFT_LISTING.md`
- Provider gates: `PROVIDER_CHECKLIST.md`
- Customer installation: `docs/INSTALLATION_AND_USAGE.md`
- Release blockers: `docs/RELEASE_GATES.md`
- Function inventory: `docs/FUNCTION_CATALOG.md`
- Evaluation download: `distribution/DataAI_ETL_Microsoft_Evaluation.zip`
- Integrity checks: `CHECKSUMS.sha256`

## External references

Marketplace requirements change. Recheck these official sources on the submission date:

- `https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-offer-setup`
- `https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-technical-assets-kubernetes`
- `https://learn.microsoft.com/en-us/partner-center/marketplace-offers/azure-container-plan-technical-configuration-kubernetes`
