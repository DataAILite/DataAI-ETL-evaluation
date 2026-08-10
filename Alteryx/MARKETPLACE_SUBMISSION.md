# Alteryx Marketplace Submission Procedure

This kit is prepared for the Alteryx Marketplace Creator Portal, but its
manifest intentionally says `submissionReady: false` until the provider gates
are complete.

Official references:

- Creator Portal: https://help.alteryx.com/marketplace/en/marketplace-creator-portal.html
- Verification Standards: https://help.alteryx.com/marketplace/en/alteryx-verification-standards.html
- Marketplace FAQ: https://help.alteryx.com/marketplace/en/frequently-asked-questions.html
- Submit an Add-On: https://marketplace.alteryx.com/en-US/apps/419011/submit-an-add-on
- AYX Plugin CLI: https://help.alteryx.com/current/en/developer-help/platform-sdk/ayx-plugin-cli.html
- Marketplace Creator Terms: https://www.alteryx.com/wp-content/uploads/media/legal/marketplace-creator-terms.pdf

## 1. Establish the provider account

1. Confirm Yanbor LLC is enrolled as an Alteryx Partner.
2. Create or use the company's Alteryx SSO identity.
3. Confirm the account can access Marketplace Creator Portal.
4. Assign a business owner, technical owner, security reviewer, legal reviewer,
   and monitored support contact.
5. Review and accept the current Marketplace Creator Terms for Yanbor LLC.

The listing must be submitted by the company, not an individual acting outside
the provider organization.

## 2. Finish the release candidate

1. Replace SNAPSHOT JARs with immutable commercial-candidate versions.
2. Run `scripts/generate_alteryx_assets.py`.
3. Build the React UI with `npm ci` and `npm run build` in
   `yxi-source/ui/DataAiEtlQuality`.
4. Download the official Python 3.13 AYX Python SDK dependencies and run
   `scripts/build_alteryx_package.py`.
5. Run `scripts/validate_alteryx_package.py` and the full DataAI Maven reactor.
6. Install and execute the YXI in clean Designer 2026.1 and, if listed,
   Alteryx Server.
7. Complete every item in `PROVIDER_CHECKLIST.md`.
8. Replace design previews with actual tested-release screenshots.
9. Regenerate archives and checksums after every change.

## 3. Create the listing draft

1. Sign in to the Creator Portal.
2. Create a new Add-On draft.
3. Select **Custom Tool** as the primary type.
4. Enter the listing and provider names from
   `listing/ALTERYX_MARKETPLACE_LISTING.md`.
5. Enter the overview, benefits, features, requirements, security disclosure,
   support details, and documentation links.
6. State clearly that the Marketplace download is an evaluation license and
   production rights require a separate agreement with Yanbor LLC.
7. Do not describe the build as certified, verified, or production-ready until
   Alteryx review and provider validation are complete.

## 4. Add media and resources

1. Upload the final square logo.
2. Upload actual Designer screenshots with no preview label.
3. Add installation, usage, security, compatibility, privacy/data handling,
   and support resources.
4. Add a link to the evaluation license before the download action.
5. Verify every support URL and monitored email address.

## 5. Create the edition and version

1. Add an edition named **Designer 2026.1 Evaluation**.
2. Declare Windows 64-bit, AMP, embedded Python 3.13.11, Java 17, Spark 3.5,
   Scala 2.12, and Delta prerequisites.
3. Upload the validated immutable `.yxi` version file—not this SNAPSHOT
   candidate.
4. Add release notes and the file SHA-256 value.
5. Add any Server limitation and separate Server validation evidence.
6. Do not claim support for 2024.1–2025.2 or older releases without separate
   Python-generation builds and tests.

## 6. Supply review notes

Provide Alteryx reviewers with:

- test workflow and isolated sample data;
- step-by-step expected outputs;
- license and production-right explanation;
- architecture and data-flow description;
- explicit no-service/no-telemetry statement;
- subprocess security controls (`shell=False`, executable allow-list, fixed
  DataAI main class);
- output overwrite disclosure;
- dependency inventory and scan reports;
- Designer/Server test evidence and checksums;
- a direct support contact for review questions.

## 7. Submit and respond to review

1. Run the Creator Portal preview and correct all missing fields.
2. Submit the Add-On for Marketplace verification.
3. Track status in the portal.
4. Respond to verification and security findings with a new immutable version.
5. Re-run all checks and update release notes/checksums for every replacement.
6. Do not silently replace an uploaded artifact.

## 8. Publish and operate

1. Confirm the public page, download, license, docs, and support routes.
2. Download the public artifact and verify its hash.
3. Maintain a version/Designer compatibility matrix.
4. Triage security and compatibility updates.
5. Publish new editions when Alteryx embedded Python changes.
6. Keep Marketplace evaluation downloads free unless Alteryx introduces and
   approves a transaction mechanism; monetize production rights through the
   signed Yanbor LLC commercial license.
