package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.expressions.Window;
import org.apache.spark.sql.types.DataType;
import org.apache.spark.sql.types.DataTypes;
import org.apache.spark.sql.types.StructField;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.lit;
import static org.apache.spark.sql.functions.trim;
import static org.apache.spark.sql.functions.when;

public final class MapFunctions {
    private MapFunctions() {
    }

    public static MapReadinessResult readiness(
            Dataset<Row> input,
            String latitudeField,
            String longitudeField,
            String nameField) {
        SparkFunctionSupport.requireFields(input, latitudeField, longitudeField, nameField);
        Column latitude = col(latitudeField).cast("double");
        Column longitude = col(longitudeField).cast("double");
        Column missing = col(latitudeField).isNull()
                .or(col(longitudeField).isNull())
                .or(latitude.isNull())
                .or(longitude.isNull());
        Column outOfRange = latitude.lt(-90).or(latitude.gt(90))
                .or(longitude.lt(-180)).or(longitude.gt(180));
        Column duplicateCount = count(lit(1)).over(Window.partitionBy(latitude, longitude));
        Column missingName = nameField == null || nameField.isBlank()
                ? lit(false)
                : col(nameField).isNull().or(trim(col(nameField).cast("string")).equalTo(""));
        Dataset<Row> classified = input
                .withColumn("_dataai_latitude", latitude)
                .withColumn("_dataai_longitude", longitude)
                .withColumn("_dataai_coordinate_occurrences", duplicateCount)
                .withColumn(
                        "_dataai_map_status",
                        when(missing, "MISSING_COORDINATE")
                                .when(outOfRange, "OUT_OF_RANGE")
                                .when(duplicateCount.gt(1), "DUPLICATE_LOCATION")
                                .when(missingName, "VALID_COORDINATE_MISSING_NAME")
                                .otherwise("KML_READY"));
        Dataset<Row> summary = classified.groupBy("_dataai_map_status")
                .agg(count(lit(1)).alias("affected_records"))
                .withColumnRenamed("_dataai_map_status", "check")
                .orderBy("check");
        Dataset<Row> valid = classified.filter(col("_dataai_map_status").isin(
                "KML_READY", "VALID_COORDINATE_MISSING_NAME", "DUPLICATE_LOCATION"));
        Dataset<Row> invalid = classified.filter(col("_dataai_map_status").isin(
                "MISSING_COORDINATE", "OUT_OF_RANGE"));
        return new MapReadinessResult(
                classified,
                summary,
                valid,
                invalid,
                suggestLatitudeFields(input),
                suggestLongitudeFields(input));
    }

    public static List<String> suggestLatitudeFields(Dataset<Row> input) {
        return coordinateCandidates(input, true);
    }

    public static List<String> suggestLongitudeFields(Dataset<Row> input) {
        return coordinateCandidates(input, false);
    }

    private static List<String> coordinateCandidates(Dataset<Row> input, boolean latitude) {
        List<String> candidates = new ArrayList<>();
        for (StructField field : input.schema().fields()) {
            String name = field.name().toLowerCase(Locale.ROOT);
            if (looksTechnicalId(name) || !isNumericOrString(field.dataType())) {
                continue;
            }
            boolean match = latitude
                    ? name.equals("lat") || name.contains("latitude") || name.endsWith("_lat")
                    : name.equals("lon") || name.equals("lng") || name.contains("longitude")
                            || name.endsWith("_lon") || name.endsWith("_lng");
            if (match) {
                candidates.add(field.name());
            }
        }
        return List.copyOf(candidates);
    }

    private static boolean isNumericOrString(DataType type) {
        return DataTypes.StringType.equals(type)
                || DataTypes.ByteType.equals(type)
                || DataTypes.ShortType.equals(type)
                || DataTypes.IntegerType.equals(type)
                || DataTypes.LongType.equals(type)
                || DataTypes.FloatType.equals(type)
                || DataTypes.DoubleType.equals(type)
                || type.typeName().startsWith("decimal");
    }

    private static boolean looksTechnicalId(String name) {
        return name.equals("id") || name.endsWith("_id") || name.contains("index") || name.contains("key");
    }
}
