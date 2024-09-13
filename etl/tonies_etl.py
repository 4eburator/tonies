from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number, unix_timestamp, to_timestamp, when
from pyspark.sql.window import Window


spark = SparkSession.builder \
    .appName('Tonies ETL') \
    .config('spark.es.nodes', 'tonies-opensearch-storage') \
    .config('spark.es.port', '9200') \
    .config('spark.es.nodes.wan.only', 'true') \
    .getOrCreate()


# Read events from OpenSearch
df_events = spark.read \
    .format("org.elasticsearch.spark.sql") \
    .option("es.resource", "toniebox-events") \
    .load()

# Ensure the timestamp field is in the correct format
df_events = df_events.withColumn(
    "timestamp",
    to_timestamp(col("timestamp"))
)

# Define start and stop event IDs
start_event_ids = [12, 100, 131, 534]
stop_event_ids = [33, 887]

# Filter start and stop events
df_start_events = df_events.filter(col("event_id").isin(start_event_ids))
df_stop_events = df_events.filter(col("event_id").isin(stop_event_ids))

# Assign row numbers to start and stop events for pairing
window_spec = Window.partitionBy("mac", "tonie_id").orderBy("timestamp")

df_start_events = df_start_events.withColumn(
    "event_rank",
    row_number().over(window_spec)
)
df_stop_events = df_stop_events.withColumn(
    "event_rank",
    row_number().over(window_spec)
)

# Alias dataframes for clarity in join
df_start_events = df_start_events.alias("start")
df_stop_events = df_stop_events.alias("stop")

# Join start and stop events
df_playbacks = df_start_events.join(
    df_stop_events,
    on=[
        col("start.mac") == col("stop.mac"),
        col("start.tonie_id") == col("stop.tonie_id"),
        col("start.event_rank") == col("stop.event_rank")
    ],
    how='inner'
)

# Calculate playback duration in seconds
df_playbacks = df_playbacks.withColumn(
    "playback_duration",
    (col("stop.timestamp").cast("long") - col("start.timestamp").cast("long"))
)

# Filter out negative or zero durations
df_playbacks = df_playbacks.filter(col("playback_duration") > 0)

# Select and rename columns for the final dataset
df_playbacks = df_playbacks.select(
    col("start.mac").alias("mac"),
    col("start.tonie_id").alias("tonie_id"),
    col("start.timestamp").alias("playback_start"),
    col("stop.timestamp").alias("playback_end"),
    col("playback_duration")
)

# Write the output to OpenSearch
df_playbacks.write \
    .format("org.elasticsearch.spark.sql") \
    .option("es.resource", "toniebox-playbacks") \
    .mode("overwrite") \
    .save()



df_playbacks.write.csv("/opt/spark-apps/playbacks_output.csv", header=True)


# Stop the Spark session
spark.stop()

