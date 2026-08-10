# Tableau Databricks Connection

DataAI ETL is proprietary, source-available evaluation software from Yanbor LLC, built with open-source technologies including Apache Spark.

Use this path when DataAI ETL runs in Databricks and persists governed Delta
tables or views.

1. Persist the DataAI outputs in Unity Catalog and create the views in
   `../sql/tableau_views.sql`.
2. Grant Tableau users or a service principal `USE CATALOG`, `USE SCHEMA`, and
   `SELECT` only on the intended views.
3. Create or select a Databricks SQL warehouse and record its server hostname
   and HTTP path.
4. In Tableau Desktop, select **Databricks**.
5. Use the customer's approved OAuth, personal access token, or service
   principal policy. OAuth is generally preferable for named interactive
   users.
6. Select `tableau_dataai_run_overview`; add finding/profile views only when
   drill-down is authorized.
7. Replace the Accelerator's sample source, verify field mappings, and publish
   to a restricted non-production Tableau project first.

The DataAI adapter does not need Databricks credentials. Credentials belong to
the Spark job and Tableau connection configured by the customer.

Official reference:
https://help.tableau.com/current/pro/desktop/en-us/examples_databricks.htm
