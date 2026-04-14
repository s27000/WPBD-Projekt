import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, DateType

# Spark session
spark = SparkSession.builder \
    .appName("KafkaToMinIO") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.apache.hadoop:hadoop-aws:3.3.4") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

print("[INFO] Rozpoczęto processor Albumów")

# Schema for albumy table
schema = StructType([
    StructField("idAlbumu", IntegerType()),
    StructField("tytul", StringType()),
    StructField("wykonawca", StringType()),
    StructField("gatunek", StringType()),
    StructField("wytwornia", StringType()),
    StructField("dataWydania", StringType()),
    StructField("cena", DoubleType())
])

# Read from Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "dbserver1.public.albumy") \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Parse the value column
parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("album"),
    col("timestamp")
).select("album.*", col("timestamp").alias("kafka_timestamp"))

# Add processing timestamp
enriched_df = parsed_df.withColumn("processed_at", current_timestamp())

# Write to MinIO
query = enriched_df.writeStream \
    .format("parquet") \
    .outputMode("append") \
    .option("path", "s3a://cd-ecommerce/albumy") \
    .option("checkpointLocation", "s3a://cd-ecommerce/.checkpoints/albumy/") \
    .trigger(processingTime="10 seconds") \
    .start()

print("[INFO] Stream Albumów rozpoczęty")

os.makedirs("/spark_flag", exist_ok=True)
with open("/spark_flag/albumy_ready", "w") as f:
    f.write("ready")
print("[INFO] Flaga gotowości Spark joba ustawiona")

query.awaitTermination()
