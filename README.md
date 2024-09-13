# Tonies Data Engineering Case Study

### * Execution flow:

* Load raw test data

    Test data load process is triggered by `docker-compose up` command. 

* Explore raw data in OpenSearch Dashboards

  DWH Dashboards entry point:  http://localhost:5601
  Index creation: Management -> Index Management -> Create index (index name = "toniebox-events*")
  OpenSearch Dashboards -> Discover -> "toniebox-events*" -> Show dates

* Transform loaded data and export target dataset

OpenSearch REST API entry point: 
http://localhost:9200
or curl http://localhost:9200





RAW Data NDJSON format:
OpenSearch Bulk API requires data to be in a specific format called newline-delimited JSON (NDJSON)
when JSON objects separated by newline characters (\n).