from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SparkSession

# Spark Context
conf = SparkConf()
conf.setMaster('spark://spark-master:7077')
conf.setAppName('spark-base-conf')
sc = SparkContext(conf=conf)

spark = SparkSession \
.builder \
.appName("kafka-to-spark") \
.config("spark.some.config.option", "some-value") \
.getOrCreate()

sc.addFile("/spark/bart.py")
import bart

sc.addFile("/spark/prompt_diffusion.py")
import prompt_diffusion

# get from kefka
# topic -> user-diary
df_raw = spark \
.readStream \
.format('kafka') \
.option('kafka.bootstrap.servers', 'kafka:9091') \
.option("startingOffsets", "earliest") \
.option('subscribe', 'user-diary') \
.load()

df_spark_init = df_raw.selectExpr('CAST(value AS STRING) as value')

schema = StructType([ \
StructField("user_id",StringType(),True), \
StructField("content", TimestampType(),True)
])

summarize_udf = udf(lambda x: bart.summarize(x), StringType())
prompt_udf = udf(lambda x: prompt_diffusion.generate_prompt(x), StringType())
gen_img_udf = udf(lambda x: prompt_diffusion.generate_img(x), StringType())

df_spark = df_spark_init.select(from_json("value",schema).alias("data")).select("data.*")
df_spark_updated = df_spark \
.withColumn("summaize", summarize_udf(col("content"))) \
.withColumn("prompt", prompt_udf(col("content"))) \
.withColumn("img", gen_img_udf(col("content"))).alias("data")

# send to kafka
df_spark_updated \
.selectExpr("CAST('data' AS STRING) AS key", "to_json(struct(*)) AS value") \
.writeStream    \
.format('kafka') \
.option('kafka.bootstrap.servers', 'kafka:9091') \
.option('topic', 'user-diary-prompt') \
.option("truncate", False).option("checkpointLocation", "/tmp/dtn/checkpoint") \
.start().awaitTermination()
