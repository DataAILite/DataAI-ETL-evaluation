# Provider Release Checklist

Artifact: `DataAI ETL for Alteryx 0.1.0-SNAPSHOT`

This checklist is intentionally incomplete. Do not change `submissionReady` to
true until every required item is checked and evidence is retained.

## Business, legal, and support

- [ ] Yanbor LLC Alteryx Partner and Creator Portal access confirmed.
- [ ] Current Marketplace Creator Terms reviewed and accepted by authorized
      company representative.
- [ ] `LICENSE.md` approved by counsel for evaluation distribution.
- [ ] Commercial agreement approved by counsel.
- [ ] Monitored support email, public support URL, response targets, and owner
      entered in the listing.
- [ ] Privacy/data-handling statement approved.

## Immutable build

- [ ] All DataAI artifacts use an immutable non-SNAPSHOT version.
- [ ] Full Maven reactor passes with Java 17 and the recorded Maven version.
- [ ] YXI built with AYX Plugin CLI 1.3.2 and AYX Python SDK 2.5.3 for Python
      3.13.
- [ ] JAR, YXI, evaluation ZIP, and submission ZIP SHA-256 values recorded.
- [ ] Dependency, secret, malware, license, and vulnerability scans pass or
      approved exceptions are documented.

## Designer 2026.1 validation

- [ ] Clean Windows/Designer 2026.1 test machine identified.
- [ ] YXI installs for a standard user.
- [ ] DataAI ETL category, tool, icon, and configuration UI render correctly.
- [ ] Workflow requires AMP and runs successfully.
- [ ] License acceptance is required.
- [ ] Successful local or approved cluster `spark-submit` run verified.
- [ ] Status anchor emits one successful row without customer data or raw logs.
- [ ] Normalization, profiling, validation, findings, and rejection verified.
- [ ] Minimum-score failure verified.
- [ ] Spark executable error, nonzero exit, and timeout paths verified.
- [ ] Selected output tables are overwritten and no unselected table changes.
- [ ] Temporary configuration is removed after success and failure.
- [ ] No traffic to Yanbor LLC occurs during execution.

## Server validation, if listed

- [ ] YXI installed on every approved Server worker.
- [ ] Service identity can access Java, Spark, catalog, connectors, and output
      locations with least privilege.
- [ ] Scheduled and Gallery execution verified.
- [ ] Server logs, concurrency, cancellation, and timeout behavior verified.

## Listing and review evidence

- [ ] Design previews replaced with actual tested-release screenshots.
- [ ] Listing claims match actual tool surface and compatibility evidence.
- [ ] Review workflow, sample data, expected output, and reviewer instructions
      execute successfully.
- [ ] Security architecture, dependency inventory, scan reports, and checksums
      attached to review notes.
- [ ] `externalDesignerValidation`, any Server flag, and `submissionReady` set
      true only after approval.

## Sign-off

- Technical owner/date: _________________________________________________
- Security reviewer/date: _______________________________________________
- Legal reviewer/date: __________________________________________________
- Business owner/date: __________________________________________________
