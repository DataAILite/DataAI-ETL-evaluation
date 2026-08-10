# Tableau Exchange Listing Package

**Publisher:** Yanbor LLC, provider of the DataAI product

## Recommended listing type

List **DataAI ETL Quality Accelerator** as a Tableau Accelerator (`.twbx`), not
as a connector. Tableau already provides native Spark SQL and Databricks
connectors, so a custom `.taco` would add maintenance and approval work without
improving the DataAI computation library.

The Exchange listing is the test-drive and discovery surface. The commercial
DataAI Spark/Java packages are delivered separately through DataAI's licensed
artifact repository or customer distribution channel. Do not put licensed
production JARs, license keys, credentials, or customer data inside the TWBX.

## Listing copy

### Name

DataAI ETL Quality Accelerator

### One-line description

Explore DataAI pipeline quality, rejected records, findings, and field health
in Tableau, then connect the dashboard to governed Spark or Databricks outputs.

### Detailed description

DataAI ETL Quality Accelerator gives data engineering, governance, and
analytics teams an immediate view of DataAI pipeline results. The included
fictional sample shows quality-score trends, accepted and rejected rows,
finding severity, and profiled-field completeness without requiring database
credentials.

After evaluation, replace the sample source with the standardized tables
created by the optional `dataai-spark-tableau` adapter. DataAI runs inside the
customer's Spark job; the customer controls storage, identity, scheduling,
network access, Tableau credentials, refreshes, and publication. No DataAI
hosted service is required.

### Intended users

- Data engineering and ETL owners
- Data quality and governance teams
- Analytics platform administrators
- Business intelligence leads
- Regulated organizations that require customer-controlled data processing

### Business outcomes

- Monitor quality score and rejection trends
- Prioritize critical and error findings
- Identify fields with increasing missing values
- Share governed pipeline status with non-Spark users
- Drill from run summaries into field and rule details

### Required data

The overview expects the `dataai_dashboard_metrics` contract documented in
`../mapping/TABLEAU_OUTPUT_SCHEMA.md`. Optional drill-down uses
`dataai_pipeline_runs`, `dataai_quality_findings`, and
`dataai_field_profiles` related by `run_id`.

### Supported connection paths

- Tableau Spark SQL connector to a customer Spark Thrift Server
- Tableau Databricks connector to a customer Databricks SQL warehouse
- Tableau Hyper or CSV for offline evaluation

### Privacy and data handling

The Accelerator download contains fictional sample data. DataAI ETL executes
inside the customer's Spark environment. The adapter has no telemetry, hosted
service, required network call, automatic persistence, or customer-data
transmission. Tableau connection and usage data are governed by the customer's
Tableau/platform configuration.

### Commercial terms

The Exchange Accelerator is a no-credential evaluation experience. It does
not grant production rights to DataAI ETL libraries. Production, continued
use, redistribution, OEM, or managed-service use requires a separate written
DataAI commercial license. The software is provided **AS IS** and customers
should complete technical, security, connector, and suitability evaluation
during the permitted evaluation period.

### Support placeholder

Replace before submission:

- Support URL: `[DATAAI SUPPORT URL]`
- Support email: `[DATAAI SUPPORT EMAIL]`
- Documentation URL: `[PUBLIC DATAAI TABLEAU DOCUMENTATION URL]`
- Privacy URL: `[DATAAI PRIVACY URL]`
- Terms URL: `[DATAAI TERMS URL]`

## Asset inventory

| Asset | Local path | Submission use |
| --- | --- | --- |
| Packaged workbook | `accelerator/DataAI_ETL_Accelerator.twbx` | Accelerator download |
| Workbook source | `accelerator/DataAI_ETL_Accelerator.twb` | QA and version repair |
| Square icon | `assets/dataai-tableau-icon.png` | Listing icon |
| Vector icon | `assets/dataai-tableau-icon.svg` | Source artwork |
| Overview preview | `screenshots/executive-summary.png` | Draft listing image |
| Quality preview | `screenshots/data-quality.png` | Draft listing image |
| Analytics preview | `screenshots/analytics.png` | Draft listing image |
| Checksums | `CHECKSUMS.sha256` | Distribution integrity |

The PNG screenshots are design previews created from fictional data, not
screenshots rendered by Tableau. Replace them with captures from the verified
Tableau workbook before submission.

## Submission sequence

1. Complete DataAI legal, brand, security, and support review.
2. Replace all bracketed support/privacy/terms placeholders above.
3. Open, repair if needed, and save the TWBX in the supported Tableau Desktop
   release.
4. Test sample-data opening and both live connection paths.
5. Run `scripts/validate_tableau_package.py` and archive its clean output.
6. Capture final Tableau screenshots using only fictional sample data.
7. Apply to or use the required Salesforce/Tableau partner program and obtain
   the marketplace permissions applicable at submission time.
8. Create the Accelerator listing in the Tableau Exchange publisher workflow,
   upload the approved TWBX/assets, and submit it for review.
9. Address review feedback and retest the final downloaded artifact.
10. Keep commercial JAR delivery and entitlement outside Exchange.

Marketplace eligibility and forms can change. Verify the current process on
the official Tableau Exchange/Accelerator pages before submission:

- Accelerator authoring:
  https://help.tableau.com/current/pro/desktop/en-us/accelerators_build.htm
- Connector SDK gallery submission (only if a future custom connector is
  justified):
  https://tableau.github.io/connector-plugin-sdk/docs/gallery-submission

## Why this package is not a connector

A Tableau connector is connection technology, not an ETL function library. A
new connector would be justified only if DataAI introduced a new protocol or
data source unavailable through Tableau. If that happens, treat it as a
separate product: JDBC/ODBC behavior, connector SDK implementation, TDVT
coverage, signed `.taco`, security review, compatibility matrix, support,
privacy, and marketplace approval. Keep it out of the Spark core and this
adapter.
