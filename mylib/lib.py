"""
Library functions for ETL and queries
"""

import os
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col

from pyspark.sql.types import StructType, StructField, IntegerType, StringType

LOG_FILE = "pyspark_output.md"


def log_output(operation, output, query=None):
    """Generates a markdown file for output"""
    with open(LOG_FILE, "a") as file:
        file.write(f"The operation is {operation}\n\n")
        if query:
            file.write(f"The query is {query}\n\n")
        file.write("The truncated output is: \n\n")
        file.write(output)
        file.write("\n\n")


def start_spark(appName):
    spark = SparkSession.builder.appName(appName).getOrCreate()
    return spark


def end_spark(spark):
    spark.stop()
    return "stopped spark session"


def extract(
    url="https://raw.githubusercontent.com/lilah-duboff/data-for-URLS/refs/heads/main/table_1_remote_work_mental_health_data.csv",
    file_path="data/table_1_remote_work_mental_health_data.csv",
    directory="data",
):
    """Extracts a url to a file path"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    with requests.get(url) as r:
        with open(file_path, "wb") as f:
            f.write(r.content)

    return file_path


def load_data(
    spark,
    data="data/table_1_remote_work_mental_health_data.csv",
    name="remote_health_1",
):
    """Loads data into file"""
    # data preprocessing by setting schema
    schema = StructType(
        [
            StructField("Employee_ID", StringType(), True),
            StructField("Age", IntegerType(), True),
            StructField("Gender", StringType(), True),
            StructField("Job_Role", StringType(), True),
            StructField("Industry", StringType(), True),
            StructField("Years_of_Experience", IntegerType(), True),
            StructField("Work_Location", StringType(), True),
            StructField("Hours_Worked_Per_Week", IntegerType(), True),
            StructField("Number_of_Virtual_Meetings", IntegerType(), True),
            StructField("Work_Life_Balance_Rating", IntegerType(), True),
        ]
    )

    df = spark.read.option("header", "false").schema(schema).csv(data)

    log_output("Loading data", df.limit(10).toPandas().to_markdown())

    return df


def query(spark, df, query, name):
    """Queries using spark, puts into md file"""
    df = df.createOrReplaceTempView(name)

    log_output("query data", spark.sql(query).toPandas().to_markdown(), query)

    return spark.sql(query).show()


def describe(df):
    """Generates summary statistics to md file"""
    summary_stats_str = df.describe().toPandas().to_markdown()
    log_output("Describing data", summary_stats_str)

    return df.describe().show()


def transform(df):
    """Transformation on the data"""
    conditions = [
        (col("Industry") == "IT") | (col("Industry") == "Healthcare"),
        (col("Industry") == "Consulting") | (col("Industry") == "Finance"),
        (col("Industry") == "Education") | (col("Industry") == "Retail"),
        (col("Industry") == "Manufacturing") | (col("Industry") == "Industry"),
    ]

    categories = ["IT", "Healthcare", "Consulting"]

    df = df.withColumn(
        "Top Industries",
        when(conditions[0], categories[0])
        .when(conditions[1], categories[1])
        .otherwise("Other"),
    )

    log_output("Transforming data", df.limit(10).toPandas().to_markdown())

    return df.show()
