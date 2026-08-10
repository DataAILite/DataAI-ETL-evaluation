# DataAI ETL Accelerator

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

`DataAI_ETL_Accelerator.twbx` is a packaged Tableau workbook intended for
evaluation and Tableau Exchange submission preparation.

## Evaluation

1. Open the `.twbx` in Tableau Desktop.
2. The initial data source is the fictional
   `dataai_dashboard_metrics.csv` embedded in the workbook.
3. Review the included overview and quality trend sheets/dashboard.
4. Use **Data > Replace Data Source** to replace the sample with the
   customer's native Spark SQL or Databricks table/view.
5. Confirm these fields map without changing their meaning:
   `run_id`, `completed_at`, `status`, `rows_read`, `rows_accepted`,
   `rows_rejected`, `quality_score`, the four severity counts,
   `fields_profiled`, and `total_null_values`.
6. Save the customer-specific workbook under a new name.

## Commercial publication gate

The package is generated without Tableau Desktop and receives XML, ZIP, data,
Hyper, checksum, and schema validation from
`../scripts/validate_tableau_package.py`. Structural validation is not a
substitute for Tableau rendering or marketplace review.

Before submission:

- open and resave the workbook in the oldest supported Tableau Desktop
  version;
- test the supported current Tableau Desktop/Cloud/Server versions;
- replace design-preview screenshots with screenshots captured from the
  verified Tableau workbook;
- verify keyboard navigation, contrast, captions, filters, and tooltips;
- remove unused fields and confirm the package contains only fictional data;
- complete partner, legal, support, privacy, and security review.

Tableau Accelerator authoring guidance:
https://help.tableau.com/current/pro/desktop/en-us/accelerators_build.htm
