package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.expressions.WindowSpec;

import java.util.ArrayList;
import java.util.List;

import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.countDistinct;
import static org.apache.spark.sql.functions.datediff;
import static org.apache.spark.sql.functions.lag;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.max;
import static org.apache.spark.sql.functions.min;
import static org.apache.spark.sql.functions.ntile;
import static org.apache.spark.sql.functions.sum;
import static org.apache.spark.sql.functions.when;

public final class MarketFunctions {
    private MarketFunctions() {
    }

    public static Dataset<Row> demand(
            Dataset<Row> input,
            List<String> dimensionFields,
            String valueField,
            String dateField,
            TimePeriod period,
            double assumptionPercent) {
        Dataset<Row> prepared = withDimension(input, dimensionFields)
                .withColumn("_dataai_value", col(valueField).cast("double"));
        SparkFunctionSupport.requireFields(input, valueField, dateField);
        List<String> keys = new ArrayList<>();
        keys.add("dimension");
        if (dateField != null && !dateField.isBlank()) {
            prepared = prepared.withColumn("period_start", SparkFunctionSupport.period(dateField, period));
            keys.add("period_start");
        }
        Dataset<Row> summary = prepared.groupBy(SparkFunctionSupport.columns(keys)).agg(
                sum("_dataai_value").alias("demand_value"),
                count(lit(1)).alias("records"));
        WindowSpec totalWindow = keys.contains("period_start")
                ? Window.partitionBy(col("period_start"))
                : Window.partitionBy(lit(1));
        return summary
                .withColumn("share_percent", SparkFunctionSupport.safeDivide(
                        col("demand_value"), sum(col("demand_value")).over(totalWindow)).multiply(100.0))
                .withColumn("assumption_percent", lit(assumptionPercent))
                .withColumn("projected_demand", col("demand_value").multiply(1.0 + SparkFunctionSupport.percentRate(assumptionPercent)));
    }

    public static Dataset<Row> segments(
            Dataset<Row> input,
            List<String> dimensionFields,
            String valueField) {
        SparkFunctionSupport.requireFields(input, valueField);
        Dataset<Row> summary = withDimension(input, dimensionFields)
                .groupBy("dimension")
                .agg(
                        count(lit(1)).alias("records"),
                        sum(col(valueField).cast("double")).alias("value"),
                        avg(col(valueField).cast("double")).alias("average_value"));
        WindowSpec all = Window.partitionBy(lit(1));
        return summary
                .withColumn("overall_average", SparkFunctionSupport.safeDivide(
                        sum(col("value")).over(all), sum(col("records")).over(all)))
                .withColumn(
                        "segment_note",
                        when(col("average_value").geq(col("overall_average")), "ABOVE_AVERAGE")
                                .otherwise("BELOW_AVERAGE"))
                .orderBy(col("value").desc_nulls_last());
    }

    public static Dataset<Row> risk(
            Dataset<Row> input,
            List<String> dimensionFields,
            String exposureField) {
        SparkFunctionSupport.requireFields(input, exposureField);
        Dataset<Row> summary = withDimension(input, dimensionFields)
                .groupBy("dimension")
                .agg(
                        count(lit(1)).alias("records"),
                        sum(col(exposureField).cast("double")).alias("value"));
        return summary
                .withColumn("maximum_exposure", max(col("value")).over(Window.partitionBy(lit(1))))
                .withColumn("risk_score", SparkFunctionSupport.safeDivide(col("value"), col("maximum_exposure")).multiply(100.0))
                .withColumn(
                        "risk_note",
                        when(col("risk_score").geq(75), "HIGH_EXPOSURE")
                                .when(col("risk_score").geq(40), "MEDIUM_EXPOSURE")
                                .otherwise("LOWER_EXPOSURE"))
                .orderBy(col("risk_score").desc_nulls_last());
    }

    public static Dataset<Row> scenario(
            Dataset<Row> input,
            List<String> dimensionFields,
            String valueField,
            double assumptionPercent) {
        SparkFunctionSupport.requireFields(input, valueField);
        double rate = Math.abs(SparkFunctionSupport.percentRate(assumptionPercent));
        Dataset<Row> summary = withDimension(input, dimensionFields)
                .groupBy("dimension")
                .agg(
                        count(lit(1)).alias("records"),
                        sum(col(valueField).cast("double")).alias("current_value"));
        return summary
                .withColumn("assumption_percent", lit(Math.abs(assumptionPercent)))
                .withColumn("downside_value", col("current_value").multiply(1.0 - rate))
                .withColumn("base_value", col("current_value"))
                .withColumn("upside_value", col("current_value").multiply(1.0 + rate))
                .withColumn("downside_difference", col("downside_value").minus(col("current_value")))
                .withColumn("upside_difference", col("upside_value").minus(col("current_value")))
                .withColumn("scenario_range", col("upside_value").minus(col("downside_value")))
                .withColumn("scenario_note", lit("DOWNSIDE_BASE_UPSIDE"));
    }

    public static Dataset<Row> pricing(
            Dataset<Row> input,
            String dimensionField,
            String priceField,
            String quantityField,
            int numberOfBands) {
        if (numberOfBands < 2) {
            throw new IllegalArgumentException("Pricing analysis requires at least two price bands.");
        }
        SparkFunctionSupport.requireFields(input, dimensionField, priceField, quantityField);
        Column dimension = dimensionField == null || dimensionField.isBlank()
                ? lit("All Records")
                : col(dimensionField).cast("string");
        Dataset<Row> prepared = input
                .withColumn("dimension", dimension)
                .withColumn("_dataai_price", col(priceField).cast("double"))
                .withColumn("_dataai_quantity", col(quantityField).cast("double"))
                .filter(col("_dataai_price").isNotNull());
        WindowSpec bands = Window.partitionBy("dimension").orderBy(col("_dataai_price"));
        Dataset<Row> summary = prepared
                .withColumn("price_band", ntile(numberOfBands).over(bands))
                .groupBy("dimension", "price_band")
                .agg(
                        count(lit(1)).alias("records"),
                        min("_dataai_price").alias("minimum_price"),
                        max("_dataai_price").alias("maximum_price"),
                        avg("_dataai_price").alias("average_price"),
                        avg("_dataai_quantity").alias("average_quantity"),
                        sum("_dataai_quantity").alias("quantity_sold"),
                        sum(col("_dataai_price").multiply(col("_dataai_quantity"))).alias("revenue"));
        WindowSpec dimensionWindow = Window.partitionBy("dimension");
        return summary
                .withColumn("average_band_quantity", avg(col("quantity_sold")).over(dimensionWindow))
                .withColumn(
                        "sensitivity_note",
                        when(col("quantity_sold").geq(col("average_band_quantity")), "HIGHER_VOLUME")
                                .otherwise("LOWER_VOLUME"))
                .orderBy("dimension", "price_band");
    }

    public static Dataset<Row> elasticity(
            Dataset<Row> input,
            String dimensionField,
            String priceField,
            String quantityField,
            int numberOfBands,
            double priceChangeAssumptionPercent) {
        Dataset<Row> pricing = pricing(input, dimensionField, priceField, quantityField, numberOfBands);
        WindowSpec ordered = Window.partitionBy("dimension").orderBy("price_band");
        double rate = SparkFunctionSupport.percentRate(priceChangeAssumptionPercent);
        return pricing
                .withColumn("previous_price", lag(col("average_price"), 1).over(ordered))
                .withColumn("previous_quantity", lag(col("quantity_sold"), 1).over(ordered))
                .withColumn("price_change_percent", SparkFunctionSupport.safeDivide(
                        col("average_price").minus(col("previous_price")), col("previous_price")).multiply(100.0))
                .withColumn("quantity_change_percent", SparkFunctionSupport.safeDivide(
                        col("quantity_sold").minus(col("previous_quantity")), col("previous_quantity")).multiply(100.0))
                .withColumn("elasticity", SparkFunctionSupport.safeDivide(
                        col("quantity_change_percent"), col("price_change_percent")))
                .withColumn("assumption_price_change_percent", lit(priceChangeAssumptionPercent))
                .withColumn("projected_price", col("average_price").multiply(1.0 + rate))
                .withColumn("projected_quantity", col("quantity_sold").multiply(lit(1.0).plus(col("elasticity").multiply(rate))))
                .withColumn("projected_revenue", col("projected_price").multiply(col("projected_quantity")))
                .withColumn("revenue_impact", col("projected_revenue").minus(col("revenue")))
                .withColumn(
                        "elasticity_note",
                        when(org.apache.spark.sql.functions.abs(col("elasticity")).gt(1), "ELASTIC")
                                .when(col("elasticity").isNull(), "INSUFFICIENT_PREVIOUS_BAND")
                                .otherwise("INELASTIC"));
    }

    public static Dataset<Row> basket(
            Dataset<Row> input,
            String transactionField,
            String itemField,
            String valueField) {
        SparkFunctionSupport.requireFields(input, transactionField, itemField, valueField);
        Dataset<Row> uniqueItems = input
                .select(col(transactionField), col(itemField))
                .filter(col(transactionField).isNotNull().and(col(itemField).isNotNull()))
                .distinct();
        Dataset<Row> left = uniqueItems.alias("left_item");
        Dataset<Row> right = uniqueItems.alias("right_item");
        Dataset<Row> pairTransactions = left.join(
                        right,
                        col("left_item." + transactionField).equalTo(col("right_item." + transactionField))
                                .and(col("left_item." + itemField).cast("string")
                                        .lt(col("right_item." + itemField).cast("string"))),
                        "inner")
                .select(
                        col("left_item." + transactionField).alias("transaction_id"),
                        col("left_item." + itemField).cast("string").alias("item_a"),
                        col("right_item." + itemField).cast("string").alias("item_b"));
        Dataset<Row> transactionValues = valueField == null || valueField.isBlank()
                ? input.select(col(transactionField).alias("transaction_id")).distinct()
                    .withColumn("transaction_value", lit(0.0))
                : input.groupBy(col(transactionField))
                    .agg(sum(col(valueField).cast("double")).alias("transaction_value"))
                    .withColumnRenamed(transactionField, "transaction_id");
        Dataset<Row> totalOrders = input.select(col(transactionField)).distinct()
                .agg(count(lit(1)).alias("total_orders"));
        return pairTransactions.join(transactionValues, "transaction_id")
                .groupBy("item_a", "item_b")
                .agg(
                        countDistinct("transaction_id").alias("orders_together"),
                        sum("transaction_value").alias("weighted_basket_value"))
                .crossJoin(totalOrders)
                .withColumn("support_percent", SparkFunctionSupport.safeDivide(
                        col("orders_together"), col("total_orders")).multiply(100.0))
                .withColumn("basket_note", lit("BUNDLE_OR_CROSS_SELL_CANDIDATE"))
                .orderBy(col("orders_together").desc(), col("item_a"), col("item_b"));
    }

    public static Dataset<Row> churn(
            Dataset<Row> input,
            String customerField,
            String valueField,
            String activityDateField,
            int activeDays,
            int reviewDays) {
        if (activeDays < 0 || reviewDays <= activeDays) {
            throw new IllegalArgumentException("Review days must be greater than active days.");
        }
        SparkFunctionSupport.requireFields(input, customerField, valueField, activityDateField);
        Dataset<Row> summary = input.groupBy(col(customerField)).agg(
                count(lit(1)).alias("records"),
                max(col(activityDateField).cast("timestamp")).alias("last_activity"),
                sum(col(valueField).cast("double")).alias("value"));
        return summary
                .withColumn("latest_dataset_activity", max(col("last_activity")).over(Window.partitionBy(lit(1))))
                .withColumn("days_inactive", datediff(col("latest_dataset_activity"), col("last_activity")))
                .withColumn("retention_score", org.apache.spark.sql.functions.greatest(
                        lit(0.0), lit(100.0).minus(col("days_inactive").multiply(100.0 / reviewDays))))
                .withColumn(
                        "churn_note",
                        when(col("days_inactive").leq(activeDays), "RECENTLY_ACTIVE")
                                .when(col("days_inactive").leq(reviewDays), "REVIEW_RETENTION")
                                .otherwise("HIGH_CHURN_RISK"))
                .orderBy(col("retention_score").asc());
    }

    public static Dataset<Row> inventory(
            Dataset<Row> input,
            List<String> dimensionFields,
            String movementField,
            String currentInventoryField,
            double safetyStockPercent) {
        SparkFunctionSupport.requireFields(input, movementField, currentInventoryField);
        Dataset<Row> summary = withDimension(input, dimensionFields)
                .groupBy("dimension")
                .agg(
                        count(lit(1)).alias("records"),
                        sum(col(movementField).cast("double")).alias("units_movement"),
                        max(col(currentInventoryField).cast("double")).alias("current_inventory"));
        return summary
                .withColumn("velocity", SparkFunctionSupport.safeDivide(col("units_movement"), col("records")))
                .withColumn("safety_stock_percent", lit(safetyStockPercent))
                .withColumn("reorder_point", col("velocity").multiply(1.0 + SparkFunctionSupport.percentRate(safetyStockPercent)))
                .withColumn("supply_periods", SparkFunctionSupport.safeDivide(col("current_inventory"), col("velocity")))
                .withColumn("reorder_needed", col("current_inventory").leq(col("reorder_point")))
                .withColumn(
                        "inventory_note",
                        when(col("reorder_needed"), "REORDER_RECOMMENDED")
                                .otherwise("INVENTORY_ABOVE_REORDER_POINT"));
    }

    public static Dataset<Row> profit(
            Dataset<Row> input,
            List<String> dimensionFields,
            String revenueField,
            String directCostField,
            String unitCostField,
            String quantityField,
            double estimatedCostPercent) {
        SparkFunctionSupport.requireFields(input, revenueField, directCostField, unitCostField, quantityField);
        Dataset<Row> prepared = withDimension(input, dimensionFields);
        Column cost;
        String costSource;
        double effectiveCostPercent = estimatedCostPercent == 0 ? 65.0 : estimatedCostPercent;
        if (directCostField != null && !directCostField.isBlank()) {
            cost = col(directCostField).cast("double");
            costSource = "DIRECT_COST";
        } else if (unitCostField != null && !unitCostField.isBlank()
                && quantityField != null && !quantityField.isBlank()) {
            cost = col(unitCostField).cast("double").multiply(col(quantityField).cast("double"));
            costSource = "UNIT_COST_X_QUANTITY";
        } else {
            cost = col(revenueField).cast("double").multiply(SparkFunctionSupport.percentRate(effectiveCostPercent));
            costSource = "ESTIMATED_COST_RATE";
        }
        Dataset<Row> summary = prepared.groupBy("dimension").agg(
                count(lit(1)).alias("records"),
                sum(col(revenueField).cast("double")).alias("revenue"),
                sum(cost).alias("estimated_cost"));
        WindowSpec all = Window.partitionBy(lit(1));
        return summary
                .withColumn("cost_source", lit(costSource))
                .withColumn("cost_rate_percent", SparkFunctionSupport.safeDivide(col("estimated_cost"), col("revenue")).multiply(100.0))
                .withColumn("estimated_profit", col("revenue").minus(col("estimated_cost")))
                .withColumn("margin_percent", SparkFunctionSupport.safeDivide(col("estimated_profit"), col("revenue")).multiply(100.0))
                .withColumn("profit_contribution_percent", SparkFunctionSupport.safeDivide(
                        col("estimated_profit"), sum(col("estimated_profit")).over(all)).multiply(100.0))
                .withColumn(
                        "profit_note",
                        when(col("estimated_profit").lt(0), "LOSS")
                                .when(col("margin_percent").geq(25), "HIGH_MARGIN")
                                .otherwise("POSITIVE_MARGIN"))
                .orderBy(col("estimated_profit").desc_nulls_last());
    }

    private static Dataset<Row> withDimension(Dataset<Row> input, List<String> dimensionFields) {
        List<String> fields = dimensionFields == null ? List.of() : List.copyOf(dimensionFields);
        SparkFunctionSupport.requireFields(input, fields.toArray(String[]::new));
        return input.withColumn("dimension", SparkFunctionSupport.dimension(fields));
    }
}
