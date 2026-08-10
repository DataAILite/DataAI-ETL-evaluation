ARG BASE_IMAGE=eclipse-temurin:17-jre
FROM ${BASE_IMAGE}
LABEL org.opencontainers.image.title="DataAI ETL Spark Libraries"
LABEL org.opencontainers.image.vendor="Yanbor LLC"
LABEL org.opencontainers.image.version="0.1.0-SNAPSHOT"
RUN groupadd --system dataai && useradd --system --gid dataai --home-dir /nonexistent --shell /usr/sbin/nologin dataai
COPY lib/*.jar /opt/dataai/lib/
RUN chmod -R a=rX /opt/dataai/lib
USER dataai:dataai
CMD ["sh", "-c", "find /opt/dataai/lib -maxdepth 1 -type f -name '*.jar' -print"]
