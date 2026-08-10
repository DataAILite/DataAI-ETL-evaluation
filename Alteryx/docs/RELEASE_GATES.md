# Release Gates

The following gates are mandatory before a Marketplace submission is marked
ready or a customer receives production rights:

1. Replace every `0.1.0-SNAPSHOT` JAR with an immutable, signed, non-SNAPSHOT
   build and regenerate every checksum.
2. Build the YXI with the official AYX Plugin CLI/AYX Python SDK toolchain for
   the exact declared Designer Python generation.
3. Install the YXI in a clean Alteryx Designer 2026.1 environment.
4. Verify the category, icon, UI values, license checkbox, AMP execution,
   output anchor, successful run, validation failure, Spark failure, and
   timeout behavior.
5. Verify output overwrite behavior with an isolated evaluation catalog.
6. Validate Java 17, Spark 3.5 / Scala 2.12, catalog connectors, and Delta.
7. Validate the same YXI on Alteryx Server workers if Server is listed.
8. Run dependency, malware, secret, license, and vulnerability scans.
9. Replace design-preview images with actual screenshots from the tested
   release build; remove preview labels.
10. Have counsel approve the evaluation and commercial licenses, Marketplace
    terms, privacy statements, and support commitments.
11. Complete `PROVIDER_CHECKLIST.md` with dates, versions, tester, evidence,
    and approval.
12. Only then set `externalDesignerValidation` and `submissionReady` to true.
