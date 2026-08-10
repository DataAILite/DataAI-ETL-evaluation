package com.dataai.etl.spark.iris;

import org.apache.spark.sql.DataFrameReader;
import org.apache.spark.sql.DataFrameWriter;
import org.apache.spark.sql.Row;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Connection options applied to Spark's standard JDBC reader and writer. */
public final class IrisJdbcOptions {
    public static final String DEFAULT_DRIVER = "com.intersystems.jdbc.IRISDriver";

    private static final Set<String> RESERVED_PROPERTIES = Set.of(
            "url", "driver", "user", "password", "dbtable", "query");

    private final String url;
    private final String driver;
    private final String user;
    private final String password;
    private final Integer fetchSize;
    private final Integer batchSize;
    private final Map<String, String> properties;

    private IrisJdbcOptions(Builder builder) {
        url = requireText(builder.url, "url");
        if (!url.regionMatches(true, 0, "jdbc:IRIS://", 0, "jdbc:IRIS://".length())) {
            throw new IllegalArgumentException("IRIS JDBC URL must start with jdbc:IRIS://.");
        }
        driver = requireText(builder.driver, "driver");
        user = builder.user;
        password = builder.password;
        if ((user == null) != (password == null)) {
            throw new IllegalArgumentException("IRIS user and password must be supplied together.");
        }
        fetchSize = positive(builder.fetchSize, "fetchSize");
        batchSize = positive(builder.batchSize, "batchSize");
        properties = Map.copyOf(builder.properties);
    }

    public static Builder builder(String url) {
        return new Builder(url);
    }

    public static Builder forServer(String host, int port, String namespace) {
        String safeHost = requireText(host, "host");
        String safeNamespace = requireText(namespace, "namespace");
        if (safeHost.contains("/") || safeHost.contains("\\")) {
            throw new IllegalArgumentException("IRIS host cannot contain a path separator.");
        }
        if (port < 1 || port > 65535) {
            throw new IllegalArgumentException("IRIS port must be between 1 and 65535.");
        }
        if (safeNamespace.contains("/") || safeNamespace.contains("\\")
                || safeNamespace.chars().anyMatch(Character::isWhitespace)) {
            throw new IllegalArgumentException("IRIS namespace cannot contain whitespace or a path separator.");
        }
        return builder("jdbc:IRIS://" + safeHost + ":" + port + "/" + safeNamespace);
    }

    public String url() {
        return url;
    }

    public String driver() {
        return driver;
    }

    DataFrameReader apply(DataFrameReader reader) {
        Objects.requireNonNull(reader, "reader");
        DataFrameReader configured = reader
                .format("jdbc")
                .option("url", url)
                .option("driver", driver);
        if (user != null) {
            configured = configured.option("user", user).option("password", password);
        }
        if (fetchSize != null) {
            configured = configured.option("fetchsize", fetchSize);
        }
        for (Map.Entry<String, String> property : properties.entrySet()) {
            configured = configured.option(property.getKey(), property.getValue());
        }
        return configured;
    }

    DataFrameWriter<Row> apply(DataFrameWriter<Row> writer) {
        Objects.requireNonNull(writer, "writer");
        DataFrameWriter<Row> configured = writer
                .format("jdbc")
                .option("url", url)
                .option("driver", driver);
        if (user != null) {
            configured = configured.option("user", user).option("password", password);
        }
        if (batchSize != null) {
            configured = configured.option("batchsize", batchSize);
        }
        for (Map.Entry<String, String> property : properties.entrySet()) {
            configured = configured.option(property.getKey(), property.getValue());
        }
        return configured;
    }

    @Override
    public String toString() {
        return "IrisJdbcOptions[url=" + url + ", driver=" + driver
                + ", credentialsConfigured=" + (user != null)
                + ", fetchSize=" + fetchSize
                + ", batchSize=" + batchSize
                + ", propertyNames=" + properties.keySet() + "]";
    }

    public static final class Builder {
        private final String url;
        private String driver = DEFAULT_DRIVER;
        private String user;
        private String password;
        private Integer fetchSize;
        private Integer batchSize;
        private final Map<String, String> properties = new LinkedHashMap<>();

        private Builder(String url) {
            this.url = url;
        }

        public Builder driver(String value) {
            driver = value;
            return this;
        }

        public Builder credentials(String valueUser, String valuePassword) {
            user = requireText(valueUser, "user");
            password = requireText(valuePassword, "password");
            return this;
        }

        public Builder fetchSize(int value) {
            fetchSize = value;
            return this;
        }

        public Builder batchSize(int value) {
            batchSize = value;
            return this;
        }

        /** Adds a non-reserved JDBC option such as SSL configuration. */
        public Builder property(String name, String value) {
            String safeName = requireText(name, "property name");
            if (RESERVED_PROPERTIES.contains(safeName.toLowerCase())) {
                throw new IllegalArgumentException("Use the typed option for reserved property: " + safeName);
            }
            properties.put(safeName, requireText(value, "property value"));
            return this;
        }

        public IrisJdbcOptions build() {
            return new IrisJdbcOptions(this);
        }
    }

    private static Integer positive(Integer value, String name) {
        if (value != null && value < 1) {
            throw new IllegalArgumentException(name + " must be at least one.");
        }
        return value;
    }

    private static String requireText(String value, String name) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(name + " cannot be blank.");
        }
        return value;
    }
}
