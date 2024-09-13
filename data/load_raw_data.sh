#!/bin/bash

# Wait for OpenSearch to be available
echo "Waiting for OpenSearch to start..."
while ! curl -s http://opensearch-node1:9200 > /dev/null; do
    sleep 1
done
echo "OpenSearch is up"

# Ingest data using the Bulk API
echo "Ingesting data..."
for file in /usr/share/opensearch/data_import/*.json; do
    if [ -f "$file" ]; then
        echo "Processing $file"
        curl -s -H "Content-Type: application/x-ndjson" -XPOST "http://opensearch-node1:9200/_bulk" --data-binary "@$file"
    fi
done

echo "Data ingestion completed"

