# DataAI ETL IRIS Marketplace Submission Kit

This folder is the complete working kit for an InterSystems Open Exchange
submission. It is not a single production deployment package and contains no
credentials or InterSystems JDBC driver.

**Publisher:** Yanbor LLC, provider of the DataAI product.

## Files to use in Open Exchange

| Open Exchange purpose | Included file |
| --- | --- |
| Listing title, descriptions, categories, tags, CTA, URLs, and checklist | `listing/INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md` |
| Primary square logo | `assets/dataai-iris-icon.png` |
| Editable vector logo | `assets/dataai-iris-icon.svg` |
| Product screenshots | `screenshots/iris-pipeline.png`, `screenshots/iris-data-quality.png` |
| Controlled demonstration download | `distribution/DataAI_ETL_IRIS_Evaluation.zip` |
| Product documentation | `README.md`, `mapping/`, and `examples/` |
| Evaluation license | `LICENSE.md` |
| Sample commercial terms | `COMMERCIAL_LICENSE_TEMPLATE.md` |
| Third-party disclosure | `THIRD_PARTY_NOTICES.md` |
| Optional public IPM bootstrap | `ipm/module.xml`, `ipm/src/`, and `ipm/README.md` |
| Integrity verification | `CHECKSUMS.sha256` |

The complete adapter source, tests, build descriptor, generation scripts, and
verified adapter JAR are included for review. The commercial production JAR
must still be fulfilled privately under signed commercial terms.

## Before submission

1. Replace every bracketed URL in
   `listing/INTERSYSTEMS_OPEN_EXCHANGE_LISTING.md`.
2. Publish stable public documentation, license, support, privacy, terms, and
   demonstration URLs.
3. Test the exact advertised IRIS server, namespace, JDBC driver, Java, and
   Spark versions.
4. Confirm whether the free IPM bootstrap will be published from a public
   GitHub or GitLab repository; never place a licensed production JAR in it.
5. Verify `CHECKSUMS.sha256`, preview the listing, and send it for approval.

Current Open Exchange submission reference:
`https://docs.openexchange.intersystems.com/apps/submit/`.

DataAI software is provided **AS IS**, with no obligations except those
expressly accepted in a signed commercial agreement or order form.
