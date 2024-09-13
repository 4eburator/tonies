#!/bin/bash

# Wait for Tonies OpenSearch service is up and running
echo "Waiting for Tonies OpenSearch service to start..."
while ! curl -s http://tonies-opensearch-storage:9200 > /dev/null; do
    sleep 1
done
echo "Tonies OpenSearch is up and running"

# Ingest data using the Bulk API
echo "Ingesting raw data into DWH"
for file in /usr/share/opensearch/data_import/*.json; do
    if [ -f "$file" ]; then
        echo "Ingesting file $file"
        curl -s -H "Content-Type: application/x-ndjson" -XPOST "http://tonies-opensearch-storage:9200/_bulk" --data-binary "@$file"
    fi
done

echo "RAW Data ingestion is completed"
