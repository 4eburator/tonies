#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status

# Download the Elasticsearch-Hadoop connector JAR
echo "Downloading Elasticsearch-Hadoop connector JAR..."
# curl -L -o /opt/spark-apps/elasticsearch-hadoop.zip https://artifacts.elastic.co/downloads/elasticsearch-hadoop/elasticsearch-hadoop-7.17.1.zip
# curl -L -o h/opt/spark-apps/elasticsearch-hadoop.zip  https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/7.17.1/elasticsearch-spark-30_2.12-7.17.1.jar

# wget -q https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/7.17.1/elasticsearch-spark-30_2.12-7.17.1.jar -O /opt/spark-apps/elasticsearch-hadoop.jar

# wget -q https://repo1.maven.org/maven2/org/opensearch/client/opensearch-spark-30_2.12/1.2.0/opensearch-spark-30_2.12-1.2.0.jar -O /opt/spark-apps/elasticsearch-hadoop.jar

# wget -q https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.13/8.15.1/elasticsearch-spark-30_2.13-8.15.1.jar -O /opt/spark-apps/elasticsearch-hadoop.jar


wget -q https://repo1.maven.org/maven2/org/elasticsearch/elasticsearch-spark-30_2.12/8.15.1/elasticsearch-spark-30_2.12-8.15.1.jar -O /opt/spark-apps/elasticsearch-hadoop.jar



# https://repo1.maven.org/maven2/org/opensearch/client/opensearch-spark-30_2.12/1.2.0/opensearch-spark-30_2.12-1.2.0.jar

# wget -q https://artifacts.elastic.co/downloads/elasticsearch-hadoop/elasticsearch-hadoop-7.17.1.zip -O /opt/spark-apps/elasticsearch-hadoop.zip

if [ $? -ne 0 ]; then
  echo "Failed to download Elasticsearch-Hadoop connector JAR"
  exit 1
fi

# Extract the JAR file from the ZIP archive

#rm -rf /opt/spark-apps/elasticsearch-hadoop-7.17.1/
#unzip -q /opt/spark-apps/elasticsearch-hadoop.zip -d /opt/spark-apps/

# Identify the correct JAR file based on your Spark and Scala versions
# For Spark 3.x and Scala 2.12, the JAR file is:
# mv /opt/spark-apps/dist/elasticsearch-spark-30_2.12-7.17.1.jar /opt/spark-apps/elasticsearch-hadoop.jar
# mv -f /opt/spark-apps/elasticsearch-hadoop-7.17.1/dist/elasticsearch-spark-20_2.11-7.17.1.jar /opt/spark-apps/elasticsearch-hadoop.jar

echo "JAR connector download is completed"

# Run the ETL script with spark-submit
echo "Starting Tonies ETL job..."
# /opt/bitnami/spark/bin/spark-submit \
#   --jars /opt/spark-apps/elasticsearch-hadoop.jar \
#  /opt/spark-apps/tonies_etl.py


/opt/bitnami/spark/bin/spark-submit \
  /opt/spark-apps/tonies_etl.py


echo "ETL job finished."

