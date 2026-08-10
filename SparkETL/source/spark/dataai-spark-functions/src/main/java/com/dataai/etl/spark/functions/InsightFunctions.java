package com.dataai.etl.spark.functions;

import com.dataai.etl.spark.core.FieldProfiler;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.types.DataType;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;
import org.apache.spark.sql.types.StructType;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.concat;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.when;

public final class InsightFunctions {
    private InsightFunctions() {
    }

    public static Dataset<Row> dataDictionary(Dataset<Row> input) {
        List<Row> rows = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            String role = role(field);
            rows.add(RowFactory.create(
                    field.name(),
                    field.dataType().catalogString(),
                    field.nullable(),
                    role,
                    suggestedUsage(role),
                    field.metadata().json()));
        }
        StructType schema = new StructType()
                .add("field_name", DataTypes.StringType, false)
                .add("source_type", DataTypes.StringType, false)
                .add("nullable", DataTypes.BooleanType, false)
                .add("detected_role", DataTypes.StringType, false)
                .add("suggested_usage", DataTypes.StringType, false)
                .add("spark_metadata", DataTypes.StringType, false);
        return input.sparkSession().createDataFrame(rows, schema);
    }

    public static Dataset<Row> chartRecommendations(Dataset<Row> input) {
        List<String> categories = new ArrayList<>();
        List<String> dates = new ArrayList<>();
        List<String> measures = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            String role = role(field);
            switch (role) {
                case "DATE_TIME" -> dates.add(field.name());
                case "MEASURE" -> measures.add(field.name());
                case "CATEGORY", "TEXT" -> categories.add(field.name());
                default -> {
                }
            }
        }
        List<Row> rows = new ArrayList<>();
        Set<String> keys = new HashSet<>();
        if (!dates.isEmpty() && !measures.isEmpty()) {
            addRecommendation(rows, keys, "LINE", dates.get(0), measures.get(0), "HIGHEST", "Time field with numeric measure supports trend analysis.");
            addRecommendation(rows, keys, "AREA", dates.get(0), measures.get(0), "HIGH", "Area emphasizes cumulative movement over time.");
            addRecommendation(rows, keys, "STEPPED_AREA", dates.get(0), measures.get(0), "NORMAL", "Stepped area suits discrete period changes.");
        }
        if (!categories.isEmpty() && !measures.isEmpty()) {
            addRecommendation(rows, keys, "BAR", categories.get(0), measures.get(0), "HIGHEST", "Bar charts compare numeric values across categories.");
            addRecommendation(rows, keys, "COLUMN", categories.get(0), measures.get(0), "HIGHEST", "Column charts provide dashboard-safe category comparison.");
            addRecommendation(rows, keys, "PIE", categories.get(0), measures.get(0), "NORMAL", "Pie charts can show contribution for a small category set.");
            addRecommendation(rows, keys, "COMBO", categories.get(0), String.join(",", measures.subList(0, Math.min(3, measures.size()))), "HIGH", "Combo charts compare several measures on one category axis.");
        }
        if (!measures.isEmpty()) {
            addRecommendation(rows, keys, "HISTOGRAM", measures.get(0), measures.get(0), "HIGH", "Histogram shows a measure's distribution.");
            addRecommendation(rows, keys, "GAUGE", "", measures.get(0), "NORMAL", "Gauge can show one monitored KPI.");
        }
        if (measures.size() >= 2) {
            addRecommendation(rows, keys, "SCATTER", measures.get(0), measures.get(1), "HIGH", "Scatter charts expose numeric relationships and outliers.");
            addRecommendation(rows, keys, "BUBBLE", measures.get(0), String.join(",", measures.subList(1, Math.min(3, measures.size()))), "NORMAL", "Bubble charts compare two or three numeric measures.");
        }
        if (categories.size() >= 2 && !measures.isEmpty()) {
            addRecommendation(rows, keys, "SANKEY", categories.get(0) + "," + categories.get(1), measures.get(0), "NORMAL", "Sankey charts show flow between two categories.");
        }
        if (rows.isEmpty()) {
            addRecommendation(rows, keys, "REPORT", String.join(",", input.columns()), "", "HIGHEST", "Use tabular output when no reliable chart mapping is available.");
        }
        StructType schema = new StructType()
                .add("chart_type", DataTypes.StringType, false)
                .add("category_fields", DataTypes.StringType, false)
                .add("value_fields", DataTypes.StringType, false)
                .add("priority", DataTypes.StringType, false)
                .add("reason", DataTypes.StringType, false);
        return input.sparkSession().createDataFrame(rows, schema);
    }

    public static Dataset<Row> narratives(Dataset<Row> input) {
        Dataset<Row> profiles = FieldProfiler.profile(input);
        return profiles.select(
                when(col("mean_value").isNotNull(), lit("FIELD_BEHAVIOR"))
                        .otherwise(lit("FIELD_STRUCTURE")).alias("narrative_type"),
                col("field_name"),
                when(
                        col("mean_value").isNotNull(),
                        concat(
                                lit("Numeric field ranges from "), col("minimum_value"),
                                lit(" to "), col("maximum_value"), lit(".")))
                        .otherwise(concat(
                                lit("Field has "), col("distinct_count"), lit(" distinct values.")))
                        .alias("finding"),
                concat(
                        lit("Records="), col("record_count"),
                        lit("; missing="), col("null_count"),
                        lit("; type="), col("source_type")).alias("evidence"),
                when(col("null_count").gt(0), lit("Review missing values and add a quality rule."))
                        .when(col("mean_value").isNotNull(), lit("Consider ranking, regression, outlier, or KPI analysis."))
                        .otherwise(lit("Consider grouping, pivot, funnel, or segmentation analysis."))
                        .alias("recommended_action"));
    }

    public static Dataset<Row> ruleBasedAlerts(Dataset<Row> input, double standardDeviationThreshold) {
        return DataQualityFunctions.automaticChecks(input, standardDeviationThreshold)
                .withColumn("alert_status", lit("ALERT"))
                .withColumn(
                        "recommended_function",
                        when(col("issue_type").equalTo("NUMERIC_OUTLIER"), "BusinessFunctions.outliers")
                                .when(col("issue_type").equalTo("INVALID_DATE"), "TimeSeriesFunctions.summarize")
                                .when(col("issue_type").equalTo("DUPLICATE_RECORDS"), "DataAiPipeline.validate")
                                .otherwise("DataQualityFunctions.automaticChecks"));
    }

    private static void addRecommendation(
            List<Row> rows,
            Set<String> keys,
            String chart,
            String categories,
            String values,
            String priority,
            String reason) {
        String key = chart + "|" + categories + "|" + values;
        if (keys.add(key)) {
            rows.add(RowFactory.create(chart, categories, values, priority, reason));
        }
    }

    private static String role(StructField field) {
        String name = field.name().toLowerCase(Locale.ROOT);
        DataType type = field.dataType();
        if (name.equals("lat") || name.contains("latitude") || name.endsWith("_lat")) return "GEO_LATITUDE";
        if (name.equals("lon") || name.equals("lng") || name.contains("longitude")
                || name.endsWith("_lon") || name.endsWith("_lng")) return "GEO_LONGITUDE";
        if (name.equals("id") || name.endsWith("_id") || name.contains("index") || name.endsWith("_key")) return "TECHNICAL_ID";
        if (DataTypes.DateType.equals(type) || DataTypes.TimestampType.equals(type)
                || name.contains("date") || name.contains("time") || name.endsWith("_at")) return "DATE_TIME";
        if (isNumeric(type)) return "MEASURE";
        if (DataTypes.BooleanType.equals(type)) return "CATEGORY";
        if (DataTypes.StringType.equals(type)) return "CATEGORY";
        return "TEXT";
    }

    private static String suggestedUsage(String role) {
        return switch (role) {
            case "GEO_LATITUDE", "GEO_LONGITUDE" -> "Map readiness and geographic analysis";
            case "TECHNICAL_ID" -> "Record keys, joins, and drill-back; avoid numeric aggregation";
            case "DATE_TIME" -> "Time summaries, rolling analysis, cohorts, churn, and drift";
            case "MEASURE" -> "Statistics, ranking, correlation, regression, KPI, and market models";
            case "CATEGORY" -> "Grouping, pivot, funnel, segmentation, and chart axes";
            default -> "Profiling, search, and descriptive reporting";
        };
    }

    private static boolean isNumeric(DataType type) {
        return DataTypes.ByteType.equals(type)
                || DataTypes.ShortType.equals(type)
                || DataTypes.IntegerType.equals(type)
                || DataTypes.LongType.equals(type)
                || DataTypes.FloatType.equals(type)
                || DataTypes.DoubleType.equals(type)
                || type.typeName().startsWith("decimal");
    }
}
