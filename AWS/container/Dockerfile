# Build only with a qualified Amazon EMR Serverless Spark base image.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
LABEL org.opencontainers.image.title="DataAI ETL Spark Libraries"
LABEL org.opencontainers.image.vendor="Yanbor LLC"
LABEL org.opencontainers.image.version="0.1.0-SNAPSHOT"
USER root
COPY lib/*.jar /opt/dataai/lib/
RUN mkdir -p /usr/lib/spark/jars && cp /opt/dataai/lib/*.jar /usr/lib/spark/jars/ && chmod -R a=rX /opt/dataai/lib /usr/lib/spark/jars
USER hadoop:hadoop
