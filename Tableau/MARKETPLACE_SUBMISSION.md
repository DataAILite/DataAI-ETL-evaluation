# DataAI ETL Tableau Marketplace Submission Kit

This folder is the complete working kit for submitting the DataAI ETL Quality
Accelerator to Tableau Exchange. The intended listing type is an Accelerator,
not a custom connector.

**Publisher:** Yanbor LLC, provider of the DataAI product.

## Files to use for Tableau Exchange review

| Tableau Exchange purpose | Included file |
| --- | --- |
| Downloadable packaged workbook | `accelerator/DataAI_ETL_Accelerator.twbx` |
| Editable workbook source | `accelerator/DataAI_ETL_Accelerator.twb` |
| Accelerator installation and replacement instructions | `accelerator/README.md` |
| Listing copy, requirements, fields, tags, and checklist | `listing/TABLEAU_EXCHANGE_LISTING.md` |
| Primary square logo | `assets/dataai-tableau-icon.png` |
| Editable vector logo | `assets/dataai-tableau-icon.svg` |
| Product screenshots | `screenshots/executive-summary.png`, `screenshots/data-quality.png`, `screenshots/analytics.png` |
| Fictional evaluation data | `sample-data/` |
| Output and function mappings | `mapping/` |
| Spark/Databricks integration examples | `examples/` |
| Evaluation license | `LICENSE.md` |
| Sample commercial terms | `COMMERCIAL_LICENSE_TEMPLATE.md` |
| Third-party disclosure | `THIRD_PARTY_NOTICES.md` |
| Integrity verification | `CHECKSUMS.sha256` |

The complete adapter source, tests, build descriptor, generation scripts, and
verified adapter JAR are included for partner review. The production DataAI
Spark JAR is commercially fulfilled outside the free Accelerator download.

## Before submission

1. Confirm managed Salesforce Partner eligibility and coordinate requirements
   with the assigned partner account manager.
2. Open, render, and interaction-test the `.twbx` in each advertised Tableau
   Desktop version; resave it with the final supported version.
3. Verify that all embedded data remains fictional and credential-free.
4. Test replacement with governed Spark SQL or Databricks output tables.
5. Finalize listing URLs and support ownership in
   `listing/TABLEAU_EXCHANGE_LISTING.md`.
6. Regenerate and verify `CHECKSUMS.sha256` after any workbook change.

Current Tableau Accelerator submission reference:
`https://help.tableau.com/current/pro/desktop/en-us/accelerators_build.htm`.

DataAI software is provided **AS IS**, with no obligations except those
expressly accepted in a signed commercial agreement or order form.
