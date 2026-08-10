# Release Gates for Maven Central

The generated package is complete for internal review and evaluation packaging, but it is not authorized for external marketplace publication.

1. Verify a Yanbor-controlled groupId namespace; do not assume `com.dataai` is publishable.
2. Replace SNAPSHOT with an immutable release consistently in POMs, bytecode metadata, and filenames.
3. Complete POM URL, license, developer, SCM, and dependency metadata.
4. Generate binary, source, and Javadoc JARs and sign every deployable file with a Yanbor PGP key.
5. Validate the Central bundle without uploading, then obtain explicit publication approval.

The `submissionReady` field in `manifest.json` must remain `false` until all gates are evidenced, the package is regenerated from immutable artifacts, and Yanbor LLC authorizes publication.
