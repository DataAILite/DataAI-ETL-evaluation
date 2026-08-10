package com.dataai.etl.spark.functions;

import com.dataai.etl.spark.testkit.SparkTestSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class DataAiFunctionsTest {
    private static SparkSession spark;
    private static Dataset<Row> input;

    @BeforeAll
    static void startSpark() {
        spark = SparkTestSession.create();
        StructType schema = new StructType()
                .add("transaction_id", DataTypes.StringType, true)
                .add("item", DataTypes.StringType, true)
                .add("customer", DataTypes.StringType, true)
                .add("region", DataTypes.StringType, true)
                .add("segment", DataTypes.StringType, true)
                .add("stage", DataTypes.StringType, true)
                .add("event_date", DataTypes.StringType, true)
                .add("amount", DataTypes.DoubleType, true)
                .add("cost", DataTypes.DoubleType, true)
                .add("units", DataTypes.DoubleType, true)
                .add("inventory", DataTypes.DoubleType, true)
                .add("latitude", DataTypes.DoubleType, true)
                .add("longitude", DataTypes.DoubleType, true)
                .add("category", DataTypes.StringType, true);
        List<Row> rows = List.of(
                RowFactory.create("T1", "Apple", "C1", "North", "A", "Visit", "2026-01-01", 10.0, 6.0, 1.0, 100.0, 33.45, -112.07, "Retail"),
                RowFactory.create("T1", "Banana", "C1", "North", "A", "Trial", "2026-01-08", 20.0, 12.0, 2.0, 98.0, 33.45, -112.07, "Retail"),
                RowFactory.create("T2", "Apple", "C2", "South", "B", "Visit", "2026-02-01", 30.0, 15.0, 3.0, 80.0, 40.71, -74.00, "Wholesale"),
                RowFactory.create("T2", "Carrot", "C2", "South", "B", "Purchase", "2026-02-10", 40.0, 22.0, 4.0, 76.0, 40.71, -74.00, "Wholesale"),
                RowFactory.create("T3", "Banana", "C3", "North", "B", "Visit", "2026-03-01", 50.0, 25.0, 5.0, 60.0, 91.0, 10.0, " retail "),
                RowFactory.create("T3", "Carrot", "C3", "North", "B", "Trial", "bad-date", 60.0, 30.0, 6.0, 55.0, null, null, "Retail"),
                RowFactory.create("T4", "Apple", null, "South", "A", "Purchase", "2026-03-15", 500.0, 100.0, 7.0, 40.0, 34.05, -118.24, "Online"),
                RowFactory.create("T4", "Apple", null, "South", "A", "Purchase", "2026-03-15", 500.0, 100.0, 7.0, 40.0, 34.05, -118.24, "Online"));
        input = spark.createDataFrame(rows, schema);
    }

    @AfterAll
    static void stopSpark() {
        if (spark != null) {
            spark.stop();
        }
    }

    @Test
    void runsAnalyticsTimeAndBusinessFunctions() {
        assertEquals(2, AnalyticsFunctions.groupedSummary(
                input, List.of("region"), "amount", Aggregation.SUM).count());
        assertEquals(2, AnalyticsFunctions.variance(
                input, List.of("region"), "segment", "A", "B", "amount", Aggregation.SUM).count());
        assertEquals(1, AnalyticsFunctions.correlations(input, List.of("amount", "units")).count());
        assertEquals(1, AnalyticsFunctions.linearRegression(input, "units", "amount", null, 8.0).count());
        assertFalse(TimeSeriesFunctions.rolling(
                input, List.of("region"), "event_date", TimePeriod.MONTH,
                "amount", Aggregation.SUM, 2, RollingOperation.MOVING_AVERAGE).isEmpty());
        assertFalse(BusinessFunctions.pareto(input, "item", "amount", Aggregation.SUM).isEmpty());
        assertFalse(BusinessFunctions.drift(input, "category", "segment", "A", "B").isEmpty());
        assertFalse(BusinessFunctions.outliers(
                input, List.of(), "amount", OutlierMethod.STANDARD_DEVIATION,
                1.5, null, null).isEmpty());
        assertEquals(2, BusinessFunctions.kpi(
                input, List.of("region"), "amount", "cost", KpiOperation.RATIO).count());
        assertEquals(3, BusinessFunctions.funnel(
                input, "stage", "customer", "amount",
                List.of("Visit", "Trial", "Purchase")).count());
        assertFalse(BusinessFunctions.cohort(
                input.filter("event_date <> 'bad-date'"), "customer", "event_date", "amount", TimePeriod.MONTH).isEmpty());
    }

    @Test
    void runsMarketQualityMapAndInsightFunctions() {
        assertFalse(MarketFunctions.demand(
                input, List.of("region", "category"), "amount", "event_date", TimePeriod.MONTH, 10).isEmpty());
        assertEquals(2, MarketFunctions.segments(input, List.of("region"), "amount").count());
        assertEquals(2, MarketFunctions.risk(input, List.of("region"), "amount").count());
        assertEquals(2, MarketFunctions.scenario(input, List.of("region"), "amount", 10).count());
        assertFalse(MarketFunctions.pricing(input, "region", "amount", "units", 2).isEmpty());
        assertFalse(MarketFunctions.elasticity(input, "region", "amount", "units", 2, 5).isEmpty());
        assertFalse(MarketFunctions.basket(input, "transaction_id", "item", "amount").isEmpty());
        assertFalse(MarketFunctions.churn(input.filter("event_date <> 'bad-date'"),
                "customer", "amount", "event_date", 15, 90).isEmpty());
        assertEquals(2, MarketFunctions.inventory(
                input, List.of("region"), "units", "inventory", 20).count());
        assertEquals(2, MarketFunctions.profit(
                input, List.of("region"), "amount", "cost", null, null, 0).count());

        assertFalse(DataQualityFunctions.automaticChecks(input, 2.0).isEmpty());
        MapReadinessResult map = MapFunctions.readiness(input, "latitude", "longitude", "customer");
        assertFalse(map.summary().isEmpty());
        assertTrue(map.suggestedLatitudeFields().contains("latitude"));
        assertTrue(map.suggestedLongitudeFields().contains("longitude"));
        assertEquals(input.schema().size(), InsightFunctions.dataDictionary(input).count());
        assertFalse(InsightFunctions.chartRecommendations(input).isEmpty());
        assertEquals(input.schema().size(), InsightFunctions.narratives(input).count());
        assertTrue(DataAiFunctionCatalog.entries().size() >= 35);
    }

    @Test
    void balancesMatrixToRowAndColumnControls() {
        StructType cellsSchema = new StructType()
                .add("row_name", DataTypes.StringType, false)
                .add("column_name", DataTypes.StringType, false)
                .add("value", DataTypes.DoubleType, false);
        Dataset<Row> cells = spark.createDataFrame(List.of(
                RowFactory.create("R1", "C1", 10.0),
                RowFactory.create("R1", "C2", 20.0),
                RowFactory.create("R2", "C1", 30.0),
                RowFactory.create("R2", "C2", 40.0)), cellsSchema);
        StructType rowTargetSchema = new StructType()
                .add("row_name", DataTypes.StringType, false)
                .add("target_total", DataTypes.DoubleType, false);
        StructType columnTargetSchema = new StructType()
                .add("column_name", DataTypes.StringType, false)
                .add("target_total", DataTypes.DoubleType, false);
        Dataset<Row> rowTargets = spark.createDataFrame(List.of(
                RowFactory.create("R1", 60.0),
                RowFactory.create("R2", 40.0)), rowTargetSchema);
        Dataset<Row> columnTargets = spark.createDataFrame(List.of(
                RowFactory.create("C1", 50.0),
                RowFactory.create("C2", 50.0)), columnTargetSchema);

        MatrixBalanceResult result = MatrixFunctions.balance(
                cells, "row_name", "column_name", "value",
                rowTargets, columnTargets, "target_total", 30, 0.001);

        assertTrue(result.converged());
        assertEquals(4, result.balancedCells().count());
        assertTrue(result.maximumError() <= 0.001);
    }
}
