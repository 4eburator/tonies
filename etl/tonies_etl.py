from pyspark.sql import SparkSession
from pyspark.sql.functions import (col, row_number, unix_timestamp, to_timestamp, when, isnull, current_timestamp,
                                   datediff)
from pyspark.sql.window import Window


spark = SparkSession.builder \
    .appName('Tonies ETL') \
    .config('spark.es.nodes', 'tonies-opensearch-storage') \
    .config('spark.es.port', '9200') \
    .config('spark.es.nodes.wan.only', 'true') \
    .getOrCreate()


spark.sparkContext.setLogLevel('INFO')

try:
    # Read raw events from Open Search
    df_events = spark.read \
        .format('org.elasticsearch.spark.sql') \
        .option('es.resource', 'toniebox-events') \
        .load()

    # Raw events Schema Validation
    raw_expected_columns = {'mac', 'timestamp', 'tonie_id', 'event_id'}
    actual_columns = set(df_events.columns)
    if not raw_expected_columns.issubset(actual_columns):
        raise ValueError(f"Missing columns in input data. Expected columns: {raw_expected_columns}")

    # Ensure the timestamp field is in the correct format
    df_events = df_events.withColumn('timestamp', to_timestamp(col('timestamp')))

    # Data Quality Check 1: Null Checks
    null_check_cols = ['mac', 'timestamp', 'tonie_id', 'event_id']
    for col_name in null_check_cols:
        null_count = df_events.filter(isnull(col(col_name))).count()
        if null_count > 0:
            raise ValueError(f'Column {col_name} contains {null_count} null values.')

    # Data Quality Check 2: Remove Duplicates
    df_events_deduplicated = df_events.dropDuplicates(['mac', 'tonie_id', 'timestamp', 'event_id'])

    # Data Quality Check 3: Validate Timestamp Range
    # Assuming events should be within the last year
    df_events_creansed = df_events_deduplicated.filter(datediff(current_timestamp(), col('timestamp')) <= 365)

    # Define start and stop event IDs
    start_event_ids = [12, 100, 131, 534]
    stop_event_ids = [33, 887]

    # Filter start and stop events
    df_start_events = df_events_creansed.filter(col('event_id').isin(start_event_ids))
    df_stop_events = df_events_creansed.filter(col('event_id').isin(stop_event_ids))

    # Assign row numbers to start and stop events (of particular Toniebox and Tonie figurine) for pairing.
    # The window defines groupping by 'mac' and 'tonie_id' and orders by 'timestamp'
    window_spec = Window.partitionBy('mac', 'tonie_id').orderBy('timestamp')

    df_start_events = df_start_events.withColumn('event_rank', row_number().over(window_spec)).alias('start')
    df_stop_events = df_stop_events.withColumn('event_rank', row_number().over(window_spec)).alias('stop')

    # Join start and stop events, so the dataframe contains the completed sessions only
    df_session_completed = df_start_events.join(
        df_stop_events,
        on=[
            col('start.mac') == col('stop.mac'),
            col('start.tonie_id') == col('stop.tonie_id'),
            col('start.event_rank') == col('stop.event_rank')
        ],
        how='inner'
    )

    # Calculate playback duration in seconds:
    df_playbacks_duration = df_session_completed.withColumn(
        'playback_duration',
        (col('stop.timestamp').cast('long') - col('start.timestamp').cast('long'))
    )

    # Data Quality Check 4: Validate Playback Duration with threshold of 8h
    max_duration_threshold = 3600 * 8  # 8 hours
    df_playbacks_duration_validated = df_playbacks_duration \
        .filter((col('playback_duration') > 0) & (col('playback_duration') < max_duration_threshold))

    # Select and rename columns for the final dataset
    df_playbacks = df_playbacks_duration_validated.select(
        col('start.mac').alias('mac'),
        col('start.tonie_id').alias('tonie_id'),
        col('start.timestamp').alias('playback_start'),
        col('stop.timestamp').alias('playback_end'),
        col('playback_duration')
    )

    # Write the output to OpenSearch
    df_playbacks.write \
        .format('org.elasticsearch.spark.sql') \
        .option('es.resource', 'toniebox-playbacks') \
        .mode('overwrite') \
        .save()

    df_playbacks.write.csv('/opt/spark-apps/playbacks_output.csv', header=True)

except Exception as e:
    print(f'An error occurred: {e}')
finally:
    spark.stop()
