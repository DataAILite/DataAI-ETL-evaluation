# Oracle Cloud Marketplace Provider Checklist

## Channel-specific gates

- [ ] Complete OCI partner and Marketplace Publisher onboarding.
- [ ] Choose lead generation or a supported OCI application package type.
- [ ] Replace SNAPSHOT artifacts and validate OCI Data Flow compatibility.
- [ ] Build, scan, and upload the container artifact to OCI Publisher when using a container listing.
- [ ] Complete paid-listing eligibility, terms, support, and regional availability review.

## Common legal and product gates

- [ ] Yanbor LLC publisher identity, tax, banking, and partner enrollment are approved.
- [ ] Evaluation and commercial terms have completed legal review.
- [ ] Public support, privacy, terms, documentation, and company URLs are live.
- [ ] All placeholders are replaced and listing claims match tested behavior.
- [ ] No listing describes DataAI as a hosted service.

## Artifact and security gates

- [ ] Full Maven `clean verify` passes with Java 17.
- [ ] Production version is immutable and does not end in `-SNAPSHOT`.
- [ ] SHA-256 checksums and any channel-required signatures pass.
- [ ] JARs contain no bundled Spark or Hadoop classes.
- [ ] Container or repository artifacts contain no credentials, keys, tokens, customer data, or signed agreements.
- [ ] Vulnerability, malware, dependency, and license reviews are current.
- [ ] Installation, upgrades, rollback, and revocation are tested in a separate buyer environment.

## Publication authorization

- [ ] Pricing and fulfillment match the signed DataAI commercial model.
- [ ] Yanbor LLC authorizes the exact final files and external submission.
