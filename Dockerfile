FROM openjdk:8-jdk-slim

# Set environment variables for Spark
ENV SPARK_VERSION=3.3.0
ENV HADOOP_VERSION=3

# Install dependencies including Python
RUN apt-get update && apt-get install -y curl python3 python3-pip && \
    curl -O https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Download Open Search connector for Spark:
ENV ELASTIC_SEARCH_SPARK_VERSION=30_2.12
ENV ELASTIC_SEARCH_CONNECTOR_VERSION=8.15.1
RUN curl -O https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-${ELASTIC_SEARCH_SPARK_VERSION}/8.15.1/elasticsearch-spark-${ELASTIC_SEARCH_SPARK_VERSION}-${ELASTIC_SEARCH_CONNECTOR_VERSION}.jar
RUN mkdir /opt/spark-app
RUN mv ./elasticsearch-spark-${ELASTIC_SEARCH_SPARK_VERSION}-${ELASTIC_SEARCH_CONNECTOR_VERSION}.jar /opt/spark-app/elasticsearch-hadoop.jar

# Copy the Spark application to the container
COPY ./etl/tonies_etl.py /opt/spark-app/

WORKDIR /opt/spark

# Set the entrypoint to run Spark
ENTRYPOINT ["./bin/spark-submit", "--jars", "/opt/spark-app/elasticsearch-hadoop.jar", "/opt/spark-app/tonies_etl.py"]
