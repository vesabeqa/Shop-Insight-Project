from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("ShopInsightTest")
    .getOrCreate()
)

data = [
    ("Product A", 100),
    ("Product B", 200),
    ("Product C", 300)
]

columns = ["product", "sales"]

df = spark.createDataFrame(data, columns)

df.show()

print("Total sales:", df.agg({"sales": "sum"}).collect()[0][0])

spark.stop()