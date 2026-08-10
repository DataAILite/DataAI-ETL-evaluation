package com.dataai.customer.examples;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.RuleSpec;
import com.dataai.etl.spark.core.DataAiPipeline;
import com.dataai.etl.spark.tableau.TableauOutputBundle;
import com.dataai.etl.spark.tableau.TableauOutputs;
import org.apache.spark.sql.SaveMode;
import org.apache.spark.sql.SparkSession;

import static org.apache.spark.sql.functions.lit;

/** Example only: choose customer-approved catalogs, formats, and write modes. */
public final class TableauSparkExample {
    private TableauSparkExample() {
    }

    public static void main(String[] args) {
        SparkSession spark = SparkSession.builder()
                .appName("DataAI outputs for Tableau")
                .getOrCreate();

        DataAiResult result = DataAiPipeline
                .fromTable(spark, "bronze.customer_orders")
                .normalize()
                .recordKey("order_id")
                .profile()
                .validate(
                        RuleSpec.required("customer-required", "customer_id"),
                        RuleSpec.minimum("amount-nonnegative", "amount", 0))
                .execute();

        TableauOutputBundle tableau = TableauOutputs.from(result);
        String runId = result.summary().runId();

        tableau.dashboardMetrics().write()
                .format("delta")
                .mode(SaveMode.Append)
                .saveAsTable("analytics.dataai_dashboard_metrics");
        tableau.pipelineRuns().write()
                .format("delta")
                .mode(SaveMode.Append)
                .saveAsTable("analytics.dataai_pipeline_runs");
        tableau.qualityFindings()
                .withColumn("run_id", lit(runId))
                .write()
                .format("delta")
                .mode(SaveMode.Append)
                .saveAsTable("analytics.dataai_quality_findings");
        tableau.fieldProfiles()
                .withColumn("run_id", lit(runId))
                .write()
                .format("delta")
                .mode(SaveMode.Append)
                .saveAsTable("analytics.dataai_field_profiles");

        result.requireMinimumQualityScore(90.0);
        tableau.cleanRows().write()
                .format("delta")
                .mode(SaveMode.Overwrite)
                .saveAsTable("silver.customer_orders");
    }
}
