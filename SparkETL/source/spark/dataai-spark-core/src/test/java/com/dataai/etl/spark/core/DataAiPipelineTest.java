package com.dataai.etl.spark.core;

import com.dataai.etl.spark.api.DataAiResult;
import com.dataai.etl.spark.api.RuleSpec;
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

class DataAiPipelineTest {
    private static SparkSession spark;

    @BeforeAll
    static void startSpark() {
        spark = SparkTestSession.create();
    }

    @AfterAll
    static void stopSpark() {
        if (spark != null) {
            spark.stop();
        }
    }

    @Test
    void normalizesProfilesAndRoutesRejectedRows() {
        StructType schema = new StructType()
                .add("Order ID", DataTypes.StringType, true)
                .add("Customer ID", DataTypes.StringType, true)
                .add("Amount", DataTypes.DoubleType, true)
                .add("Email", DataTypes.StringType, true);
        List<Row> rows = List.of(
                RowFactory.create("1", " C-1 ", 25.0, "one@example.com"),
                RowFactory.create("2", "", 15.0, "two@example.com"),
                RowFactory.create("3", "C-3", -1.0, "not-an-email"),
                RowFactory.create("3", "C-4", 10.0, "four@example.com"));
        Dataset<Row> input = spark.createDataFrame(rows, schema);

        DataAiResult result = DataAiPipeline
                .fromDataset(input)
                .normalize()
                .recordKey("order_id", "customer_id")
                .profile()
                .validate(
                        RuleSpec.required("customer-required", "customer_id"),
                        RuleSpec.unique("order-unique", "order_id"),
                        RuleSpec.minimum("amount-minimum", "amount", 0),
                        RuleSpec.maximum("amount-maximum", "amount", 1000),
                        RuleSpec.between("amount-range", "amount", -1, 1000),
                        RuleSpec.inSet("customer-set", "customer_id", List.of("C-1", "C-3", "C-4")),
                        RuleSpec.length("order-length", "order_id", 1, 10),
                        RuleSpec.regex("email-format", "email", "^[^@]+@[^@]+\\.[^@]+$"))
                .execute();

        assertEquals(4, result.summary().rowsRead());
        assertEquals(1, result.summary().rowsAccepted());
        assertEquals(3, result.summary().rowsRejected());
        assertEquals(25.0, result.summary().qualityScore());
        assertEquals(5, result.fieldProfiles().count());
    }

    @Test
    void evaluatesDateAndEqualityRules() {
        StructType schema = new StructType()
                .add("Code", DataTypes.StringType, true)
                .add("Status", DataTypes.StringType, true)
                .add("Event Date", DataTypes.StringType, true);
        Dataset<Row> input = spark.createDataFrame(List.of(
                RowFactory.create("1", "OK", "2026-08-06"),
                RowFactory.create("2", "BAD", "not-a-date")), schema);

        DataAiResult result = DataAiPipeline
                .fromDataset(input)
                .normalize()
                .recordKey("code")
                .validate(
                        RuleSpec.equalsValue("status-ok", "status", "OK"),
                        RuleSpec.dateFormat("valid-date", "event_date", "yyyy-MM-dd"))
                .execute();

        assertEquals(1, result.summary().rowsAccepted());
        assertEquals(1, result.summary().rowsRejected());
        assertEquals(2, result.findings().count());
    }
}
