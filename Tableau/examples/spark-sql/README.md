# Tableau Spark SQL Connection

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

Use this path when the customer exposes DataAI Spark catalog tables through a
Spark Thrift Server compatible with Tableau.

1. Persist the DataAI outputs and create the views in
   `../sql/tableau_views.sql`.
2. Confirm the Thrift Server can query the views under the same identity or
   authorization model intended for Tableau.
3. In Tableau Desktop, select **Connect > To a Server > Spark SQL**.
4. Enter the customer-provided host and port. Select the required transport,
   authentication, SSL, and HTTP-path settings.
5. Choose the `analytics` schema and add
   `tableau_dataai_run_overview`.
6. For drill-down, add the finding and profile views and relate on `run_id`.
7. Validate live-query performance. Use a Tableau extract only if approved by
   the customer's data-governance policy.

Do not embed shared production passwords in the workbook. Prefer the
customer's supported single sign-on or managed credential policy.

Official reference:
https://help.tableau.com/current/pro/desktop/en-us/examples_sparksql.htm
