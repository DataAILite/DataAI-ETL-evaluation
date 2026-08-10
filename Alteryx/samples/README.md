# Evaluation Sample

1. Load `customer_orders.csv` into an isolated Spark table named
   `dataai_eval.customer_orders`.
2. Copy `rules.json` into the Rules JSON field.
3. Configure the four `dataai_eval.customer_orders_*` output tables shown in
   `job-config.json`.
4. Use minimum quality score `80` and enable normalization.
5. Accept the evaluation license and run with AMP.
6. Verify missing `order_id` and negative `amount` records are rejected and
   that the country warning appears in findings.

The sample uses invented, non-sensitive records. The exact quality score can
change with DataAI rule semantics; verify row-level outcomes and capture the
observed score as external validation evidence.
