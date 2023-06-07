from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession

# Spark Context
conf = SparkConf()
conf.setMaster('spark://spark-master:7077') # spark-master
conf.setAppName('spark-base-conf')
sc = SparkContext(conf=conf)

spark = SparkSession \
.builder \
.appName("kafka-to-spark") \
.config("spark.some.config.option", "some-value") \
.getOrCreate()

# sc.addFile("/spark/bart.py")
# import bart

sc.addFile("/diffusion.py")
import diffusion

# get from kefka (broker : kafka1)
# topic -> user-diary
df_raw = spark \
    .readStream \
    .format('kafka') \
    .option('kafka.bootstrap.servers', 'kafka1:19091') \
    .option("startingOffsets", "earliest") \
    .option('subscribe', 'inference_prompt') \
    .load()

query = df_raw \
    .writeStream \
    .queryName("kafka_spark_console")\
    .format("console") \
    .option("truncate", "false") \
    .start()

# query.awaitTermination()

df_spark = df_raw.selectExpr('CAST(value AS STRING) as value')

print(df_spark)

schema = StructType([ \
StructField("diary_id", StringType(),True), \
StructField("prompt", StringType(),True)
])

df2 = df_spark.select(from_json("value",schema).alias("data")).select("data.*")

gen_img_udf = udf(lambda x: diffusion.generate_one(x), StringType())

df3 = df2 \
.withColumn("url", gen_img_udf(col('prompt'))).alias('url')

df3 \
.selectExpr("CAST('data' AS STRING) AS key", "to_json(struct(*)) AS value") \
.writeStream    \
.format('kafka') \
.option('kafka.bootstrap.servers', 'kafka1:19091') \
.option('topic', 'output') \
.option("truncate", False).option("checkpointLocation", "/tmp/dtn/checkpoint") \
.start().awaitTermination()
