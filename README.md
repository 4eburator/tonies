# Toniebox Data Pipeline Design Document

## Architecture

The data pipeline architecture consists of the following components:

1. **Open Search Cluster as DWH:** This serves as the data warehouse (DWH) where raw event data is ingested and stored. 
   It provides the necessary storage and search capabilities for large datasets.

2. **Ingest Raw Data Process:** Data is ingested into Open Search in the Elasticsearch Bulk API format or 
   Newline delimited JSON (NDJSON), which allows efficient batch data ingestion.

3. **Apache Spark:** Used as the ETL (Extract, Transform, Load) framework, running locally within Docker containers. 
   Spark processes and transforms the raw data, extracting meaningful insights.

4. **Docker Compose:** Acts as the build and orchestration tool. It manages the lifecycle of all the services involved 
   in the pipeline, including Open Search, Spark, and auxiliary services.

5. **Open Search Dashboards:** A visualization tool (BI tool) used to explore and monitor the data stored in Open Search. 
   It provides an interface for interactive querying and visualization.

## Data Flow

1. **Data Ingestion:** 
   - Raw data is formatted as NDJSON, compatible with Open Search, and ingested into the raw layer of the data 
     warehouse through Open Search REST API calls.

2. **Data Exploration and Monitoring:** 
   - Open Search Dashboards provides a user interface for exploring and monitoring the ingested raw data. Analysts 
     can create indices and query data interactively.

3. **Data Transformation:**
   - The raw events are processed by a Spark job that performs filtering, cleaning, and aggregation of the data.
   - The transformed data is saved back into the data warehouse.

## Low-Level Design

The implementation includes the following components and files:

### 1. **Docker Compose Configuration**
   - `docker-compose.yml`: Entry point defining the build and run workflow. It references the following services:
     - **tonies-opensearch-storage**: Uses the `opensearchproject/opensearch:latest` image to represent the data 
       warehouse.
     - **tonies-dashboards**: Uses the `opensearchproject/opensearch-dashboards:latest` image for the Open Search UI 
       as the BI console.
     - **tonies-data-loader**: Uses the `opensearchproject/opensearch:latest` image to load raw data into the data 
       warehouse.
     - **tonies-spark-master**: A custom Docker image (`custom-spark-master:3.3.0`) built from 
       `Dockerfile.spark_master`. Represents the Spark master with health check support.
     - **tonies-spark-worker**: Uses the `bitnami/spark:3.3.0` image as an Apache Spark worker node.
     - **tonies-spark-etl**: A custom image built from `Dockerfile`, which installs the Open Search connector jar and 
       submits Spark transformations.

### 2. **Custom Dockerfiles**
   - `Dockerfile`: Defines the custom Spark ETL environment, installing necessary dependencies and the Open Search 
      connector.
   - `Dockerfile.spark_master`: Builds the Spark master image with additional health checks and `curl` support.

### 3. **ETL Job and Supporting Files**
   - `etl/tonies_etl.py`: The PySpark ETL job that reads, transforms, and loads data using Apache Spark.
   - `data/load_raw_data.sh`: A shell script executed by `tonies-data-loader` to ingest raw data.
   - `data/test_data1.json`: Contains raw test data for ingestion and testing.

### 4. **README.md**
   - Documentation for the pipeline, providing build instructions, usage, and commands to run the pipeline.

## Implementation Details

### **Build Instructions**
- To build the custom Spark master image:
  ```bash
  docker build -t custom-spark-master:3.3.0 -f Dockerfile.spark_master .
  ```
- To build all Docker images defined in `docker-compose.yml` without using the cache:
  ```bash
  docker compose build --no-cache
  ```

### **Pipeline Run Instructions**
- Start the entire pipeline:
  ```bash
  docker compose up
  ```

## Questions and Answers

### What is the purpose of this data pipeline?
- The purpose of this data pipeline is to ingest interaction events from Tonieboxes into a data warehouse, transform 
  the data to extract relevant playback information, and make it available for analytics and machine learning. The 
  primary metric to be derived is the average weekly playtime per user.

### What data sources will be ingested?
- The data source is an Open Search cluster containing Newline delimited JSON (NDJSON) logs of interaction events 
  from Tonieboxes. These events include playback start and stop interactions, logged in NDJSON format.

### Which tools and technologies will be used for ingestion?
- **Open Search:** Used for storing and querying the raw event data.
- **Elasticsearch Bulk API / NDJSON:** Used for efficient data ingestion into Open Search.
- **Apache Spark:** Used for processing and transforming the ingested data.
- **Docker Compose:** Used to orchestrate the entire pipeline, including Open Search, Spark, and related services.

### How will the data be ingested?
- Data will be ingested in NDJSON format into the Open Search cluster using REST API calls. The `tonies-data-loader` 
  service will execute the `load_raw_data.sh` script to perform the ingestion.

### What transformations will be applied?
- **Filtering:** Identify and filter out events relevant to playback sessions (start and stop events).
- **Pairing Events:** Match start and stop events to form complete playback sessions.
- **Calculating Duration:** Compute the duration of each playback session in seconds.
- **Data Cleaning:** Remove duplicates, null values, and events with unreasonable timestamps.
- **Aggregation:** Aggregate playback sessions for further analysis.

### Which data quality checks will be implemented?
- **Schema Validation:** Ensure that the data contains all expected fields (`mac`, `timestamp`, `tonie_id`, `event_id`).
- **Null Checks:** Verify that no critical fields contain null values.
- **Duplicate Removal:** Eliminate duplicate events based on `mac`, `tonie_id`, `timestamp`, and `event_id`.
- **Timestamp Validation:** Ensure that the timestamps are within a reasonable range (e.g., within the last year).
- **Playback Duration Validation:** Ensure that playback durations are positive and below a specified threshold 
  (e.g., 8 hours).

### How will the data pipeline be scheduled?
- While this implementation runs locally using Docker Compose, it can be extended to run on a scheduled basis using 
  tools like Apache Airflow, cron jobs, or Spark's built-in scheduling capabilities.

### How will the data pipeline be monitored?
- **Open Search Dashboards:** Used to monitor the ingestion process and explore raw and processed data.
- **Spark Logs:** Set the Spark log level to 'INFO' to track job execution and monitor ETL transformations.

### Which alerting mechanisms will be put in place?
- **Health Checks:** Health checks for services (`tonies-spark-master` and `tonies-opensearch-storage`) are included 
  in the Docker Compose configuration to monitor the status of key components.
- **Error Logging:** The ETL script logs errors during processing, which can be extended to trigger alerts or 
  notifications (e.g., via email or messaging services).

### How will the data pipeline scale?
- **Scalability with Spark:** Apache Spark can handle large-scale data processing by distributing the workload across 
  multiple worker nodes. Additional worker nodes can be added to the Docker Compose setup to increase processing 
  capacity.
- **Scalable Storage:** Open Search can scale horizontally to manage large volumes of indexed data by adding more 
  nodes to the cluster.

### What are potential risks and challenges?
- **Data Completeness:** Ensuring all relevant events are captured and properly paired can be challenging, especially 
  if events are missing or arrive out of order.
- **Resource Limitations:** Running Spark locally within Docker may have resource limitations; scaling might require 
  moving to a cloud-based setup.
- **Time Zone Handling:** Accurate time zone conversion is crucial to ensure consistency when calculating playbacks 
  across different regions.
- **Error Handling:** Robust error handling is needed to manage data discrepancies, such as missing stop events, 
  which can lead to incomplete playback sessions.

