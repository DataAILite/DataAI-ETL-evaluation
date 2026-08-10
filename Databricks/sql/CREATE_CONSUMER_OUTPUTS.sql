-- Consumer-side template. Replace every <placeholder> before execution.
-- The customer controls all names, locations, ownership, and grants.

CREATE CATALOG IF NOT EXISTS <customer_catalog>;
CREATE SCHEMA IF NOT EXISTS <customer_catalog>.<customer_schema>;
CREATE VOLUME IF NOT EXISTS <customer_catalog>.<customer_schema>.<dataai_volume>;

-- Optional outputs are created only when explicitly enabled in the notebooks.
