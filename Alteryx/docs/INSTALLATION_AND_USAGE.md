# Installation and Usage

## 1. Verify prerequisites

For this evaluation candidate, use:

- Windows 64-bit;
- Alteryx Designer 2026.1;
- AMP Engine enabled;
- Java 17;
- a customer-managed Spark 3.5 / Scala 2.12 runtime;
- a working `spark-submit` command on the Designer machine or an absolute path
  to `spark-submit.cmd`, `.bat`, or `.exe`;
- a Spark catalog reachable with the identity that runs Designer.

Designer 2026.1 is the declared target because the YXI bundles Alteryx Python
SDK 2.5.3 for embedded Python 3.13.11. A separately built and separately tested
YXI is required for older Designer Python generations.

## 2. Verify the download

From PowerShell in the extracted package directory:

```powershell
Get-FileHash .\install\DataAI_ETL_Alteryx_2026_1_Evaluation.yxi -Algorithm SHA256
```

Compare the value with `CHECKSUMS.sha256` from the provider package.

## 3. Review and accept evaluation terms

Read `LICENSE.md`. The tool also requires the user to select the evaluation
acceptance checkbox before execution. Do not use the evaluation build in
production. A production license requires a signed commercial agreement.

## 4. Install the YXI

1. Close workflows that use older DataAI ETL tool versions.
2. Double-click `DataAI_ETL_Alteryx_2026_1_Evaluation.yxi`, or drag it into
   Alteryx Designer.
3. Select user or administrator installation according to the customer's
   deployment policy.
4. Restart Designer if the **DataAI ETL** tool category does not appear.
5. Confirm **DataAI ETL Quality** appears in that category.

For Alteryx Server, an administrator must install the same approved YXI on
every execution worker and make Java, Spark, catalogs, and connector libraries
available to the service account. Validate Server separately before use.

## 5. Prepare a Spark source table

The tool operates on a Spark catalog table, not an in-memory Alteryx record
stream. Load the sample CSV or an approved evaluation data set into a table,
for example `dataai_eval.customer_orders`.

Ensure the Spark identity can:

- read the source table;
- create or overwrite only the selected output tables;
- write Delta tables in the selected catalog and schema.

## 6. Configure the tool

Create a new workflow and drag **DataAI ETL Quality** onto the canvas.

1. **Spark Submit**: enter the command or full path.
2. **Spark Master**: enter `local[*]`, `yarn`, or the approved cluster URL.
3. **Deploy Mode**: select `client` or `cluster`.
4. **Source Table**: enter the existing Spark catalog table.
5. Enter any desired **Clean**, **Rejected**, **Profile**, and **Findings**
   tables. Each specified table is overwritten by the DataAI CLI.
6. Select normalization if desired.
7. Enter comma-separated record keys.
8. Paste a JSON array of rules, such as `samples/rules.json`.
9. Optionally enter a minimum quality score from 0 through 100.
10. Add extra Spark arguments as a JSON string array, never as one shell
    command. Example: `["--conf","spark.sql.session.timeZone=UTC"]`.
11. Set the timeout and accept the evaluation license.

The adapter enforces the DataAI main class and does not invoke a command shell.
Do not place passwords, access tokens, or private keys in the tool fields.
Use the customer's Spark credential and secret-management mechanisms.

## 7. Run and verify

1. Enable AMP for the workflow.
2. Connect a Browse tool to the optional **Status** output.
3. Run the workflow.
4. Confirm the status row says `Succeeded` and exit code `0`.
5. Inspect the customer-controlled Spark logs.
6. Verify each configured output table and its row counts.
7. Test at least one intentionally failing rule and minimum-score gate.
8. Confirm no output table outside the selected schema changed.

The status output never returns customer rows or raw Spark logs. On failure,
use local Designer and Spark logs, because logs can contain environment-specific
details and are intentionally not copied into the Alteryx output.

## 8. Use advanced DataAI functions

The evaluation ZIP includes the API, quality, core, functions, and CLI JARs.
Matrix balancing and the other advanced functions in
`docs/FUNCTION_CATALOG.md` are called from a customer Java/Spark job. Add the
four unshaded libraries to that job, create an approved wrapper for the desired
function, and call that job from Alteryx or the customer's scheduler. They are
not separate buttons in the first Alteryx tool version.

## 9. Uninstall

Use the customer's Alteryx custom-tool administration process to remove the
`DataAiEtlQuality_1_0` tool directory. Removing the tool does not delete Spark
tables. Output tables must be retained or removed under the customer's data
governance procedure.
