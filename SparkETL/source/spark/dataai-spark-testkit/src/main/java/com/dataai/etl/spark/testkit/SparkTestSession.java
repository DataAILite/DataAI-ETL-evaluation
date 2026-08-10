package com.dataai.etl.spark.testkit;

import org.apache.spark.sql.SparkSession;

public final class SparkTestSession {
    private SparkTestSession() {
    }

    public static SparkSession create() {
        SparkSession session = SparkSession.builder()
                .master("local[2]")
                .appName("dataai-spark-test")
                .config("spark.ui.enabled", "false")
                .config("spark.sql.shuffle.partitions", "2")
                .getOrCreate();
        session.sparkContext().setLogLevel("WARN");
        return session;
    }
}
