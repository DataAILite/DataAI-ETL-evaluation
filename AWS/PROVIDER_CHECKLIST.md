# AWS Marketplace Provider Checklist

## Channel-specific gates

- [ ] Replace the SNAPSHOT build with an immutable production release.
- [ ] Build and scan AMD64 and any claimed ARM64 images in AWS Marketplace-managed ECR.
- [ ] Validate the selected EMR release, Java, Spark, Scala, IAM, and job behavior.
- [ ] Select BYOL, contract, or supported pricing and complete seller review.
- [ ] Provide fully self-service usage instructions without external paid dependencies.

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
