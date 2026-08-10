# Maven Central Submission Procedure

**Publisher:** Yanbor LLC, provider of the DataAI product.

**Recommended offer type:** Maven Central pre-publication component bundle

## Product boundary

Use this as a release-engineering review kit. Maven Central is public, immutable, and not a billing marketplace; publish only after Yanbor approves public distribution and completes all release gates.

The raw DataAI JAR bundle is not assumed to be an accepted marketplace product type. The current SNAPSHOT build is for evaluation and reviewer preparation only. Do not submit it as a production release.

## Submission steps

1. Create a Central Publisher Portal account for Yanbor LLC and verify a controlled namespace.
2. Decide whether permanent public source/binary availability is compatible with the DataAI license strategy.
3. Create an immutable release branch/version; update all modules and runtime version reporting together.
4. Complete required POM metadata and configure the Central Publishing Maven Plugin.
5. Generate binary, source, and Javadoc JARs for each published module.
6. Sign every POM and JAR with an approved Yanbor PGP key and distribute the public key.
7. Run a clean build and consumer dependency-resolution test in an empty local repository.
8. Create a Central bundle with upload disabled and review validation results.
9. Publish only after explicit Yanbor approval; released components cannot be replaced in place.

## Files supplied by this kit

- Listing copy: `listing/MAVEN_LISTING.md`
- Provider gates: `PROVIDER_CHECKLIST.md`
- Customer installation: `docs/INSTALLATION_AND_USAGE.md`
- Release blockers: `docs/RELEASE_GATES.md`
- Function inventory: `docs/FUNCTION_CATALOG.md`
- Evaluation download: `distribution/DataAI_ETL_Maven_Evaluation.zip`
- Integrity checks: `CHECKSUMS.sha256`

## External references

Marketplace requirements change. Recheck these official sources on the submission date:

- `https://central.sonatype.org/publish/requirements/`
- `https://central.sonatype.org/publish/publish-portal-maven/`
- `https://central.sonatype.org/register/namespace/`
