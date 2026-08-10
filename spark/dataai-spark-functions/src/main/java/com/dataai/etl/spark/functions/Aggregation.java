package com.dataai.etl.spark.functions;

import org.apache.spark.sql.Column;

import static org.apache.spark.sql.functions.avg;
import static org.apache.spark.sql.functions.count;
import static org.apache.spark.sql.functions.countDistinct;
import static org.apache.spark.sql.functions.max;
import static org.apache.spark.sql.functions.min;
import static org.apache.spark.sql.functions.stddev_pop;
import static org.apache.spark.sql.functions.sum;

public enum Aggregation {
    COUNT,
    COUNT_DISTINCT,
    SUM,
    MINIMUM,
    MAXIMUM,
    AVERAGE,
    STANDARD_DEVIATION;

    public Column apply(Column value) {
        return switch (this) {
            case COUNT -> count(value);
            case COUNT_DISTINCT -> countDistinct(value);
            case SUM -> sum(value.cast("double"));
            case MINIMUM -> min(value);
            case MAXIMUM -> max(value);
            case AVERAGE -> avg(value.cast("double"));
            case STANDARD_DEVIATION -> stddev_pop(value.cast("double"));
        };
    }
}
