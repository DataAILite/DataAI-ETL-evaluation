-- Provider-side template. Replace every <placeholder> before execution.
-- Requires provider-controlled Unity Catalog privileges.

CREATE CATALOG IF NOT EXISTS <provider_catalog>;
CREATE SCHEMA IF NOT EXISTS <provider_catalog>.<provider_schema>;
CREATE VOLUME IF NOT EXISTS <provider_catalog>.<provider_schema>.<evaluation_volume>;

-- Upload Databricks/lib, data, docs, and distribution files to:
-- /Volumes/<provider_catalog>/<provider_schema>/<evaluation_volume>/dataai-etl/
-- Create the Marketplace share through the Databricks Provider console.
